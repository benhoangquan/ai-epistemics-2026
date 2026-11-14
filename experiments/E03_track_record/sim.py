"""Part A: simulated track-record ledger with honest skilled sources, hand-coded zero-skill cheats and
learning cheaters trained by the cross-entropy method (CEM) against each scoring rule.

    uv run python -I experiments/E03_track_record/sim.py --smoke          # quick check
    uv run python -I experiments/E03_track_record/sim.py --cond main --seeds 10
    uv run python -I experiments/E03_track_record/sim.py --cond R1 --seeds 5   # exploratory robustness

Outputs go to results/E03/sim_<cond>.json (resumable per seed: results/E03/sim_cache/<cond>_<seed>.json).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
from rules import RULES, aggregate, claim_terms, pop_stats  # noqa: E402

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "results" / "E03"
CACHE = OUT / "sim_cache"

TOPIC_MU = np.array([-2.5, -1.25, 0.0, 1.25, 2.5])
N_TOPICS = len(TOPIC_MU)
BIN_EDGES = np.array([0.1, 0.2, 0.3, 0.4, 0.45])  # on |c - 0.5|; 6 bins, last = crowd >= 0.95 either way
N_BINS = len(BIN_EDGES) + 1
GH_X, GH_W = np.polynomial.hermite_e.hermegauss(32)
GH_W = GH_W / GH_W.sum()

CONDS = {
    "main": dict(miscal=0.0, crowd_slope=1.0, min_n=10),
    "R1": dict(miscal=0.3, crowd_slope=1.0, min_n=10),   # honest sources miscalibrated
    "R2": dict(miscal=0.0, crowd_slope=0.75, min_n=10),  # crowd has favourite-longshot bias
    "R3": dict(miscal=0.0, crowd_slope=1.0, min_n=30),   # minimum volume 30 claims
}

# theta layout: 6 bin logits, 5 topic logits, alpha, beta, log10 volume
D = N_BINS + N_TOPICS + 3
LO = np.r_[np.full(N_BINS + N_TOPICS, -8.0), -2.0, -4.0, 1.0]
HI = np.r_[np.full(N_BINS + N_TOPICS, 8.0), 8.0, 4.0, 3.0]


def sigmoid(x):
    return 1.0 / (1.0 + np.exp(-x))


def logit(p):
    p = np.clip(p, 1e-9, 1 - 1e-9)
    return np.log(p / (1 - p))


def e_sigmoid(mu, sd):
    """E[sigmoid(mu + sd * Z)], Z ~ N(0, 1), by Gauss-Hermite quadrature."""
    return (sigmoid(mu[:, None] + sd[:, None] * GH_X[None, :]) * GH_W[None, :]).sum(1)


def make_world(rng, cond, n_events=3000, n_honest=200):
    topic = rng.integers(0, N_TOPICS, n_events)
    a = rng.normal(TOPIC_MU[topic], 1.5)
    sig = rng.uniform(0.25, 2.5, n_events)
    b = rng.normal(0.0, sig)
    y = rng.random(n_events) < sigmoid(a + b)
    crowd_true = e_sigmoid(a, sig)
    c = sigmoid(cond["crowd_slope"] * logit(crowd_true))  # published crowd prior
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
    H = np.stack([scores[R] for R in RULES])  # (n_rules, n_honest)
    return {"topic": topic, "c": c, "y": y, "bin": conf_bin, "stats": stats, "H": H, "k": k, "n": n}


def cheater_scores(theta, w, rng):
    """All rule scores for one zero-skill source with policy theta in world w."""
    logw = theta[:N_BINS][w["bin"]] + theta[N_BINS:N_BINS + N_TOPICS][w["topic"]]
    n = int(round(10 ** np.clip(theta[-1], LO[-1], HI[-1])))
    g = logw + rng.gumbel(size=len(logw))
    idx = np.argpartition(-g, n - 1)[:n]
    alpha, beta = theta[-3], theta[-2]
    r = sigmoid(alpha * logit(w["c"][idx]) + beta)
    terms = claim_terms(r, w["y"][idx], w["c"][idx])
    sc = aggregate(np.zeros(n, dtype=int), 1, terms, w["topic"][idx], w["stats"])
    return np.array([sc[R][0] for R in RULES])


def percentiles(x, H):
    """Percentile of scores x (n_rules,) among honest scores H (n_rules, n_honest); ties count half."""
    return 100.0 * ((H < x[:, None]).sum(1) + 0.5 * (H == x[:, None]).sum(1)) / H.shape[1]


def theta_of(sel_bins=None, sel_topics=None, alpha=1.0, beta=0.0, n=100):
    t = np.zeros(D)
    if sel_bins is not None:
        t[:N_BINS] = np.where(np.isin(np.arange(N_BINS), sel_bins), 8.0, -8.0)
    if sel_topics is not None:
        t[N_BINS:N_BINS + N_TOPICS] = np.where(np.isin(np.arange(N_TOPICS), sel_topics), 8.0, -8.0)
    t[-3], t[-2], t[-1] = alpha, beta, np.log10(n)
    return t


HANDCODED = {
    "copy-crowd": theta_of(),
    "always-0.5": theta_of(alpha=0.0),
    "cherry-pick": theta_of(sel_bins=[5]),
    "cherry+extremize": theta_of(sel_bins=[5], alpha=8.0),
    "extremize": theta_of(alpha=3.0),
    "flood": theta_of(n=1000),
    "abstain-hard": theta_of(sel_bins=[3, 4, 5]),
    "topic-pick": theta_of(sel_topics=[0]),
    "low-vol-gamble": theta_of(alpha=3.0, n=10),
    "cherry+flood": theta_of(sel_bins=[5], n=1000),
}


def cem(rule_i, train_worlds, rng, iters, pop, n_elite, worlds_per_iter, min_n):
    lo = LO.copy()
    lo[-1] = np.log10(min_n)
    mean = theta_of()
    mean[-1] = max(mean[-1], lo[-1])
    std = np.r_[np.full(N_BINS + N_TOPICS, 2.0), 1.5, 1.0, 0.5]
    curve = []
    for it in range(iters):
        th = np.clip(mean + std * rng.standard_normal((pop, D)), lo, HI)
        wi = rng.choice(len(train_worlds), worlds_per_iter, replace=False)
        seeds = rng.integers(0, 2**31, worlds_per_iter)
        rew = np.zeros(pop)
        for q, (j, sd) in enumerate(zip(wi, seeds)):
            w = train_worlds[j]
            for p in range(pop):  # common random numbers across candidates within a world
                x = cheater_scores(th[p], w, np.random.default_rng(sd))
                rew[p] += percentiles(x[[rule_i]], w["H"][[rule_i]])[0]
        rew /= worlds_per_iter
        el = th[np.argsort(-rew)[:n_elite]]
        mean = el.mean(0)
        std = 0.8 * el.std(0) + 0.2 * std + 0.02
        curve.append(float(rew.mean()))
    return mean, curve


def run_seed(args):
    cond_name, seed, smoke, strong = args
    fn = CACHE / f"{cond_name}_{seed}{'_smoke' if smoke else ''}{'_strong' if strong else ''}.json"
    if fn.exists():
        return json.loads(fn.read_text())
    cond = CONDS[cond_name]
    t0 = time.time()
    rng = np.random.default_rng([seed, 1000 + list(CONDS).index(cond_name)])
    n_train, n_test = (6, 4) if smoke else (40, 20)
    iters, pop, n_elite, wpi = (5, 16, 4, 2) if smoke else (80, 128, 16, 8) if strong else (40, 64, 12, 6)
    train = [make_world(rng, cond) for _ in range(n_train)]
    test = [make_world(rng, cond) for _ in range(n_test)]

    def evaluate(theta, reps=1):
        P = []
        for w in test:
            for _ in range(reps):
                P.append(percentiles(cheater_scores(theta, w, rng), w["H"]))
        return np.array(P)  # (n_test*reps, n_rules)

    res = {"cond": cond_name, "seed": seed, "rules": RULES, "learned": {}, "handcoded": {}}
    for name, th in HANDCODED.items():
        th = th.copy()
        th[-1] = max(th[-1], np.log10(cond["min_n"]))
        P = evaluate(th, reps=3)
        res["handcoded"][name] = {"pct_mean": P.mean(0).tolist(), "beat_median": (P > 50).mean(0).tolist()}
    # honest reference: the median honest source (k = 0.5) is ~50 by construction; record EB constants
    res["eb"] = {R: [w["stats"][key][R2] for w in test] for R, key, R2 in
                 [("brier_kappa", "eb_brier", "kappa"), ("ig_kappa", "eb_ig", "kappa"), ("ig_mu", "eb_ig", "mu")]}
    for ri, R in enumerate(RULES):
        theta, curve = cem(ri, train, rng, iters, pop, n_elite, wpi, cond["min_n"])
        P = evaluate(theta, reps=3)
        res["learned"][R] = {"theta": theta.tolist(), "curve": curve, "pct_all_rules": P.mean(0).tolist(),
                             "pct": float(P[:, ri].mean()), "beat_median": float((P[:, ri] > 50).mean())}
    res["seconds"] = time.time() - t0
    fn.parent.mkdir(parents=True, exist_ok=True)
    fn.write_text(json.dumps(res))
    print(f"[{cond_name}{' strong' if strong else ''} seed {seed}] done in {res['seconds']:.0f}s: " +
          " ".join(f"{R}={res['learned'][R]['pct']:.0f}" for R in RULES), flush=True)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cond", default="main", choices=list(CONDS))
    ap.add_argument("--seeds", type=int, default=10)
    ap.add_argument("--workers", type=int, default=min(10, os.cpu_count() or 1))
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--strong", action="store_true", help="exploratory: ~5x larger CEM budget (80 iters, pop 128, 8 worlds per iter)")
    a = ap.parse_args()
    jobs = [(a.cond, s, a.smoke, a.strong) for s in range(1 if a.smoke else a.seeds)]
    with Pool(min(a.workers, len(jobs))) as pool:
        out = pool.map(run_seed, jobs)
    name = f"sim_{a.cond}{'_smoke' if a.smoke else ''}{'_strong' if a.strong else ''}.json"
    (OUT / name).write_text(json.dumps(out))
    print(f"wrote {OUT / name}", flush=True)


if __name__ == "__main__":
    main()
