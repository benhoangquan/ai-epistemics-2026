"""X4 (review round): a crowd distortion that is NOT linear in log-odds, matched in mean baseline error to R2.
R2asym: for the true crowd probability p >= 0.5, c = 0.5 + 0.5 * (2p - 1)**gamma (gamma > 1: favourites under-priced, the
longshot side p < 0.5 is left exactly as is, so the bias is asymmetric and not a logit-linear map). gamma is chosen so that
mean |c - p| over events equals 0.044, R2's value (results/E03/sim_recal_summary.csv, cal_err_raw for R2_*), using 5 pooled worlds.
Everything else (blocks, recalibration modes, CEM, rng stream paired with original R2) is sim_recal.py.
    uv run python -I experiments/E03_track_record/sim_recal_asym.py --seeds 30
"""
import json, sys
from multiprocessing import Pool
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim, sim_recal
from sim import sigmoid, logit, e_sigmoid, N_TOPICS, TOPIC_MU


def distort(p, g):
    return np.where(p >= 0.5, 0.5 + 0.5 * np.abs(2 * p - 1) ** g, p)


def calibrate_gamma(target=0.044):
    rng = np.random.default_rng(123)
    cts = []
    for _ in range(5):
        topic = rng.integers(0, N_TOPICS, 3000); a = rng.normal(TOPIC_MU[topic], 1.5); sig = rng.uniform(0.25, 2.5, 3000)
        cts.append(e_sigmoid(a, sig))
    p = np.concatenate(cts)
    lo, hi = 1.0, 3.0
    for _ in range(50):
        mid = 0.5 * (lo + hi)
        if np.abs(distort(p, mid) - p).mean() < target: lo = mid
        else: hi = mid
    return 0.5 * (lo + hi), float(np.abs(distort(p, 0.5 * (lo + hi)) - p).mean())


GAMMA, ACHIEVED = calibrate_gamma()
orig = sim_recal.crowd_of
sim_recal.crowd_of = lambda ct, b: distort(ct, b["gamma"]) if "gamma" in b else orig(ct, b)
sim_recal.BIAS["R2asym"] = dict(gamma=GAMMA)
sim_recal.CACHE = sim.OUT / "sim_cache_recal_asym"

if __name__ == "__main__":
    n = int(sys.argv[sys.argv.index("--seeds") + 1]) if "--seeds" in sys.argv else 30
    jobs = [("R2asym", m, s) for m in ("none", "logit", "iso") for s in range(n)]
    with Pool(18) as p:
        out = p.map(sim_recal.run_seed, jobs, chunksize=1)
    (sim.OUT / "sim_recal_asym_all.json").write_text(json.dumps({"gamma": GAMMA, "mean_abs_err_achieved": ACHIEVED, "runs": out}))
    print("done asym gamma", GAMMA, ACHIEVED, flush=True)
