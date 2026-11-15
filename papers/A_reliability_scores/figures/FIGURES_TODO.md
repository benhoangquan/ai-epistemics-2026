# Figures

Done:
- Figure 0, setup schematic: `figures/make_fig0.py` writes `fig0_setup.png`. No data.
- Figure 1: `figures/make_fig1.py` reads `results/E03/sim_30seeds_summary.csv` and writes `fig1_cheater_inflation_30seeds.png`. The old 10-seed `fig1_cheater_inflation.png` is kept but not used.
- Figure 2: `fig2_manifold.png`, copied from `results/E03/`.
- Figure 3: `figures/make_fig3.py` reads `results/E03/sim_recal_summary.csv` and writes `fig3_recalibration.png` (IG-SUM and EB0-IG, raw, logistic and isotonic baselines, three worlds).

Run from the repo root: `uv run --frozen python -I papers/A_reliability_scores/figures/make_fig3.py`.
