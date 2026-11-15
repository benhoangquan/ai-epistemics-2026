"""Figure 0: one-panel setup schematic. No data. Writes fig0_setup.png next to this script."""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

HERE = os.path.dirname(os.path.abspath(__file__))
fig, ax = plt.subplots(figsize=(10, 3.4))
ax.set_xlim(0, 100); ax.set_ylim(0, 34); ax.axis("off")
def box(x, w, text, fc="#eef2f7", ec="#334", y=9, h=16):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.3,rounding_size=1.2", fc=fc, ec=ec, lw=1.2))
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=8.2)
def arrow(x0, x1, y=17):
    ax.annotate("", xy=(x1, y), xytext=(x0, y), arrowprops=dict(arrowstyle="->", lw=1.4))
box(1, 14, "Event pool\n3,000 events\n5 topics")
box(19, 15, "Crowd prior\nrecorded before\nany claim")
box(38, 24, "Cheater sees prior and topic\nand chooses\nwhich events (selection logits)\nwhat probability (alpha, beta)\nhow many (10 to 1,000)", fc="#fde9d9", ec="#a43")
box(66, 12, "Outcomes\nresolve")
box(82, 17, "13 rules score\nthe claims.\nPercentile among\n200 honest sources\n= reward")
for a, b in [(15.6, 18.4), (34.6, 37.4), (62.6, 65.4), (78.6, 81.4)]: arrow(a, b)
ax.annotate("", xy=(90, 8.2), xytext=(90, 8.2))
ax.text(50, 3.2, "Reward feeds back to the cross-entropy search that sets the cheater's 14 parameters.", ha="center", fontsize=8.5, color="#444")
ax.text(50, 30, "Setup of the learned-cheater audit", ha="center", fontsize=11, weight="bold")
out = os.path.join(HERE, "fig0_setup.png")
fig.savefig(out, dpi=170, bbox_inches="tight")
print("wrote", out)
