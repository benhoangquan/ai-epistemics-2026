"""Check of the FE-BRIER approximation used in sim_v3.py (cheater effect solved with honest-fitted event effects held fixed)
against a full ALS that includes the cheater as a 201st source. 20 main worlds, 3 cheater policies. Output: results/E03/review_fe_check.json"""
import json, sys
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sim, sim_v3
from sim import theta_of, N_BINS, N_TOPICS, sigmoid, logit, claim_terms, percentiles
cap = {}
orig = sim_v3.fe_als
sim_v3.fe_als = lambda src, ev, b, ns, ne, sweeps=25: (cap.update(src=src, ev=ev, b=b, ns=ns, ne=ne), orig(src, ev, b, ns, ne, sweeps))[1]
rng = np.random.default_rng(5)
pol = {"copy-crowd-n100": theta_of(n=100), "cherry-flood-1000": theta_of(sel_bins=[5], n=1000), "cherry-10": theta_of(sel_bins=[5], n=10)}
out = {k: [] for k in pol}
for _ in range(20):
    w = sim_v3.make_world(rng, sim.CONDS["main"])
    src, ev, b, ns, ne = cap["src"], cap["ev"], cap["b"], cap["ns"], cap["ne"]
    ri = sim_v3.RULES.index("FE-BRIER")
    for name, th in pol.items():
        th = th.copy(); th[-1] = max(th[-1], 1.0)
        x = sim_v3.cheater_scores(th, w, np.random.default_rng(1))
        approx_pct = percentiles(x[[ri]], w["H"][[ri]])[0]
        # full fit with the same claims: recover claim set by replaying the policy
        logw = th[:N_BINS][w["bin"]] + th[N_BINS:N_BINS + N_TOPICS][w["topic"]]
        n = int(round(10 ** th[-1])); g = logw + np.random.default_rng(1).gumbel(size=len(logw)); idx = np.argpartition(-g, n - 1)[:n]
        r = sigmoid(th[-3] * logit(w["c"][idx]) + th[-2]); t = claim_terms(r, w["y"][idx], w["c"][idx])
        a, gam = orig(np.r_[src, np.full(n, ns)], np.r_[ev, idx], np.r_[b, t["brier"]], ns + 1, ne)
        full = -a[ns]; hon = -a[:ns]
        full_pct = 100 * ((hon < full).mean() + 0.5 * (hon == full).mean())
        out[name].append([float(approx_pct), float(full_pct)])
res = {k: {"mean_approx_pct": float(np.mean([a for a, _ in v])), "mean_full_pct": float(np.mean([f for _, f in v])),
           "max_abs_diff": float(np.max([abs(a - f) for a, f in v]))} for k, v in out.items()}
(Path(__file__).resolve().parents[2] / "results" / "E03" / "review_fe_check.json").write_text(json.dumps(res, indent=1))
print(json.dumps(res, indent=1))
