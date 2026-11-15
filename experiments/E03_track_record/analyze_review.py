"""Review round summaries: X1 (new rules), X2 (skill/volume recovery), X3 (EB floor diagnostics), X4 (asymmetric distortion).
Bootstrap = 10,000 resamples of seeds (cluster bootstrap for pooled per-world numbers), 95% percentile CI."""
import json, sys
from pathlib import Path
import numpy as np, pandas as pd
sys.path.insert(0, str(Path(__file__).resolve().parent))
OUT = Path(__file__).resolve().parents[2] / "results" / "E03"
rng = np.random.default_rng(0)
pd.set_option("display.width", 250)


def ci(v):
    v = np.asarray(v, float)
    b = rng.choice(v, (10000, len(v))).mean(1)
    return v.mean(), *np.percentile(b, [2.5, 97.5])


conds = [c for c in ("main", "R1", "R2") if (OUT / f"sim_v3_{c}.json").exists()]
R = {c: json.loads((OUT / f"sim_v3_{c}.json").read_text()) for c in conds}
RULES = R[conds[0]][0]["rules"]
x1, x2, x3 = [], [], []
for c in conds:
    res = R[c]
    for ri, r in enumerate(RULES):
        v = [s["learned"][r]["pct"] for s in res]
        m, lo, hi = ci(v)
        hc = {h: [s["handcoded"][h]["pct_mean"][ri] for s in res] for h in res[0]["handcoded"]}
        bh = max(hc, key=lambda h: np.mean(hc[h]))
        cc = ci(hc["copy-crowd"])
        bm = ci([s["learned"][r]["beat_median"] for s in res])
        x1.append(dict(cond=c, rule=r, n_seeds=len(v), pct=m, ci_lo=lo, ci_hi=hi, seed_min=min(v), seed_max=max(v),
                       beat_median_share=bm[0], best_handcoded=bh, best_handcoded_pct=np.mean(hc[bh]),
                       copy_crowd_pct=cc[0], copy_lo=cc[1], copy_hi=cc[2]))
        sk = ci([s["skill_rho"][r] for s in res]); vo = ci([s["vol_rho"][r] for s in res])
        x2.append(dict(cond=c, rule=r, n_seeds=len(v), rho_skill=sk[0], skill_lo=sk[1], skill_hi=sk[2],
                       rho_volume=vo[0], vol_lo=vo[1], vol_hi=vo[2]))
X1 = pd.DataFrame(x1); X1.round(2).to_csv(OUT / "review_x1_rules_summary.csv", index=False)
X2 = pd.DataFrame(x2); X2.round(3).to_csv(OUT / "review_x2_skill_volume.csv", index=False)
print(X1[X1.rule.isin(["PEER", "PEER-SUM", "FE-BRIER"])].round(1).to_string(index=False))
print(X1.pivot(index="rule", columns="cond", values="pct").loc[RULES].round(1).to_string())
print(X2.pivot(index="rule", columns="cond", values=["rho_skill", "rho_volume"]).loc[RULES].round(2).to_string())
# X3
for c in conds:
    res = R[c]
    for rule, flag in [("EB-BRIER", "floor_b"), ("EB-IG", "floor_i"), ("EB-BRIER-PM", "floor_b_pm"), ("EB-IG-PM", "floor_i_pm")]:
        P = np.array([s["learned"][rule]["per_world"] for s in res]); F = np.array([s["floor_flags"][flag] for s in res])
        for name, mask in (("at floor", F), ("above floor", ~F)):
            seeds_ok = [i for i in range(len(res)) if mask[i].any()]
            if not seeds_ok:
                x3.append(dict(cond=c, rule=rule, group=name, share_worlds=0.0, n_worlds=0)); continue
            def pooled(idx): return np.mean(np.concatenate([P[i][mask[i]] for i in idx]))
            pt = pooled(seeds_ok)
            bs = [pooled(rng.choice(seeds_ok, len(seeds_ok))) for _ in range(2000)]
            x3.append(dict(cond=c, rule=rule, group=name, share_worlds=float(mask.mean()), n_worlds=int(mask.sum()),
                           n_seeds_with=len(seeds_ok), pct=pt, ci_lo=np.percentile(bs, 2.5), ci_hi=np.percentile(bs, 97.5)))
X3 = pd.DataFrame(x3); X3.round(3).to_csv(OUT / "review_x3_eb_floor.csv", index=False)
print(X3.round(2).to_string(index=False))
# policies of the new rules (median over seeds)
pol = []
for c in conds:
    for r in ["PEER", "PEER-SUM", "FE-BRIER", "IG-SUM", "EB-BRIER-PM", "EB0-IG-PM"]:
        th = np.array([s["learned"][r]["theta"] for s in R[c]])
        pol.append(dict(cond=c, rule=r, alpha=np.median(th[:, -3]), beta=np.median(th[:, -2]), n_claims=np.median(10 ** th[:, -1])))
pd.DataFrame(pol).round(2).to_csv(OUT / "review_x1_policies.csv", index=False); print(pd.DataFrame(pol).round(2).to_string(index=False))
# X4
fa = OUT / "sim_recal_asym_all.json"
if fa.exists():
    A = json.loads(fa.read_text()); runs = A["runs"]; rows = []
    from sim_recal import RULES as R13
    for cond in sorted({s["cond"] for s in runs}):
        rs = [s for s in runs if s["cond"] == cond]
        for ri, r in enumerate(R13):
            v = [s["learned"][r]["pct"] for s in rs]; m, lo, hi = ci(v)
            hc = {h: np.mean([s["handcoded"][h]["pct_mean"][ri] for s in rs]) for h in rs[0]["handcoded"]}
            bh = max(hc, key=hc.get)
            rows.append(dict(cond=cond, rule=r, n_seeds=len(v), pct=m, ci_lo=lo, ci_hi=hi, seed_min=min(v), seed_max=max(v),
                             best_handcoded=bh, best_handcoded_pct=hc[bh], cal_err_raw=np.mean([s["cal_err_raw"] for s in rs]),
                             cal_err_baseline=np.mean([s["cal_err_base"] for s in rs])))
    T = pd.DataFrame(rows); T.round(3).to_csv(OUT / "review_x4_asym_summary.csv", index=False)
    print("gamma", A["gamma"], A["mean_abs_err_achieved"])
    print(T[T.rule.isin(["IG-SUM", "EB0-IG", "IG", "BRIER-GAIN", "BSS", "EB-IG"])].round(2).to_string(index=False))
