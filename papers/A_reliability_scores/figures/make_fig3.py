"""Figure 3: learned-cheater percentile for IG-SUM and EB0-IG under no, logistic and isotonic recalibration.
Reads results/E03/sim_recal_summary.csv (columns cond, rule, pct, ci_lo, ci_hi). Writes fig3_recalibration.png next to this script."""
import csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "results", "E03", "sim_recal_summary.csv")
rows = {(r["cond"], r["rule"]): r for r in csv.DictReader(open(SRC))}
worlds = [("main", "calibrated crowd"), ("R2", "longshot-biased crowd (R2)"), ("R2tail", "tail bias (R2tail, weak test)")]
modes = [("none", "raw crowd", "#888888"), ("logit", "logistic recalibration", "#1b9e77"), ("iso", "isotonic recalibration", "#d95f02")]
rules = ["IG-SUM", "EB0-IG"]
fig, axes = plt.subplots(1, 2, figsize=(10, 3.8), sharey=True)
for ax, rule in zip(axes, rules):
    for wi, (w, wl) in enumerate(worlds):
        for mi, (m, ml, col) in enumerate(modes):
            r = rows[(f"{w}_{m}", rule)]
            y = wi + (mi - 1) * 0.22
            p, lo, hi = float(r["pct"]), float(r["ci_lo"]), float(r["ci_hi"])
            ax.errorbar(p, y, xerr=[[p - lo], [hi - p]], fmt="o", color=col, capsize=2, label=ml if wi == 0 else None)
    ax.axvline(50, color="k", ls="--", lw=1)
    ax.set_xlim(0, 100)
    ax.set_title(rule)
    ax.set_xlabel("Learned-cheater percentile among honest sources")
    ax.grid(axis="x", alpha=0.3)
axes[0].set_yticks(range(len(worlds)))
axes[0].set_yticklabels([wl for _, wl in worlds])
axes[0].invert_yaxis()
h, l = axes[0].get_legend_handles_labels()
fig.legend(h, l, loc="lower center", ncol=3, fontsize=8, frameon=False, bbox_to_anchor=(0.5, 0.04))
fig.text(0.01, 0.01, "Mean over 30 seeds; bars are 95% bootstrap CIs. Dashed line: median honest source.", fontsize=8, color="#555")
fig.tight_layout(rect=(0, 0.1, 1, 1))
out = os.path.join(HERE, "fig3_recalibration.png")
fig.savefig(out, dpi=170)
print("wrote", out)
