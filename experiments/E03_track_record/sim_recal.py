"""Item 1 (post hoc, 15 Nov): recalibrated-crowd baseline and learned cheaters against it.

World generation is identical to sim.make_world (same rng stream), plus a time structure: events are in time order
(index), split into 4 blocks. Claims and scoring use only blocks 1-3. The baseline for a block-b event is the crowd
prior recalibrated by a map fitted ONLY on (crowd prior, outcome) of events in blocks < b (resolved before b starts).
The cheater never sees outcomes of fitted events: it can only claim blocks 1-3 events, it cannot change outcomes, and
the fit uses event outcomes, not claims. Honest sources' claims are rescored against the same baseline.

    modes: none (raw crowd baseline, same eligible events), logit (logistic recalibration of logit c), iso (isotonic)
    bias:  main (calibrated crowd), R2 (slope 0.75 in logit), R2tail (slope 0.6 only beyond |logit| > 2; a
           misspecified-for-logistic bias that attacks the weakest part of a 2-parameter fit)

    uv run python -I experiments/E03_track_record/sim_recal.py --seeds 30
"""
from __future__ import annotations
import argparse, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from sklearn.isotonic import IsotonicRegression
from sklearn.linear_model import LogisticRegression

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim
from sim import (N_TOPICS, TOPIC_MU, BIN_EDGES, N_BINS, sigmoid, logit, e_sigmoid, percentiles, HANDCODED, cem,
                 OUT, RULES, aggregate, claim_terms, pop_stats, D, LO, HI)

CACHE = OUT / "sim_cache_recal"
BIAS = {"main": dict(slope=1.0, tail=None), "R2": dict(slope=0.75, tail=None), "R2tail": dict(slope=1.0, tail=0.6)}
N_BLOCKS = 4
EPSC = 0.01


def crowd_of(ct, b):
    z = logit(ct)
    if b["tail"] is not None:  # slope b['tail'] beyond |z| > 2, identity inside (continuous)
        z = np.sign(z) * np.where(np.abs(z) <= 2, np.abs(z), 2 + b["tail"] * (np.abs(z) - 2))
        return sigmoid(z)
    return sigmoid(b["slope"] * z)


def fit_map(c, y, mode):
    if mode == "none":
        return lambda x: x
    if mode == "logit":
        z = logit(c)[:, None]
        m = LogisticRegression(C=1e6).fit(z, y)  # ~unregularised
        return lambda x: m.predict_proba(logit(x)[:, None])[:, 1]
    iso = IsotonicRegression(out_of_bounds="clip", y_min=EPSC, y_max=1 - EPSC).fit(c, y.astype(float))
    return lambda x: iso.predict(x)


def make_world(rng, bias_name, mode, miscal=0.0, min_n=10, n_events=3000, n_honest=200):
    bias = BIAS[bias_name]
    topic = rng.integers(0, N_TOPICS, n_events)
    a = rng.normal(TOPIC_MU[topic], 1.5)
    sig = rng.uniform(0.25, 2.5, n_events)
    b = rng.normal(0.0, sig)
    y = rng.random(n_events) < sigmoid(a + b)
    crowd_true = e_sigmoid(a, sig)
    c = crowd_of(crowd_true, bias)
    conf_bin = np.searchsorted(BIN_EDGES, np.abs(c - 0.5), side="right")
    k = rng.uniform(0.1, 0.9, n_honest)
    n = np.round(np.exp(rng.uniform(np.log(min_n), np.log(500), n_honest))).astype(int)
    lam = np.ones(n_honest)
    src, ev = [], []
    for j in range(n_honest):
        src.append(np.full(n[j], j))
        ev.append(rng.choice(n_events, n[j], replace=False))
    src, ev = np.concatenate(src), np.concatenate(ev)
    kk = k[src]
    s = b[ev] + rng.normal(0, 1, len(ev)) * sig[ev] * np.sqrt((1 - kk) / kk)
    r = e_sigmoid(a[ev] + kk * s, sig[ev] * np.sqrt(1 - kk))
    # ---- time structure and recalibrated baseline (no rng use below) ----
    blk = np.arange(n_events) * N_BLOCKS // n_events
    cb = np.empty(n_events)
    cb[blk == 0] = c[blk == 0]
    for q in range(1, N_BLOCKS):
        past = blk < q
        f = fit_map(c[past], y[past], mode)
        cb[blk == q] = f(c[blk == q])
    elig = blk >= 1
    new_idx = -np.ones(n_events, int)
    new_idx[elig] = np.arange(elig.sum())
    keep = elig[ev]
    src2, ev2, r2 = src[keep], new_idx[ev[keep]], r[keep]
    cnt = np.bincount(src2, minlength=n_honest)
    ok = cnt >= 2
    remap = -np.ones(n_honest, int)
    remap[ok] = np.arange(ok.sum())
    m = ok[src2]
    src2, ev2, r2 = remap[src2[m]], ev2[m], r2[m]
    nh = int(ok.sum())
    w = {"topic": topic[elig], "c": c[elig], "cb": cb[elig], "y": y[elig], "bin": conf_bin[elig]}
    terms = claim_terms(r2, w["y"][ev2], w["cb"][ev2])
    stats = pop_stats(src2, nh, terms, w["topic"][ev2], N_TOPICS)
    scores = aggregate(src2, nh, terms, w["topic"][ev2], stats)
    w["stats"], w["H"], w["k"] = stats, np.stack([scores[R] for R in RULES]), k[ok]
    w["n_honest"] = nh
    # calibration diagnostic: mean |baseline - truth| over eligible events (truth = crowd_true)
    w["cal_err_raw"] = float(np.abs(c[elig] - crowd_true[elig]).mean())
    w["cal_err_base"] = float(np.abs(cb[elig] - crowd_true[elig]).mean())
    return w


