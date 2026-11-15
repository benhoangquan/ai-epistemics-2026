"""Summarise llm_pundit_log.csv: held-out (pool B) percentile of the target rule, by model and rule."""
import numpy as np, pandas as pd
from pathlib import Path
OUT = Path(__file__).resolve().parents[2] / "results" / "E03"
d = pd.read_csv(OUT / "llm_pundit_log.csv")
rng = np.random.default_rng(0)
def ci(v):
    v = np.asarray(v, float); b = rng.choice(v, (5000, len(v))).mean(1); return v.mean(), *np.percentile(b, [2.5, 97.5])
rows = []
for rule in ["ACC", "BRIER", "IG", "IG-SUM", "BSS"]:
    for model in list(d.model.unique()) + ["both"]:
        x = d[(d.rule == rule) & (d.stage == "B_heldout") & ((d.model == model) | (model == "both"))]
        a = d[(d.rule == rule) & (d.stage.str.startswith("A_")) & ((d.model == model) | (model == "both"))]
        if len(x) == 0: continue
        m, lo, hi = ci(x[f"pct_{rule}"])
        rows.append(dict(rule=rule, model=model, n_heldout=len(x), B_pct=m, ci_lo=lo, ci_hi=hi, B_min=x[f"pct_{rule}"].min(),
                         B_max=x[f"pct_{rule}"].max(), share_B_above_50=(x[f"pct_{rule}"] > 50).mean(),
                         A_best_of_8_pct=a.groupby(["pair", "model"])[f"pct_{rule}"].max().mean(),
                         B_share_fav_ge90=x.share_fav_ge90.mean(), B_n_claims=x.n_claims.mean(), B_alpha=x.alpha.mean(),
                         ref_copy_top40=x.ref_copy_top40.mean(), ref_copy_random40=x.ref_copy_random40.mean()))
S = pd.DataFrame(rows); S.round(2).to_csv(OUT / "llm_pundit_summary.csv", index=False)
print(S.round(1).to_string(index=False))
n = d[d.rule == "NONE"]
print("NONE (no rule stated), B direct, n=%d:" % len(n)); print(n[[f"pct_{R}" for R in ["ACC","BRIER","IG","IG-SUM","BSS"]] + ["share_fav_ge90","n_claims","alpha"]].mean().round(1).to_string())
