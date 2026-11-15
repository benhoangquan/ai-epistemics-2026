"""Fig 1: mirror bias by drafter under two judges (scaled run) plus pilot verdict bias.
Reads results/E04/summary_v2.json (draft bias, ambiguous, 'write it for me') and summary.json (pilot verdicts).
Fig 2: fault admission by drafter and judge (values and CIs copied from results/E04/tables_v2.md)."""
import json, pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = pathlib.Path(__file__).resolve().parents[3] / "results" / "E04"
OUT = pathlib.Path(__file__).resolve().parent
v2 = json.load(open(R / "summary_v2.json"))
p = json.load(open(R / "summary.json"))
models = ["gemma-4-31b-it", "gemma-4-26b-a4b-it", "glm-5.3-flash", "qwen3.8-27b"]
C = {"verdict": "#8a8a8a", "deepseek": "#1b6ca8", "gemma": "#d2691e"}

fig, ax = plt.subplots(figsize=(6.6, 3.3))
off = {"verdict": 0.24, "deepseek": 0.0, "gemma": -0.24}
lab = {"verdict": "verdict (pilot tellings)", "deepseek": "draft, judge deepseek-v4-flash",
       "gemma": "draft, judge gemma-4-31b-it"}
for i, m in enumerate(models):
    y = len(models) - 1 - i
    pts = {"verdict": p["mirror"][m]["ambiguous"]["bias"],
           "deepseek": dict(zip(("est", "lo", "hi"), v2["bias_me"]["deepseek"][m]["all"])),
           "gemma": dict(zip(("est", "lo", "hi"), v2["bias_me"]["gemma"][m]["all"]))}
    for k, d in pts.items():
        ax.errorbar(d["est"], y + off[k], xerr=[[d["est"] - d["lo"]], [d["hi"] - d["est"]]], fmt="o" if k != "verdict" else "s",
                    color=C[k], capsize=2.5, ms=5, lw=1.3, label=lab[k] if i == 0 else None)
ax.axvline(0, color="k", lw=0.8)
ax.set_yticks(range(len(models))); ax.set_yticklabels(models[::-1], fontsize=8)
ax.set_xlabel("mirror bias, ambiguous scenarios (points; positive = sides with the narrator)", fontsize=8)
ax.tick_params(axis="x", labelsize=8)
ax.legend(fontsize=7, loc="lower right", frameon=False)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(OUT / "fig1_mirror_bias.png", dpi=200)

# Figure 2: any fault admitted per draft, ambiguous, 'write it for me' (tables_v2.md)
F = {"gemma-4-31b-it": {"deepseek": (38, 28, 49), "gemma": (43, 35, 51)},
     "gemma-4-26b-a4b-it": {"deepseek": (40, 30, 51), "gemma": (48, 40, 56)},
     "glm-5.3-flash": {"deepseek": (79, 70, 88), "gemma": (78, 72, 85)},
     "qwen3.8-27b": {"deepseek": (76, 66, 85), "gemma": (78, 72, 85)}}
fig, ax = plt.subplots(figsize=(6.6, 2.8))
for i, m in enumerate(models):
    for k, o in (("deepseek", 0.1), ("gemma", -0.1)):
        e, lo, hi = F[m][k]
        ax.errorbar(e, len(models) - 1 - i + o, xerr=[[e - lo], [hi - e]], fmt="o", color=C[k], capsize=2.5, ms=5, lw=1.3,
                    label=("judge " + ("deepseek-v4-flash" if k == "deepseek" else "gemma-4-31b-it")) if i == 0 else None)
ax.set_yticks(range(len(models))); ax.set_yticklabels(models[::-1], fontsize=8)
ax.set_xlim(0, 100); ax.set_xlabel("drafts admitting any fault (%), ambiguous scenarios", fontsize=8)
ax.tick_params(axis="x", labelsize=8); ax.legend(fontsize=7, loc="center left", bbox_to_anchor=(0.0, 0.5), frameon=False)
for s in ("top", "right"): ax.spines[s].set_visible(False)
fig.tight_layout(); fig.savefig(OUT / "fig2_fault_admission.png", dpi=200)
