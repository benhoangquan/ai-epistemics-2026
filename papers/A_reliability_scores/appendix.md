# Appendix (not counted in the 8 pages)

## A. Limitations and Dual-Use / Ethical Considerations

### Limitations and threats to validity

- **Simulation assumptions.** The world is Gaussian in log-odds. Honest sources pick events uniformly at random and are calibrated, except in condition R1. The crowd is calibrated, except in R2. The cheater sees only the crowd prior and the topic. With richer public features, or if honest sources also select, absolute rules become noisier. The theory for crowd-relative rules is unchanged.
- **The optimizer gives a lower bound.** The cross-entropy method finds exploits. It cannot prove that none exist. BSS ranged from 39.2 to 89.4 across 30 seeds. The EB0-IG cheater ended slightly below copy-the-crowd, so it was under-optimized. About five times more search did not change any verdict.
- **Reward choice.** The cheater maximizes expected percentile. A winner-take-all objective would favour variance more.
- **Empirical-Bayes constants.** The method-of-moments variance estimate hit its floor (complete pooling) in 38.5% of worlds for Brier and 7.5% for information gain. A better estimator could change the EB-BRIER and EB-IG numbers. It does not change EB0-IG.
- **Population statistics.** Topic means and shrinkage constants are fit on honest sources only. One cheater among 200 barely moves them.
- **Manifold data.** The money is play money. A bet is not a stated belief, so we use the post-bet price as the stated probability. Information gain there measures market impact, which scales with bet size. The sample is popularity-biased: it comes from the top 1,500 resolved binary markets, with 20 to 500 bettors. Topics come from a crude keyword match. There is no ground-truth skill, so the data show stability and signatures, not which rule is right. The share of claims on near-certain favourites is a correlational signature, not proof of intent. Crowd-relative rules are too noisy to rank individual users at 20 or more claims (split-half rho about 0.07).
- **Biased baseline and recalibration.** Every crowd-relative rule fails under R2. A logistic recalibration closes the gap, but only because the injected bias is logistic. Isotonic recalibration fails. The R2tail test was too mild to stress the logistic fit. No hand-crafted attack on the fit was run beyond the learned cheater. The real-ledger backtest of recalibration was negative, because the crowd's bias drifts. The simulated fix assumes a stationary bias.
- **LLM pundit.** 223 calls, two models from one family, 2 world pairs each, 3 to 4 held-out runs per rule, a simulated world. Deepseek was dropped because its reasoning exhausted the token limit.
- **Pilot status.** The study ran on 14 to 15 November 2026. The main and R2 conditions use 30 seeds. The other conditions use 10 (pilot) or 30 (recalibration). Exploratory conditions (R1, R2, R2tail, R3, the 5x search budget, the recalibration, the higher-volume stability, the backtest, the LLM check and the sensitivity runs) were not pre-registered. BRIER-GAIN was added post hoc.

### Dual use

The learned policies are recipes for gaming reliability leaderboards: cherry-picking, low-volume ratio-gaming, shrink-to-mean entry and baseline recalibration with flooding. We mitigate this in four ways.

1. We report each attack together with a rule that resists it, which favours defenders.
2. The attacks are simple and use only public information (the crowd prior and the topic). They need no access to a platform's internals.
3. We publish no per-user labels. Manifold user ids are hashed in the derived ledger, and the gaming signature is reported only as an aggregate.
4. We do not name or accuse any individual user or account.

A platform that adopts a rule from this paper should still test it with a learned attacker. A rule that passes our audit is not proven safe.

### Ethical considerations

The data are public Manifold Markets API responses, collected at no more than about 3 requests per second, below the documented limit of 500 per minute per IP. We did not use tokens or private data. We store the raw cache locally and do not release it, because it contains Manifold user ids. No human subjects were recruited and no personal data beyond public pseudonymous bet histories were used.

## B. Disclosure of prior work

All code in this project was written during the sprint, on 14 to 15 November 2026. No code from before the sprint is used. The swarm-alignment-2026 repository is not used. 

## C. AI-tool use statement

Language models and coding agents were used for code, analysis and drafting. The team is responsible for all content, including every number and reference. We opened and checked each cited work (see `references.md`).

## D. Extra tables

