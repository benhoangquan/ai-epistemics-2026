# TODO after pass 2

All E03 results listed in `results/E03/new_results.md` are now in the paper. No `[[PENDING]]` markers remain (`grep -c PENDING paper.md appendix.md` gives 0).

Open items, none blocking:
- Fill `[AUTHORS: confirm]` (owner: team).
- Paste into the official Google Doc template and check the 8-page limit. The body is about 4,100 words including tables and captions, with 3 body tables (1, 2, 4) and 4 figures. If it still runs over, shrink Figure 0 or drop Table 1's family column first.
- Figures 0 to 3 are final: `figures/make_fig0.py`, `make_fig1.py` (30 seeds), `make_fig3.py`. Run from the repo root with `uv run --frozen python -I`. Fig 2 is the original E03 plot.
- Re-check the Metaculus Scores FAQ if the team wants to cite it (fetches returned 403; currently not cited).
- Optional experiments, not run, named as future work in Section 9: a stronger misspecified bias, a hand-crafted attack on the recalibration fit, a drift-tracking baseline, Metaculus data, a GRPO pundit.
- Video, slides and public repo are optional in the sprint rules and not prepared here.
