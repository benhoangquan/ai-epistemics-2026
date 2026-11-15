"""Review round (15 Nov): 6 extra rules, skill/volume recovery and EB diagnostics, with the SAME world generator, rng stream
and CEM protocol as sim.py (rules are appended after the original 13 so the first 13 rules reproduce the original run).

New rules (higher is better for all):
  PEER        mean over peered claims of [log2 r_y - mean_{j in honest peers of the event} log2 r_{j,y}]
  PEER-SUM    the same, summed
  FE-BRIER    -(source effect) of a two-way fixed-effects fit  Brier_{ie} = a_i + g_e + noise  (ALS, honest sources, 25 sweeps,
              normalisation mean honest a_i = 0). A cheater's effect is solved with the honest-fitted event effects g_e held fixed.
  EB-BRIER-PM, EB-IG-PM, EB0-IG-PM  the three EB rules with the Paule-Mandel between-source variance estimator.
Peers: all honest sources that claimed the event; for an honest source's own claim the source itself is excluded (leave-one-out);
claims on events with no peers are dropped (contribute 0 to PEER-SUM, excluded from the PEER mean; a source with no peered claims scores 0).

    uv run python -I experiments/E03_track_record/sim_v3.py --cond main --seeds 30
"""
from __future__ import annotations
import argparse, json, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim
from sim import (N_TOPICS, TOPIC_MU, BIN_EDGES, N_BINS, sigmoid, logit, e_sigmoid, percentiles, HANDCODED, cem, OUT,
                 aggregate, claim_terms, pop_stats, D, LO, HI)
from rules import RULES as R13

NEW = ["PEER", "PEER-SUM", "FE-BRIER", "EB-BRIER-PM", "EB-IG-PM", "EB0-IG-PM"]
RULES = R13 + NEW
CACHE = OUT / "sim_cache_v3"
FLOOR = 1e-12


def pm_stats(src, x, n_src, s2w):
    """Paule-Mandel tau^2 for per-source means of x, with sampling variance s2w/n_i. Returns mu_w, kappa, tau2."""
    cnt = np.bincount(src, minlength=n_src).astype(float)
    ok = cnt >= 2
    m = (np.bincount(src, weights=x, minlength=n_src) / np.maximum(cnt, 1))[ok]
    v = s2w / cnt[ok]
    k = ok.sum()

    def g(t2):
        w = 1 / (t2 + v)
        mu = (w * m).sum() / w.sum()
        return (w * (m - mu) ** 2).sum() - (k - 1), mu

    g0, mu0 = g(FLOOR)
    if g0 <= 0:
        t2, mu = FLOOR, mu0
    else:
        lo, hi = FLOOR, max(10 * m.var(), 1e-9)
        for _ in range(80):
            mid = 0.5 * (lo + hi)
            if g(mid)[0] > 0: lo = mid
            else: hi = mid
        t2 = 0.5 * (lo + hi); mu = g(t2)[1]
    return {"mu": float(mu), "kappa": float(s2w / t2), "tau2": float(t2)}


def fe_als(src, ev, b, n_src, n_ev, sweeps=25):
    a = np.zeros(n_src); g = np.zeros(n_ev)
    cs = np.maximum(np.bincount(src, minlength=n_src), 1); ce = np.maximum(np.bincount(ev, minlength=n_ev), 1)
    for _ in range(sweeps):
        a = np.bincount(src, weights=b - g[ev], minlength=n_src) / cs
        g = np.bincount(ev, weights=b - a[src], minlength=n_ev) / ce
    mu = a.mean(); a -= mu; g += mu
    return a, g


def extra_scores(terms, idx_ev, w, n):
    """The 6 new rule scores for ONE source whose claims have `terms` on events idx_ev (cheater)."""
    pv = w["peer_n"][idx_ev] >= 1
    pe = terms["log"] - w["peer_mean"][idx_ev]
    peer = pe[pv].mean() if pv.any() else 0.0
    psum = pe[pv].sum() if pv.any() else 0.0
    fe = -np.mean(terms["brier"] - w["gamma"][idx_ev])
    mb, mig = -terms["brier"].mean(), terms["ig"].mean()
    b, i = w["pm_b"], w["pm_i"]
    return [peer, psum, fe, (n * mb + b["kappa"] * b["mu"]) / (n + b["kappa"]),
            (n * mig + i["kappa"] * i["mu"]) / (n + i["kappa"]), n * mig / (n + i["kappa"])]