**Table A1. Learned-cheater percentile for all 13 rules, 30 seeds, main and R2.** Mean [95% CI over seeds], seed range. Hand-coded and copy-the-crowd columns are from the 10-seed pilot. Source: `results/E03/sim_30seeds_summary.csv`, `sim_summary.csv`.

| rule | main, 30 seeds | main seed range | R2, 30 seeds | R2 seed range | best hand-coded, main, 10 seeds (percentile) | copy the crowd, main, 10 seeds |
|---|---|---|---|---|---|---|
| ACC | 98.9 [98.8, 99.0] | 97.9 to 99.4 | 99.2 [99.2, 99.3] | 98.9 to 99.6 | cherry+extremize (99.1) | 32.6 |
| BRIER | 99.8 [99.8, 99.9] | 99.4 to 99.9 | 99.9 [99.8, 99.9] | 99.5 to 100.0 | cherry-pick (99.8) | 29.5 |
| LOG | 99.9 [99.8, 99.9] | 99.5 to 100.0 | 99.9 [99.8, 99.9] | 98.4 to 100.0 | cherry-pick (99.8) | 29.2 |
| DW-ACC | 98.2 [97.9, 98.4] | 96.2 to 99.2 | 98.5 [98.2, 98.7] | 95.0 to 99.1 | cherry+extremize (99.0) | 29.6 |
| DW-BRIER | 99.7 [99.6, 99.8] | 98.0 to 100.0 | 99.8 [99.8, 99.9] | 99.2 to 100.0 | cherry-pick (99.9) | 24.3 |
| TOPIC-BRIER | 99.8 [99.7, 99.8] | 99.1 to 100.0 | 99.6 [99.5, 99.8] | 98.6 to 100.0 | cherry-pick (99.3) | 29.3 |
| EB-BRIER | 100.0 [100.0, 100.0] | 100.0 to 100.0 | 100.0 [100.0, 100.0] | 100.0 to 100.0 | cherry-pick (99.9) | 27.2 |
| BSS | 72.5 [68.9, 75.7] | 39.2 to 89.4 | 76.9 [73.0, 80.8] | 54.1 to 93.7 | low-vol-gamble (20.2) | 13.1 |
| IG | 27.8 [25.6, 29.9] | 16.5 to 40.3 | 40.5 [38.5, 42.5] | 29.9 to 51.3 | low-vol-gamble (17.3) | 12.3 |
| EB-IG | 41.9 [41.4, 42.3] | 38.4 to 44.3 | 42.6 [41.7, 43.4] | 36.4 to 48.4 | low-vol-gamble (23.3) | 8.1 |
| EB0-IG | 11.3 [10.9, 11.8] | 8.7 to 13.5 | 46.1 [44.7, 47.5] | 38.1 to 56.5 | copy-crowd (12.3) | 12.3 |
| IG-SUM | 11.5 [10.9, 11.9] | 6.9 to 13.6 | 81.1 [80.3, 81.8] | 75.5 to 84.7 | copy-crowd (12.3) | 12.3 |
| BRIER-GAIN* | 21.7 [19.9, 23.5] | 12.3 to 30.2 | 27.8 [26.0, 29.6] | 19.0 to 41.0 | low-vol-gamble (17.3) | 13.1 |

**Table A2. Robustness: learned-cheater percentile by condition (10-seed pilot).** Mean [95% CI over 10 seeds]. Source: `results/E03/sim_summary.csv`, conditions `main`, `R1`, `R2`, `R3`, `main_strong`. R1: miscalibrated honest sources. R2: crowd with longshot bias. R3: minimum 30 claims. Strong: about 5x the search budget.