def cheater_scores(theta, w, rng):
    logw = theta[:N_BINS][w["bin"]] + theta[N_BINS:N_BINS + N_TOPICS][w["topic"]]
    n = int(round(10 ** np.clip(theta[-1], LO[-1], HI[-1])))
    g = logw + rng.gumbel(size=len(logw))
    idx = np.argpartition(-g, n - 1)[:n]
    alpha, beta = theta[-3], theta[-2]
    r = sigmoid(alpha * logit(w["c"][idx]) + beta)  # cheater sees the published crowd c, not the secret baseline
    terms = claim_terms(r, w["y"][idx], w["cb"][idx])
    sc = aggregate(np.zeros(n, dtype=int), 1, terms, w["topic"][idx], w["stats"])
    return np.array([sc[R][0] for R in RULES])


sim.cheater_scores = cheater_scores  # cem() looks the function up in sim's namespace


def run_seed(args):
    bias_name, mode, seed = args
    cname = f"{bias_name}_{mode}"
    fn = CACHE / f"{cname}_{seed}.json"
    if fn.exists():
        return json.loads(fn.read_text())
    t0 = time.time()
    # same rng stream as sim.run_seed(R2 / main): worlds are paired with the original conditions
    rng = np.random.default_rng([seed, 1000 + list(sim.CONDS).index("R2" if bias_name != "main" else "main")])
    train = [make_world(rng, bias_name, mode) for _ in range(40)]
    test = [make_world(rng, bias_name, mode) for _ in range(20)]

    def evaluate(theta, reps=1):
        return np.array([percentiles(cheater_scores(theta, w, rng), w["H"]) for w in test for _ in range(reps)])

    res = {"cond": cname, "seed": seed, "rules": RULES, "learned": {}, "handcoded": {},
           "cal_err_raw": float(np.mean([w["cal_err_raw"] for w in test])),
           "cal_err_base": float(np.mean([w["cal_err_base"] for w in test])),
           "n_honest": float(np.mean([w["n_honest"] for w in test]))}
    for name, th in HANDCODED.items():
        th = th.copy(); th[-1] = max(th[-1], 1.0)
        P = evaluate(th, 3)
        res["handcoded"][name] = {"pct_mean": P.mean(0).tolist()}
    for ri, R in enumerate(RULES):
        theta, curve = cem(ri, train, rng, 40, 64, 12, 6, 10)
        P = evaluate(theta, 3)
        res["learned"][R] = {"theta": theta.tolist(), "pct": float(P[:, ri].mean()),
                             "beat_median": float((P[:, ri] > 50).mean())}
    res["seconds"] = time.time() - t0
    CACHE.mkdir(exist_ok=True)
    fn.write_text(json.dumps(res))
    print(f"[recal {cname} seed {seed}] {res['seconds']:.0f}s " + " ".join(f"{R}={res['learned'][R]['pct']:.0f}" for R in RULES), flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--workers", type=int, default=18)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--only", default=None)
    a = ap.parse_args()
    jobs = [(b, m, s) for b in BIAS for m in ("none", "logit", "iso") for s in range(a.seeds)
            if a.only is None or f"{b}_{m}" == a.only]
    if a.smoke:
        CACHE = OUT / "sim_cache_recal_smoke"
        jobs = [("R2", "logit", 0)]
    with Pool(a.workers) as p:
        out = p.map(run_seed, jobs, chunksize=1)
    if not a.smoke:
        (OUT / "sim_recal_all.json").write_text(json.dumps(out))
    print("done", flush=True)