def make_world(rng, cond, n_events=3000, n_honest=200):
    topic = rng.integers(0, N_TOPICS, n_events)
    a = rng.normal(TOPIC_MU[topic], 1.5)
    sig = rng.uniform(0.25, 2.5, n_events)
    b = rng.normal(0.0, sig)
    y = rng.random(n_events) < sigmoid(a + b)
    crowd_true = e_sigmoid(a, sig)
    c = sigmoid(cond["crowd_slope"] * logit(crowd_true))
    conf_bin = np.searchsorted(BIN_EDGES, np.abs(c - 0.5), side="right")
    k = rng.uniform(0.1, 0.9, n_honest)
    n = np.round(np.exp(rng.uniform(np.log(cond["min_n"]), np.log(500), n_honest))).astype(int)
    lam = np.exp(rng.normal(0, cond["miscal"], n_honest)) if cond["miscal"] > 0 else np.ones(n_honest)
    src, ev = [], []
    for j in range(n_honest):
        src.append(np.full(n[j], j))
        ev.append(rng.choice(n_events, n[j], replace=False))
    src, ev = np.concatenate(src), np.concatenate(ev)
    kk = k[src]
    s = b[ev] + rng.normal(0, 1, len(ev)) * sig[ev] * np.sqrt((1 - kk) / kk)
    r = e_sigmoid(a[ev] + kk * s, sig[ev] * np.sqrt(1 - kk))
    r = sigmoid(lam[src] * logit(r))
    terms = claim_terms(r, y[ev], c[ev])
    stats = pop_stats(src, n_honest, terms, topic[ev], N_TOPICS)
    scores = aggregate(src, n_honest, terms, topic[ev], stats)
    # ---- extras ----
    lg = terms["log"]
    sum_e = np.bincount(ev, weights=lg, minlength=n_events); n_e = np.bincount(ev, minlength=n_events)
    loo_n = n_e[ev] - 1
    valid = loo_n >= 1
    loo = np.where(valid, (sum_e[ev] - lg) / np.maximum(loo_n, 1), 0.0)
    pe = np.where(valid, lg - loo, 0.0)
    peer_sum = np.bincount(src, weights=pe, minlength=n_honest)
    peer_cnt = np.bincount(src, weights=valid.astype(float), minlength=n_honest)
    scores["PEER-SUM"] = peer_sum
    scores["PEER"] = peer_sum / np.maximum(peer_cnt, 1)
    al, gam = fe_als(src, ev, terms["brier"], n_honest, n_events)
    scores["FE-BRIER"] = -al
    cnt = np.bincount(src, minlength=n_honest).astype(float)
    s2b, s2i = stats["eb_brier"]["s2w"], stats["eb_ig"]["s2w"]
    pm_b = pm_stats(src, -terms["brier"], n_honest, s2b); pm_i = pm_stats(src, terms["ig"], n_honest, s2i)
    mb = -np.bincount(src, weights=terms["brier"], minlength=n_honest) / cnt
    mig = np.bincount(src, weights=terms["ig"], minlength=n_honest) / cnt
    scores["EB-BRIER-PM"] = (cnt * mb + pm_b["kappa"] * pm_b["mu"]) / (cnt + pm_b["kappa"])
    scores["EB-IG-PM"] = (cnt * mig + pm_i["kappa"] * pm_i["mu"]) / (cnt + pm_i["kappa"])
    scores["EB0-IG-PM"] = cnt * mig / (cnt + pm_i["kappa"])
    H = np.stack([scores[R] for R in RULES])
    return {"topic": topic, "c": c, "y": y, "bin": conf_bin, "stats": stats, "H": H, "k": k, "n": n,
            "peer_mean": np.where(n_e > 0, sum_e / np.maximum(n_e, 1), 0.0), "peer_n": n_e, "gamma": gam,
            "pm_b": pm_b, "pm_i": pm_i,
            "floor_b": bool(stats["eb_brier"]["tau2"] <= FLOOR * 1.001), "floor_i": bool(stats["eb_ig"]["tau2"] <= FLOOR * 1.001),
            "floor_b_pm": bool(pm_b["tau2"] <= FLOOR * 1.001), "floor_i_pm": bool(pm_i["tau2"] <= FLOOR * 1.001)}