| rule | main | R1 | R2 | R3 | main, strong search |
|---|---|---|---|---|---|
| ACC | 98.9 [98.7, 99.0] | 98.9 [98.8, 99.0] | 99.3 [99.2, 99.4] | 100.0 [99.9, 100.0] | 98.8 [98.4, 99.0] |
| BRIER | 99.8 [99.7, 99.9] | 99.7 [99.6, 99.8] | 99.9 [99.9, 99.9] | 100.0 [100.0, 100.0] | 99.9 [99.8, 99.9] |
| BSS | 69.4 [59.9, 77.5] | 73.8 [70.5, 77.2] | 74.5 [67.0, 81.5] | 44.7 [39.8, 48.9] | 73.8 [69.2, 78.4] |
| IG | 27.3 [23.6, 30.9] | 28.3 [25.5, 31.4] | 40.2 [37.1, 43.7] | 11.6 [10.2, 13.2] | 25.3 [22.1, 28.5] |
| EB-IG | 41.2 [40.4, 41.9] | 43.2 [42.4, 44.1] | 42.8 [41.4, 44.3] | 32.3 [31.7, 32.8] | 42.0 [41.4, 42.5] |
| EB0-IG | 10.8 [10.2, 11.5] | 20.3 [19.6, 21.0] | 46.0 [43.9, 48.0] | 6.7 [6.1, 7.2] | 9.2 [7.5, 10.8] |
| IG-SUM | 10.7 [9.6, 11.7] | 20.1 [19.5, 20.7] | 81.9 [80.7, 83.0] | 7.0 [6.6, 7.3] | 10.8 [10.0, 11.5] |
| BRIER-GAIN* | 19.9 [17.4, 22.4] | 21.3 [18.2, 24.5] | 28.1 [25.2, 31.6] | 9.7 [8.8, 10.7] | 19.6 [17.5, 21.5] |

**Table A3. Split-half rank stability on Manifold, all 13 rules, three minimum claim counts.** Spearman rho [95% bootstrap CI over users]. Sources: `results/E03/real_stability_main.csv`, `real_min50/real_stability_main.csv`, `real_min100/real_stability_main.csv`.

| rule | min 20 random (n=1,855) | min 20 early vs late | min 50 random (n=488) | min 50 early vs late | min 100 random (n=112) | min 100 early vs late |
|---|---|---|---|---|---|---|
| ACC | 0.35 [0.32, 0.38] | 0.32 [0.28, 0.36] | 0.47 [0.42, 0.52] | 0.46 [0.39, 0.53] | 0.67 [0.57, 0.76] | 0.63 [0.48, 0.73] |
| DW-ACC | 0.23 [0.19, 0.25] | 0.19 [0.15, 0.23] | 0.33 [0.28, 0.39] | 0.32 [0.23, 0.40] | 0.54 [0.42, 0.65] | 0.52 [0.36, 0.64] |
| BRIER | 0.10 [0.04, 0.12] | 0.10 [0.05, 0.14] | 0.18 [0.11, 0.24] | 0.18 [0.10, 0.27] | 0.35 [0.15, 0.46] | 0.34 [0.15, 0.52] |
| LOG | 0.10 [0.05, 0.12] | 0.09 [0.05, 0.14] | 0.18 [0.11, 0.24] | 0.18 [0.09, 0.26] | 0.33 [0.13, 0.44] | 0.32 [0.13, 0.49] |
| DW-BRIER | 0.04 [-0.01, 0.07] | 0.06 [0.01, 0.10] | 0.10 [0.03, 0.17] | 0.10 [0.02, 0.18] | 0.29 [0.10, 0.38] | 0.23 [0.06, 0.40] |
| TOPIC-BRIER | 0.09 [0.04, 0.11] | 0.09 [0.05, 0.14] | 0.16 [0.09, 0.23] | 0.17 [0.09, 0.26] | 0.33 [0.13, 0.45] | 0.32 [0.14, 0.51] |
| EB-BRIER | 0.12 [0.07, 0.14] | 0.12 [0.07, 0.17] | 0.20 [0.12, 0.27] | 0.18 [0.10, 0.27] | 0.37 [0.16, 0.47] | 0.35 [0.15, 0.53] |
| BSS | 0.07 [0.04, 0.12] | 0.06 [0.01, 0.11] | 0.16 [0.10, 0.24] | 0.10 [0.01, 0.19] | 0.39 [0.25, 0.53] | 0.22 [0.05, 0.39] |
| IG | 0.07 [0.04, 0.12] | 0.07 [0.02, 0.11] | 0.18 [0.11, 0.26] | 0.12 [0.02, 0.20] | 0.39 [0.23, 0.53] | 0.18 [0.00, 0.37] |
| EB-IG | 0.10 [0.07, 0.14] | 0.07 [0.01, 0.11] | 0.20 [0.13, 0.28] | 0.11 [0.01, 0.20] | 0.39 [0.23, 0.52] | 0.16 [-0.02, 0.36] |
| EB0-IG | 0.10 [0.07, 0.14] | 0.07 [0.01, 0.11] | 0.20 [0.14, 0.28] | 0.11 [0.01, 0.20] | 0.40 [0.24, 0.53] | 0.17 [-0.02, 0.35] |
| IG-SUM | 0.10 [0.07, 0.15] | 0.06 [0.01, 0.11] | 0.21 [0.14, 0.28] | 0.11 [0.01, 0.20] | 0.41 [0.24, 0.53] | 0.15 [-0.04, 0.35] |
| BRIER-GAIN* | 0.08 [0.05, 0.12] | 0.07 [0.02, 0.11] | 0.17 [0.11, 0.25] | 0.11 [0.01, 0.19] | 0.40 [0.25, 0.53] | 0.23 [0.05, 0.40] |

