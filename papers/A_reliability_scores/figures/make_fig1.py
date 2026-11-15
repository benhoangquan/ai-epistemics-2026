"""Figure 1 at 30 seeds: learned-cheater percentile per rule, conditions main and R2.
Reads results/E03/sim_30seeds_summary.csv (cond, rule, pct, ci_lo, ci_hi). Writes fig1_cheater_inflation_30seeds.png next to this script."""
import csv, os, sys
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = sys.argv[1] if len(sys.argv) > 1 else os.path.join(HERE, "..", "..", "..", "results", "E03", "sim_30seeds_summary.csv")
rows = {(r["cond"], r["rule"]): r for r in csv.DictReader(open(SRC))}
rules = ["ACC", "BRIER", "LOG", "DW-ACC", "DW-BRIER", "TOPIC-BRIER", "EB-BRIER", "BSS", "IG", "EB-IG", "EB0-IG", "IG-SUM", "BRIER-GAIN"]
fam = {r: "#2b6fd6" for r in rules[:6]}
fam["EB-BRIER"] = "#e8662d"; fam["EB-IG"] = "#e8662d"
for r in ["BSS", "IG", "EB0-IG", "IG-SUM", "BRIER-GAIN"]: fam[r] = "#1aa37a"
fig, ax = plt.subplots(figsize=(8.2, 5.4))
for i, rule in enumerate(rules):
    for cond, dy, filled in (("main", -0.15, True), ("R2", 0.15, False)):
        r = rows[(cond, rule)]
        p, lo, hi = float(r["pct"]), float(r["ci_lo"]), float(r["ci_hi"])
        ax.errorbar(p, i + dy, xerr=[[p - lo], [hi - p]], fmt="o", color=fam[rule], mfc=fam[rule] if filled else "white", capsize=2, ms=6)
ax.axvline(50, color="k", ls="--", lw=1)
ax.text(51, 9.6, "median honest source", fontsize=8, color="#444")
ax.set_yticks(range(len(rules)))
ax.set_yticklabels([r + ("*" if r == "BRIER-GAIN" else "") for r in rules])
ax.invert_yaxis(); ax.set_xlim(0, 100)
ax.set_xlabel("Learned zero-skill cheater: percentile among 200 honest sources (held out)")
ax.grid(axis="x", alpha=0.3)
from matplotlib.lines import Line2D
h = [Line2D([], [], marker="o", color="k", ls="", label="main (calibrated crowd)"),
     Line2D([], [], marker="o", color="k", mfc="white", ls="", label="R2 (longshot-biased crowd)"),
     Line2D([], [], marker="s", color="#2b6fd6", ls="", label="absolute, difficulty-weighted, per-topic"),
     Line2D([], [], marker="s", color="#e8662d", ls="", label="shrinkage toward population mean"),
     Line2D([], [], marker="s", color="#1aa37a", ls="", label="crowd-relative")]
ax.legend(handles=h, loc="lower center", bbox_to_anchor=(0.5, -0.32), ncol=2, fontsize=8, frameon=False)
fig.text(0.01, 0.005, "Mean over 30 seeds; bars are 95% bootstrap CIs over seeds. * = rule added post hoc.", fontsize=8, color="#555")
fig.tight_layout(rect=(0, 0.03, 1, 1))
out = os.path.join(HERE, "fig1_cheater_inflation_30seeds.png")
fig.savefig(out, dpi=170)
print("wrote", out)
