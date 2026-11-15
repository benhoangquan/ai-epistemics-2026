"""Summaries for items 1-2 (post hoc, 15 Nov). Bootstrap = 10,000 resamples of seeds, 95% percentile CI."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
from rules import RULES
OUT = Path(__file__).resolve().parents[2] / "results" / "E03"
rng = np.random.default_rng(0)

def ci(v):
    v = np.asarray(v, float)
    b = rng.choice(v, (10000, len(v))).mean(1)
    return v.mean(), *np.percentile(b, [2.5, 97.5])

rows = []
for cond in ["main", "R2"]:
    res = json.loads((OUT / f"sim_{cond}_30seeds.json").read_text())
    for ri, R in enumerate(RULES):
        v = [r["learned"][R]["pct"] for r in res]
        m, lo, hi = ci(v)
        m10, l10, h10 = ci(v[:10]); m20, _, _ = ci(v[10:])
        bm = ci([r["learned"][R]["beat_median"] for r in res])
        rows.append(dict(cond=cond, rule=R, n_seeds=len(v), pct=m, ci_lo=lo, ci_hi=hi, sd_over_seeds=np.std(v, ddof=1),
                         seed_min=min(v), seed_max=max(v), median_seed=np.median(v), pct_first10=m10,
                         first10_lo=l10, first10_hi=h10, pct_new20=m20, beat_median_share=bm[0],
                         bm_lo=bm[1], bm_hi=bm[2]))
S = pd.DataFrame(rows)
S.round(2).to_csv(OUT / "sim_30seeds_summary.csv", index=False)
print(S[["cond", "rule", "pct", "ci_lo", "ci_hi", "sd_over_seeds", "seed_min", "seed_max", "pct_first10", "pct_new20"]].round(1).to_string(index=False))
bss = {c: [round(r["learned"]["BSS"]["pct"], 1) for r in json.loads((OUT / f"sim_{c}_30seeds.json").read_text())] for c in ["main", "R2"]}
(OUT / "sim_30seeds_bss_per_seed.json").write_text(json.dumps(bss))

# ---- item 1 ----
allr = json.loads((OUT / "sim_recal_all.json").read_text())
rows = []
for cond in sorted({r["cond"] for r in allr}):
    res = [r for r in allr if r["cond"] == cond]
    for ri, R in enumerate(RULES):
        v = [r["learned"][R]["pct"] for r in res]
        m, lo, hi = ci(v)
        hc = {h: np.mean([r["handcoded"][h]["pct_mean"][ri] for r in res]) for h in res[0]["handcoded"]}
        bh = max(hc, key=hc.get)
        bm = ci([r["learned"][R]["beat_median"] for r in res])
        rows.append(dict(cond=cond, rule=R, n_seeds=len(v), pct=m, ci_lo=lo, ci_hi=hi, seed_min=min(v), seed_max=max(v),
                         beat_median_share=bm[0], best_handcoded=bh, best_handcoded_pct=hc[bh],
                         cal_err_raw=np.mean([r["cal_err_raw"] for r in res]),
                         cal_err_baseline=np.mean([r["cal_err_base"] for r in res]),
                         n_honest=np.mean([r["n_honest"] for r in res])))
T = pd.DataFrame(rows)
T.round(3).to_csv(OUT / "sim_recal_summary.csv", index=False)
pv = T.pivot(index="rule", columns="cond", values="pct").loc[RULES]
print(pv.round(1).to_string())
print(T[T.rule == "IG-SUM"][["cond", "pct", "ci_lo", "ci_hi", "cal_err_raw", "cal_err_baseline"]].round(3).to_string())
# learned policies (median over seeds) for the crowd-relative rules
pol = []
for cond in sorted({r["cond"] for r in allr}):
    for R in ["BSS", "IG", "EB0-IG", "IG-SUM", "BRIER-GAIN"]:
        th = np.array([r["learned"][R]["theta"] for r in allr if r["cond"] == cond])
        pol.append(dict(cond=cond, trained_on=R, alpha=np.median(th[:, -3]), beta=np.median(th[:, -2]),
                        n_claims=np.median(10 ** th[:, -1])))
pd.DataFrame(pol).round(2).to_csv(OUT / "sim_recal_policies.csv", index=False)
print(pd.DataFrame(pol).round(2).to_string(index=False))