The random-split CI is bootstrapped over 5 of the 20 splits. Heavy users are a selected subset. At minimum 100 claims the early-against-late CIs for IG, EB-IG, EB0-IG and IG-SUM reach 0.

**Table A4. Transfer, selected rows.** Percentile under each scoring rule for a cheater trained on a different rule. Source: `results/E03/sim_transfer_main.csv`.

| trained on | scored by ACC | BRIER | BSS | IG | EB0-IG | IG-SUM |
|---|---|---|---|---|---|---|
| ACC | 98.9 | 98.8 | 35.9 | 13.3 | 9.9 | 9.7 |
| BSS | 95.3 | 91.9 | 69.4 | 18.3 | 12.2 | 12.1 |

**Table A5. Learned policies and baseline error under recalibration (R2, IG-SUM).** Source: `results/E03/sim_recal_policies.csv` (median over seeds) and `sim_recal_summary.csv`, column `cal_err_baseline` (mean absolute error of the baseline against the true probability).

| baseline | claims | alpha | baseline error |
|---|---|---|---|
| raw crowd | 990.9 | 1.30 | 0.044 |
| logistic | 41.2 | 1.44 | 0.012 |
| isotonic | 983.5 | 1.34 | 0.032 |

**Table A6. Real-ledger backtest of a recalibrated baseline.** Mean log2 score of the baseline on 126,526 eligible claims (blocks 1 to 3). Source: `results/E03/real_recal_summary.json`, `baseline_mean_log2score_eligible_claims`.

| baseline | all blocks | block 1 | block 2 | block 3 |
|---|---|---|---|---|
| raw price | -0.790 | -0.795 | -0.846 | -0.731 |
| logistic | -0.832 | -0.783 | -0.940 | -0.774 |
| isotonic | -0.833 | -0.784 | -0.941 | -0.776 |

Fitted logistic slope and intercept by block: 0.93 and -0.07; 0.93 and -0.70; 0.86 and -0.37.

**Table A7. LLM pundit, by model.** Held-out percentile (n = held-out runs). Source: `results/E03/llm_pundit_summary.csv`.

| rule | gemma-4-31b-it | gemma-4-26b-a4b-it |
|---|---|---|
| ACC | 98.4 (n=2) | 99.1 (n=2) |
| BRIER | 99.3 (n=2) | 98.8 (n=2) |
| IG | 1.0 (n=1) | 0.5 (n=2) |
| IG-SUM | 5.3 (n=2) | 5.3 (n=2) |
| BSS | 12.5 (n=2) | 15.0 (n=2) |

Pooled over both models, held-out percentile [CI] and n: ACC 98.75 [98.31, 99.44] (4); BRIER 99.0 [98.62, 99.38] (4); IG 0.67 [0.0, 1.0] (3); IG-SUM 5.25 [1.75, 8.75] (4); BSS 13.75 [7.25, 20.62] (4). Source: rows `model == both`.

**Table A8. Learned-cheater percentile, crowd-relative rules, main against R2.** Mean [95% CI over 30 seeds].

| rule | main | R2 (crowd with longshot bias) |
|---|---|---|
| BSS | 72.5 [68.9, 75.7] | 76.9 [73.0, 80.8] |
| IG | 27.8 [25.6, 29.9] | 40.5 [38.5, 42.5] |
| EB-IG | 41.9 [41.4, 42.3] | 42.6 [41.7, 43.4] |
| EB0-IG | 11.3 [10.9, 11.8] | 46.1 [44.7, 47.5] |
| IG-SUM | 11.5 [10.9, 11.9] | 81.1 [80.3, 81.8] |
| BRIER-GAIN* | 21.7 [19.9, 23.5] | 27.8 [26.0, 29.6] |