def cheater_scores(theta, w, rng):
    logw = theta[:N_BINS][w["bin"]] + theta[N_BINS:N_BINS + N_TOPICS][w["topic"]]
    n = int(round(10 ** np.clip(theta[-1], LO[-1], HI[-1])))
    g = logw + rng.gumbel(size=len(logw))
    idx = np.argpartition(-g, n - 1)[:n]
    alpha, beta = theta[-3], theta[-2]
    r = sigmoid(alpha * logit(w["c"][idx]) + beta)
    terms = claim_terms(r, w["y"][idx], w["c"][idx])
    sc = aggregate(np.zeros(n, dtype=int), 1, terms, w["topic"][idx], w["stats"])
    return np.array([sc[R][0] for R in R13] + extra_scores(terms, idx, w, n))


sim.cheater_scores = cheater_scores


def run_seed(args):
    cond_name, seed = args
    fn = CACHE / f"{cond_name}_{seed}.json"
    if fn.exists():
        return json.loads(fn.read_text())
    cond = sim.CONDS[cond_name]
    t0 = time.time()
    rng = np.random.default_rng([seed, 1000 + list(sim.CONDS).index(cond_name)])
    train = [make_world(rng, cond) for _ in range(40)]
    test = [make_world(rng, cond) for _ in range(20)]

    def evaluate(theta, reps=1):
        return np.array([percentiles(cheater_scores(theta, w, rng), w["H"]) for w in test for _ in range(reps)])

    res = {"cond": cond_name, "seed": seed, "rules": RULES, "learned": {}, "handcoded": {}}
    for name, th in HANDCODED.items():
        th = th.copy(); th[-1] = max(th[-1], np.log10(cond["min_n"]))
        P = evaluate(th, 3)
        res["handcoded"][name] = {"pct_mean": P.mean(0).tolist()}
    # honest-skill recovery: Spearman(score, k) and Spearman(score, volume N), mean over the 20 test worlds
    def sp(x, z):
        return float(np.mean([spearmanr(w["H"][ri], w[z]).correlation for w in test]))
    res["skill_rho"] = {R: sp(None, "k") if False else float(np.nanmean([spearmanr(w["H"][ri], w["k"]).correlation for w in test])) for ri, R in enumerate(RULES)}
    res["vol_rho"] = {R: float(np.nanmean([spearmanr(w["H"][ri], w["n"]).correlation for w in test])) for ri, R in enumerate(RULES)}
    res["floor_flags"] = {f: [w[f] for w in test] for f in ("floor_b", "floor_i", "floor_b_pm", "floor_i_pm")}
    for ri, R in enumerate(RULES):
        theta, curve = cem(ri, train, rng, 40, 64, 12, 6, cond["min_n"])
        P = evaluate(theta, 3)
        res["learned"][R] = {"theta": theta.tolist(), "pct": float(P[:, ri].mean()), "beat_median": float((P[:, ri] > 50).mean())}
        if R in ("EB-BRIER", "EB-IG", "EB-BRIER-PM", "EB-IG-PM"):
            res["learned"][R]["per_world"] = P[:, ri].reshape(len(test), 3).mean(1).tolist()
    res["seconds"] = time.time() - t0
    CACHE.mkdir(exist_ok=True)
    fn.write_text(json.dumps(res))
    print(f"[v3 {cond_name} seed {seed}] {res['seconds']:.0f}s " + " ".join(f"{R}={res['learned'][R]['pct']:.0f}" for R in RULES), flush=True)
    return res


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", default="main"); ap.add_argument("--seeds", type=int, default=30)
    ap.add_argument("--workers", type=int, default=18); ap.add_argument("--smoke", action="store_true")
    a = ap.parse_args()
    if a.smoke:
        CACHE = OUT / "sim_cache_v3_smoke"; jobs = [(a.cond, 0)]
    else:
        jobs = [(a.cond, s) for s in range(a.seeds)]
    with Pool(min(a.workers, len(jobs))) as p:
        out = p.map(run_seed, jobs, chunksize=1)
    if not a.smoke:
        (OUT / f"sim_v3_{a.cond}.json").write_text(json.dumps(out))
    print("done", a.cond, flush=True)
