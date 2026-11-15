# Numbers in the paper.md text, with exact values and sources

Part 1 below is the 10-seed pilot (`sim_summary.csv`). Rows A1 to A11 are still used for the hand-coded and copy-the-crowd columns and for the pilot-only statements (A14 to A23, R-rows). Where paper.md quotes a 30-seed value, see Part 2 ("Pass 2 additions") at the end. R1 to R3 rows for R2 refer to the pilot unless stated.

Paths are under `/home/ben/remote-work/ai-epistemics-2026/`. "SS" = `results/E03/sim_summary.csv`, columns `learned_pct, ci_lo, ci_hi, seed_min, seed_max, beat_median_share, best_handcoded_pct, copy_crowd_pct, skill_rho_main`, selected by `cond` and `rule`. "README" = `experiments/E03_track_record/README.md` (design constants live in section 3 and in code; no results file stores them). Exact values are unrounded as stored (2 decimals in the CSV).

## Design constants (S)
| id | text value | exact | source |
|---|---|---|---|
| S1 | 13 rules | 13 | SS, distinct `rule`; README section 3 |
| S2 | 200 honest sources per world | 200 | README section 3 |
| S3 | 3,000 events, 5 topics | 3000; 5 | README section 3 |
| S4 | topic mean log-odds -2.5 to 2.5; base rates about 8% to 92% | -2.5..2.5 | README section 3 |
| S5 | skill k from 0.1 to 0.9; median k near 0.5; volume 10 to 500 | U(0.1,0.9); log-uniform(10,500) | README section 3 |
| S6 | 10 hand-coded cheats | 10 | `results/E03/sim_handcoded.csv`, distinct `strategy` is 10 (README lists 10) |
| S7 | cheater 14 parameters; 6 confidence bins; 5 topics; volume 10 to 1,000 | 14; 6; 5; 10..1000 | README section 3; `sim_learned_policies.csv` columns `alpha, beta`; theta length 14 in `sim_R2.json` |
| S8 | 20 fresh test worlds per seed; 10 seeds | 20; 10 | README section 5; SS `n_seeds` |
| S9 | R2 bias c' = sigmoid(0.75 x logit c); R3 minimum 30 claims | 0.75; 30 | README section 3 |
| S10 | strong run about five times more search | 80 iterations, 128 candidates, 8 worlds vs 40 x 6 x 64 | README "Deviations" |
| S11 | alpha 1.31 vs inverse bias 1.33 | 1.313; 1/0.75 = 1.3333 | `sim_learned_policies.csv`, row `cond=R2, trained_on=IG-SUM`, column `alpha` |

## Simulation results (main condition unless stated)
| id | text value | exact | source |
|---|---|---|---|
| A1 | ACC 98.9 [98.7, 99.0] | 98.85 [98.72, 98.98] | SS main/ACC |
| A2 | BRIER 99.8 [99.7, 99.9] | 99.8 [99.71, 99.87] | SS main/BRIER |
| A3 | ACC best hand-coded 99.1; copy crowd 32.6 | 99.11; 32.6 | SS main/ACC `best_handcoded_pct`, `copy_crowd_pct` |
| A4 | BRIER best hand 99.8; copy crowd 29.5 | 99.82; 29.52 | SS main/BRIER |
| A5 | BSS 69.4 [59.9, 77.5]; hand 20.2; copy 13.1; share above median 0.67; rho 0.53 | 69.43 [59.93, 77.52]; 20.24; 13.07; 0.67; 0.53 | SS main/BSS |
| A6 | BSS seed range 39 to 89 | 39.15 to 89.42 | SS main/BSS `seed_min`, `seed_max` |
| A7 | IG 27.3 [23.6, 30.9]; hand 17.3; copy 12.3; share 0.33; rho 0.55 | 27.32 [23.62, 30.88]; 17.3; 12.34; 0.33; 0.55 | SS main/IG |
| A8 | EB-IG 41.2 [40.4, 41.9]; hand 23.3; copy 8.1; share 0.15; rho 0.62 | 41.17 [40.43, 41.89]; 23.28; 8.13; 0.15; 0.62 | SS main/EB-IG |
| A9 | EB0-IG 10.8 [10.2, 11.5]; hand 12.3; copy 12.3; share 0.00; rho 0.46 | 10.84 [10.21, 11.48]; 12.34; 12.34; 0.0; 0.46 | SS main/EB0-IG |
| A10 | IG-SUM 10.7 [9.6, 11.7]; hand 12.3; share 0.00; rho 0.37 | 10.7 [9.63, 11.71]; 12.34; 0.0; 0.37 | SS main/IG-SUM |
| A11 | BRIER-GAIN 19.9 [17.4, 22.4]; hand 17.3; copy 13.1; share 0.17; rho 0.53 | 19.88 [17.38, 22.36]; 17.31; 13.07; 0.17; 0.53 | SS main/BRIER-GAIN |
| A12 | "98 or higher under all seven absolute and difficulty-weighted variants" | min is DW-ACC 98.0 | SS main, rules ACC, BRIER, LOG, DW-ACC, DW-BRIER, TOPIC-BRIER, EB-BRIER (EB-BRIER is shrinkage; the sentence counts the seven Table 1 rows before BSS) |
| A13 | skill recovery absolute 0.27 to 0.41; relative 0.37 to 0.62 | 0.27,0.33,0.34,0.30,0.40,0.34,0.41; 0.53,0.55,0.62,0.46,0.37 | SS main `skill_rho_main`, same seven absolute rows; BSS, IG, EB-IG, EB0-IG, IG-SUM |
| A14 | BSS about 11 claims, all crowd at least 95%, mild extremizing | 11.0; 1.0; alpha 1.313 | `sim_learned_policies.csv` main/BSS: `n_claims`, `share_crowd_ge_0.95`, `alpha` |
| A15 | IG: 10 claims on 80 to 95% favourites, extremize hard | 10.0; share_ge_0.95 0.0; share_ge_0.8 0.907; alpha 2.972 | `sim_learned_policies.csv` main/IG |
| A16 | EB-IG: 10 claims, roughly copies crowd | 10.0; alpha 1.098 | `sim_learned_policies.csv` main/EB-IG |
| A18 | Strong search: BSS 73.8, IG 25.3, EB0-IG 9.2, IG-SUM 10.8, BRIER-GAIN 19.6 | 73.83; 25.27; 9.22; 10.77; 19.55 | SS `cond=main_strong` |
| A19 | R3: IG 11.6, EB0-IG 6.7, BSS 44.7 | 11.6; 6.67; 44.69 | SS R3 |
| A20 | Transfer: BSS-trained scores 95.3 (ACC), 91.9 (BRIER); ACC-trained 13.3 (IG), 9.9 (EB0-IG) | 95.3; 91.9; 13.3; 9.9 (1 decimal in file) | `results/E03/sim_transfer_main.csv`, rows `trained_on` BSS and ACC |
| A21 | Table A4 extras: ACC-trained BSS 35.9, IG-SUM 9.7; BSS-trained IG 18.3, EB0-IG 12.2, IG-SUM 12.1 | as shown | `sim_transfer_main.csv` |
| A22 | EB tau-squared floor 38.5% (Brier), 7.5% (IG) | 0.385; 0.075 | `sim_eb_constants.json`, `share_tau2_floored(kappa>1e6)` |
| A23 | Pre-registered signal passed; four rules below median (IG, EB-IG, EB0-IG, IG-SUM) | `signal_present` true | `killtest_sim.json` |

## Robustness and R2 (Table 3, Table A2, Section 5)
| id | text value | exact | source |
|---|---|---|---|
| R1 | R2: BSS 74.5 [67.0, 81.5]; IG 40.2 [37.1, 43.7]; EB-IG 42.8 [41.4, 44.3]; EB0-IG 46.0 [43.9, 48.0]; IG-SUM 81.9 [80.7, 83.0]; BRIER-GAIN 28.1 [25.2, 31.6] | 74.46 [67.0, 81.53]; 40.19 [37.11, 43.66]; 42.83 [41.36, 44.26]; 46.02 [43.85, 47.97]; 81.88 [80.68, 83.02]; 28.06 [25.16, 31.59] | SS cond R2 |
| R2 | Copy-the-crowd under R2 | 9.2 | SS R2/IG-SUM `copy_crowd_pct` = 9.2 |
| R3 | IG-SUM under R2: median about 994 claims | 993.5 | `sim_learned_policies.csv` R2/IG-SUM `n_claims` |
| R4 | Table A2 R1 column (EB0-IG 20.3 [19.6, 21.0], IG-SUM 20.1 [19.5, 20.7], etc.) | see file | SS cond R1 |
| R5 | Table A2 R3 and strong columns | see file | SS cond R3, main_strong |

## Real data (Section 6, Appendix)
| id | text value | exact | source |
|---|---|---|---|
| M1 | 698 markets | 698 | `results/E03/real_summary_main.json` `n_markets` |
| M2 | 168,701 claims; 28,704 users | 168701; 28704 | same, `n_claims_all_users`, `n_users_total` |
| M3 | dates 28 Dec 2021 to 12 Nov 2026 | ["2021-12-28","2026-11-12"] | same, `date_range` |
| M4 | 83,298 claims; 1,855 users | 83298; 1855 | same, `n_claims_analysed`, `n_users_analysed` |
| M5 | signature rho 0.42 [0.38, 0.45] | 0.41639 [0.37565, 0.45269] | same, `spearman_nearcertain_vs_accrank_minus_igrank`, `ci` |
| M6 | top decile by favourite share: ACC pct 86.5, IG pct 52.9 | 86.5499; 52.8841 | same, `high_near_certain_median_acc_pct`, `high_near_certain_median_ig_pct` |
| M7 | top ACC decile median IG percentile 69.9; 25.8% below median | 69.8922; 0.25806 | same, `top_acc_decile_median_ig_pct`, `top_acc_decile_share_below_median_ig` |
| M8 | no-creator signature 0.42; all-buys 0.39 | 0.41928; 0.39458 | `real_summary_main_nocreator.json`, `real_summary_main_allbuys.json`, same key |
| M9 | BRIER vs LOG rho 0.99; IG vs IG-SUM 0.98; BRIER vs IG 0.10 | 0.99; 0.975; 0.103 | `results/E03/real_rule_corr_main.csv` |
| M10 | ACC stability 0.35 random, 0.32 early-late | 0.351; 0.318 | `real_stability_main.csv` `split_half_random`, `split_half_temporal` |
| M11 | IG and BSS 0.07 | IG 0.072/0.065; BSS 0.073/0.063 | same |
| M12 | IG-SUM and EB0-IG 0.06 to 0.10 | IG-SUM 0.101/0.064; EB0-IG 0.098/0.065 | same |
| M13 | mean favourite-probability stability 0.56; with ACC 0.70; with IG -0.06 | 0.5552; 0.6961; -0.0617 | `real_summary_main.json` `selection_habit` keys |
| M14 | Appendix Table A3 | exact in file | `real_stability_main.csv` |
| M15 | Manifold rate: 3 requests per second; limit 500 per minute; 1,500 top markets; 20 to 500 bettors; 20 claims minimum | stated in README | README sections 3 and 8; docs.manifold.markets/api |

## Derived or illustrative numbers
| id | text value | derivation |
|---|---|---|
| D1 | Copy a 97% crowd: expected Brier 0.03; 50% event: 0.25 | c(1-c) = 0.0291; 0.25; formula from README section 5.4 |
| D2 | Hand-coded under-estimated by 18 and 49 points | 69.43 - 20.24 = 49.19; 41.17 - 23.28 = 17.89 (SS) |
| D3 | 87% pundit in intro | illustrative example from the README question; not a result |


# Pass 2 additions (30 seeds, recalibration, higher-volume stability, backtest, LLM pundit)

Source of the narrative and the list of files: `results/E03/new_results.md`. Exact values below are copied from the CSV or JSON by script. Table cells in paper.md are rounded to 1 decimal (stability to 2).

## N1. 30-seed summary, `results/E03/sim_30seeds_summary.csv` (columns pct, ci_lo, ci_hi, sd_over_seeds, seed_min, seed_max, beat_median_share)

| cond | rule | pct | ci_lo | ci_hi | sd | seed_min | seed_max | beat_median_share |
|---|---|---|---|---|---|---|---|---|
| main | ACC | 98.9 | 98.8 | 99.0 | 0.28 | 97.9 | 99.4 | 1.0 |
| main | BRIER | 99.83 | 99.79 | 99.86 | 0.1 | 99.44 | 99.94 | 1.0 |
| main | LOG | 99.86 | 99.83 | 99.89 | 0.09 | 99.52 | 99.99 | 1.0 |
| main | DW-ACC | 98.17 | 97.86 | 98.44 | 0.81 | 96.22 | 99.19 | 1.0 |
| main | DW-BRIER | 99.73 | 99.57 | 99.85 | 0.39 | 97.98 | 99.98 | 1.0 |
| main | TOPIC-BRIER | 99.75 | 99.67 | 99.81 | 0.2 | 99.12 | 99.98 | 1.0 |
| main | EB-BRIER | 100.0 | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 1.0 |
| main | BSS | 72.52 | 68.88 | 75.67 | 9.79 | 39.15 | 89.42 | 0.7 |
| main | IG | 27.77 | 25.55 | 29.91 | 6.05 | 16.48 | 40.26 | 0.33 |
| main | EB-IG | 41.89 | 41.41 | 42.33 | 1.33 | 38.38 | 44.27 | 0.14 |
| main | EB0-IG | 11.34 | 10.87 | 11.81 | 1.33 | 8.71 | 13.48 | 0.0 |
| main | IG-SUM | 11.46 | 10.91 | 11.95 | 1.48 | 6.91 | 13.6 | 0.0 |
| main | BRIER-GAIN | 21.7 | 19.85 | 23.53 | 5.29 | 12.33 | 30.19 | 0.2 |
| R2 | ACC | 99.24 | 99.18 | 99.31 | 0.19 | 98.94 | 99.62 | 1.0 |
| R2 | BRIER | 99.89 | 99.85 | 99.93 | 0.12 | 99.49 | 99.99 | 1.0 |
| R2 | LOG | 99.86 | 99.75 | 99.94 | 0.29 | 98.44 | 100.0 | 1.0 |
| R2 | DW-ACC | 98.47 | 98.15 | 98.73 | 0.86 | 95.01 | 99.14 | 1.0 |
| R2 | DW-BRIER | 99.81 | 99.75 | 99.86 | 0.15 | 99.25 | 99.95 | 1.0 |
| R2 | TOPIC-BRIER | 99.64 | 99.52 | 99.75 | 0.33 | 98.64 | 99.95 | 1.0 |
| R2 | EB-BRIER | 100.0 | 100.0 | 100.0 | 0.0 | 100.0 | 100.0 | 1.0 |
| R2 | BSS | 76.93 | 72.96 | 80.84 | 11.12 | 54.07 | 93.67 | 0.76 |
| R2 | IG | 40.46 | 38.45 | 42.5 | 5.73 | 29.95 | 51.32 | 0.45 |
| R2 | EB-IG | 42.59 | 41.74 | 43.43 | 2.43 | 36.39 | 48.44 | 0.42 |
| R2 | EB0-IG | 46.07 | 44.7 | 47.47 | 3.92 | 38.08 | 56.52 | 0.38 |
| R2 | IG-SUM | 81.11 | 80.32 | 81.84 | 2.16 | 75.45 | 84.67 | 0.98 |
| R2 | BRIER-GAIN | 27.76 | 26.03 | 29.58 | 5.12 | 19.01 | 41.01 | 0.28 |

Used in: abstract (98.9, 99.8, 72.5, 41.9), Table 2, Table 3, Table A1, Section 4 (BSS SD 9.8, range 39.2 to 89.4 where `seed_min` is 39.15; 21.7 for BRIER-GAIN; 33% of test worlds for IG, 0.33), Section 5 (81.1 for IG-SUM under R2), Section 8 (72.5, 21.7, 11.5, 11.3, 41.9).

## N2. Recalibration, `results/E03/sim_recal_summary.csv` (columns pct, ci_lo, ci_hi, seed_min, seed_max, beat_median_share, cal_err_raw, cal_err_baseline)

| cond | rule | pct | ci_lo | ci_hi | seed_min | seed_max | beat_median_share | cal_err_baseline |
|---|---|---|---|---|---|---|---|---|
| R2_iso | BSS | 79.142 | 74.753 | 83.096 | 39.133 | 92.275 | 0.767 | 0.032 |
| R2_iso | IG | 22.298 | 20.854 | 23.704 | 14.625 | 32.483 | 0.2 | 0.032 |
| R2_iso | EB-IG | 41.568 | 41.053 | 42.048 | 38.592 | 43.925 | 0.155 | 0.032 |
| R2_iso | EB0-IG | 42.568 | 41.078 | 44.039 | 33.583 | 50.425 | 0.326 | 0.032 |
| R2_iso | IG-SUM | 68.161 | 66.593 | 69.665 | 58.308 | 75.308 | 0.865 | 0.032 |
| R2_iso | BRIER-GAIN | 22.604 | 20.983 | 24.177 | 12.458 | 29.558 | 0.179 | 0.032 |
| R2_logit | BSS | 80.144 | 75.718 | 84.178 | 50.683 | 97.042 | 0.78 | 0.012 |
| R2_logit | IG | 25.502 | 23.302 | 27.614 | 13.758 | 34.525 | 0.277 | 0.012 |
| R2_logit | EB-IG | 40.387 | 39.892 | 40.851 | 36.25 | 42.75 | 0.092 | 0.012 |
| R2_logit | EB0-IG | 13.299 | 12.605 | 13.953 | 9.342 | 16.117 | 0.002 | 0.012 |
| R2_logit | IG-SUM | 16.227 | 14.687 | 17.989 | 9.992 | 31.842 | 0.021 | 0.012 |
| R2_logit | BRIER-GAIN | 20.889 | 19.259 | 22.457 | 12.292 | 28.467 | 0.175 | 0.012 |
| R2_none | BSS | 79.4 | 74.633 | 83.711 | 43.433 | 96.683 | 0.776 | 0.044 |
| R2_none | IG | 39.672 | 36.567 | 42.482 | 15.292 | 52.308 | 0.448 | 0.044 |
| R2_none | EB-IG | 40.342 | 39.327 | 41.425 | 35.533 | 48.05 | 0.449 | 0.044 |
| R2_none | EB0-IG | 52.283 | 50.289 | 54.164 | 38.45 | 62.642 | 0.487 | 0.044 |
| R2_none | IG-SUM | 85.238 | 84.265 | 86.138 | 77.3 | 89.483 | 0.982 | 0.044 |
| R2_none | BRIER-GAIN | 25.774 | 24.175 | 27.287 | 14.383 | 33.85 | 0.239 | 0.044 |
| R2tail_iso | BSS | 78.392 | 74.072 | 82.28 | 46.85 | 90.992 | 0.759 | 0.032 |
| R2tail_iso | IG | 23.776 | 22.134 | 25.404 | 14.792 | 35.825 | 0.222 | 0.032 |
| R2tail_iso | EB-IG | 41.499 | 40.899 | 42.123 | 38.317 | 45.642 | 0.152 | 0.032 |
| R2tail_iso | EB0-IG | 39.692 | 38.252 | 41.183 | 32.7 | 49.267 | 0.291 | 0.032 |
| R2tail_iso | IG-SUM | 64.533 | 62.789 | 66.249 | 55.25 | 71.9 | 0.813 | 0.032 |
| R2tail_iso | BRIER-GAIN | 23.217 | 22.172 | 24.27 | 17.725 | 28.217 | 0.184 | 0.032 |
| R2tail_logit | BSS | 78.3 | 73.626 | 82.41 | 44.267 | 93.958 | 0.762 | 0.014 |
| R2tail_logit | IG | 32.292 | 29.877 | 34.765 | 19.842 | 43.967 | 0.398 | 0.014 |
| R2tail_logit | EB-IG | 41.419 | 40.724 | 42.167 | 37.475 | 45.975 | 0.172 | 0.014 |
| R2tail_logit | EB0-IG | 16.597 | 15.554 | 17.637 | 11.567 | 22.508 | 0.006 | 0.014 |
| R2tail_logit | IG-SUM | 20.588 | 18.364 | 22.759 | 12.875 | 31.258 | 0.041 | 0.014 |
| R2tail_logit | BRIER-GAIN | 20.01 | 18.771 | 21.218 | 13.75 | 26.758 | 0.164 | 0.014 |
| R2tail_none | BSS | 75.521 | 70.089 | 80.358 | 41.733 | 93.975 | 0.731 | 0.004 |
| R2tail_none | IG | 35.43 | 33.23 | 37.584 | 23.375 | 46.767 | 0.442 | 0.004 |
| R2tail_none | EB-IG | 41.544 | 40.671 | 42.458 | 36.683 | 47.375 | 0.334 | 0.004 |
| R2tail_none | EB0-IG | 18.702 | 16.98 | 20.493 | 7.683 | 31.717 | 0.028 | 0.004 |
| R2tail_none | IG-SUM | 24.519 | 21.504 | 27.689 | 12.167 | 43.175 | 0.105 | 0.004 |
| R2tail_none | BRIER-GAIN | 21.518 | 20.102 | 23.001 | 15.542 | 31.758 | 0.19 | 0.004 |
| main_iso | BSS | 71.041 | 67.223 | 74.619 | 41.042 | 85.433 | 0.678 | 0.031 |
| main_iso | IG | 24.128 | 22.711 | 25.545 | 15.5 | 34.675 | 0.229 | 0.031 |
| main_iso | EB-IG | 41.546 | 41.055 | 42.036 | 38.9 | 43.917 | 0.143 | 0.031 |
| main_iso | EB0-IG | 41.228 | 38.9 | 43.255 | 19.35 | 50.125 | 0.312 | 0.031 |
| main_iso | IG-SUM | 65.84 | 64.472 | 67.139 | 55.592 | 72.817 | 0.838 | 0.031 |
| main_iso | BRIER-GAIN | 21.918 | 20.279 | 23.617 | 13.683 | 30.467 | 0.176 | 0.031 |
| main_logit | BSS | 73.521 | 69.237 | 77.273 | 41.858 | 86.292 | 0.707 | 0.012 |
| main_logit | IG | 27.57 | 25.71 | 29.518 | 19.192 | 38.525 | 0.324 | 0.012 |
| main_logit | EB-IG | 40.169 | 39.511 | 40.752 | 35.192 | 42.758 | 0.112 | 0.012 |
| main_logit | EB0-IG | 13.743 | 12.763 | 14.768 | 8.492 | 21.967 | 0.002 | 0.012 |
| main_logit | IG-SUM | 15.513 | 13.955 | 17.312 | 7.792 | 30.05 | 0.015 | 0.012 |
| main_logit | BRIER-GAIN | 20.838 | 19.147 | 22.584 | 12.208 | 34.633 | 0.179 | 0.012 |
| main_none | BSS | 72.289 | 67.459 | 76.684 | 39.642 | 86.342 | 0.694 | 0.0 |
| main_none | IG | 27.803 | 25.932 | 29.712 | 17.55 | 36.583 | 0.329 | 0.0 |
| main_none | EB-IG | 39.916 | 39.105 | 40.638 | 33.55 | 43.542 | 0.092 | 0.0 |
| main_none | EB0-IG | 13.279 | 12.654 | 13.881 | 9.517 | 16.8 | 0.0 | 0.0 |
| main_none | IG-SUM | 13.778 | 12.9 | 14.608 | 7.733 | 17.908 | 0.001 | 0.0 |
| main_none | BRIER-GAIN | 21.835 | 19.961 | 23.805 | 12.583 | 31.967 | 0.197 | 0.0 |

Used in: abstract (16, 68), Table 4, Figure 3, Section 5.1 (85.2 [84.3, 86.1] to 16.2 [14.7, 18.0]; EB0-IG 52.3 to 13.3; worst IG-SUM seed 31.8 = `seed_max` of R2_logit/IG-SUM 31.842; 15.5 vs 13.8; 68.2 [66.6, 69.7]; 65.8 [64.5, 67.1]; R2tail raw IG-SUM 24.5; BSS 71 to 80 = range of BSS `pct` across all nine rows, 71.0 to 80.1; EB-IG 40 to 42 per the `new_results.md` statement), Section 8.

## N3. Recalibration policies and baseline error

`results/E03/sim_recal_policies.csv`, IG-SUM rows (columns alpha, beta, n_claims): R2_none 1.3 / 990.9; R2_logit 1.44 / 41.2; R2_iso 1.34 / 983.54; main_iso claims about 980 per `new_results.md` finding 3. Baseline error `cal_err_baseline` in `sim_recal_summary.csv`: logistic 0.012, isotonic 0.032 (0.031 in main), raw R2 0.044. In text: 0.031 and 0.012 as quoted in `new_results.md`, "about 990 claims" and "about 41".

## N4. Manifold higher volume

- Users and claims: min 50: 488 users, 42,336 claims; min 100: 112 users, 17,077 claims (`results/E03/real_min50/real_summary_main.json`, `real_min100/real_summary_main.json`, keys `n_users_analysed`, `n_claims_analysed`).
- Stability: `real_min50/real_stability_main.csv`, `real_min100/real_stability_main.csv`, columns `split_half_random`, `split_half_temporal`, and CI columns. Table A3 is generated from them. Text values: crowd-relative random split 0.16 to 0.21 (min 50); about 0.40 (min 100); ACC 0.47 and 0.67; early-late 0.15 to 0.23 at min 100.
  - real_min50 ACC: random 0.474, temporal 0.46 [0.393, 0.527]
  - real_min50 BSS: random 0.164, temporal 0.105 [0.01, 0.187]
  - real_min50 IG: random 0.178, temporal 0.115 [0.019, 0.197]
  - real_min50 EB-IG: random 0.205, temporal 0.113 [0.011, 0.204]
  - real_min50 EB0-IG: random 0.205, temporal 0.114 [0.015, 0.205]
  - real_min50 IG-SUM: random 0.209, temporal 0.111 [0.01, 0.204]
  - real_min50 BRIER-GAIN: random 0.172, temporal 0.107 [0.012, 0.19]
  - real_min100 ACC: random 0.671, temporal 0.626 [0.481, 0.734]
  - real_min100 BSS: random 0.39, temporal 0.218 [0.046, 0.388]
  - real_min100 IG: random 0.39, temporal 0.185 [0.004, 0.369]
  - real_min100 EB-IG: random 0.392, temporal 0.164 [-0.018, 0.356]
  - real_min100 EB0-IG: random 0.399, temporal 0.165 [-0.019, 0.355]
  - real_min100 IG-SUM: random 0.405, temporal 0.152 [-0.039, 0.348]
  - real_min100 BRIER-GAIN: random 0.4, temporal 0.229 [0.049, 0.404]
- real_min50 signature: 0.5240810590647789 [0.465195172009802, 0.5843994486408999]; users 488, claims 42336
- real_min100 signature: 0.564670103917629 [0.3911051221848886, 0.6734280091832427]; users 112, claims 17077

## N5. Real-ledger backtest, `results/E03/real_recal_summary.json`

- `n_claims_eligible` 126526; `baseline_mean_log2score_eligible_claims`: raw -0.7903714339923377, logit -0.832438036662046, iso -0.8333873368318114; by block raw {'1': -0.7946696456857981, '2': -0.8456164885318476, '3': -0.7308295795401485}, logit {'1': -0.7832990096839408, '2': -0.9401297037817439, '3': -0.7738867848133245}, iso {'1': -0.7837626547401823, '2': -0.9407415046711198, '3': -0.7756592198598751}.
- `fit`: {"logit_block1": {"n_fit": 19103, "slope": 0.934, "intercept": -0.072}, "logit_block2": {"n_fit": 64116, "slope": 0.932, "intercept": -0.697}, "logit_block3": {"n_fit": 112340, "slope": 0.863, "intercept": -0.371}}
- variant raw min 20: n_users 1394, IG_temp 0.06420785505587961 [0.005618182079894052, 0.11046564628547548], pop_mean_IG_bits -0.0005899317025723995
- variant logit min 20: n_users 1394, IG_temp 0.010665157934014832 [-0.034896010235256035, 0.057683397058004876], pop_mean_IG_bits 0.0452638947073612

Text values: -0.832 vs -0.790; 0.93/-0.07 to 0.86/-0.37; IG early-late 0.064 raw, 0.011 logistic; 126,526 claims. Used in Section 5? no: Section 6, Section 8, Table A6.

## N6. LLM pundit, `results/E03/llm_pundit_summary.csv` rows `model == both`

- ACC: n_heldout 4, B_pct 98.75 [98.31, 99.44], range 98.25 to 99.75, share above 50 1.0
- BRIER: n_heldout 4, B_pct 99.0 [98.62, 99.38], range 98.5 to 99.5, share above 50 1.0
- IG: n_heldout 3, B_pct 0.67 [0.0, 1.0], range 0.0 to 1.0, share above 50 0.0
- IG-SUM: n_heldout 4, B_pct 5.25 [1.75, 8.75], range 0.5 to 10.0, share above 50 0.0
- BSS: n_heldout 4, B_pct 13.75 [7.25, 20.62], range 5.5 to 24.5, share above 50 0.0
- 223 calls, 2 models, 2 world pairs each: `new_results.md` item 6 (`python -m epi.llm` output quoted there). Not in a CSV.

## N7. Design constants traced to code

- 3,000 events, 200 honest sources, skill U(0.1, 0.9), volume log-uniform up to 500: `experiments/E03_track_record/sim.py`, `make_world(rng, cond, n_events=3000, n_honest=200)` and lines drawing `k` and `n`. 5 topics: README section 3 (constant `N_TOPICS` in sim.py).
- 14 parameters: length of `theta` in each entry of `results/E03/sim_R2.json` (`learned.<rule>.theta`), 14 entries.
- 20 test worlds per seed, CEM budget: README section 3 and "Deviations" (code: `sim.py`).
- 30 seeds, 4 blocks of 750 events, claims in blocks 1 to 3 (2,250 events): `new_results.md` Item 1 design.

## N8. Derived

- Hand-coded under-estimates: 72.52 - 20.24 = 52.3 (BSS, 30-seed vs pilot hand-coded) and 41.9 - 23.28 = 18.6 (EB-IG), quoted as 52 and 19.
- "3.1 points or less" (Figure 1 note): largest gap between pilot (`sim_summary.csv`) and 30-seed (`sim_30seeds_summary.csv`) learned percentile among the 8 Table 2 rules is BSS, 72.52 - 69.43 = 3.09.
- "seven rules score 98 or higher": min of ACC, BRIER, LOG, DW-ACC, DW-BRIER, TOPIC-BRIER, EB-BRIER at 30 seeds is DW-ACC 98.2.

## Pass 3 changes (cleanup)
- Figure 1 is now `figures/fig1_cheater_inflation_30seeds.png`, made by `figures/make_fig1.py` from `results/E03/sim_30seeds_summary.csv`, conditions main and R2, columns `pct`, `ci_lo`, `ci_hi`. Values are those in N1.
- Table 2 hand-coded and copy-the-crowd columns remain 10-seed pilot values (rows A3 to A11), because `sim_30seeds_summary.csv` has no such columns. The caption says so.
- New text numbers in Section 5: EB0-IG 46.1 and IG 40.5 under R2 (N1, rows R2/EB0-IG and R2/IG, `pct`).
- Table 3 moved to Appendix Table A8 and Table 5 content is in Appendix Table A3. No numbers were added or changed.

## Review round, pass 1 (changes to paper.tex)
- Abstract: "2,250-event subset" and "85th" (raw R2 baseline IG-SUM 85.2): `results/E03/sim_recal_summary.csv`, cond R2_none, rule IG-SUM, `pct` 85.238. Eligible events 2,250: `sim_recal.py` line 75 to 82 (blocks 1 to 3 of 4 x 750). "Spearman rho = 0.42": `real_summary_main.json` `spearman_nearcertain_vs_accrank_minus_igrank` 0.41639.
- Section 3.4 additions: 700 markets sampled, 698 kept: `fetch_stats.json` `markets_sampled`, `real_summary_main.json` `n_markets`; top 1,500 and 20 to 500 bettors: README sections 3 and 8; 2 truncated: `real_summary_main.json` `markets_skipped.truncated`.
- Section 4.1: "11.3 against 12.3 for EB0-IG": `sim_30seeds_summary.csv` main/EB0-IG `pct` 10.84 in the pilot, 11.3 at 30 seeds; copy-crowd 12.34 in `sim_summary.csv` `copy_crowd_pct`; "9.2 with five times more search": `sim_summary.csv` main_strong/EB0-IG 9.22.
- Section 4.2: "27.8" IG and "21.7" BRIER-GAIN: `sim_30seeds_summary.csv` main. "N = 10 claims" for the IG gamble: `sim_learned_policies.csv` main/IG `n_claims` 10. 0.029: 0.97 x 0.03 = 0.0291 (derived).
- Section 4.3: 0.031 (main isotonic) and 0.032 (R2 isotonic): `sim_recal_summary.csv` `cal_err_baseline`, rows main_iso and R2_iso.
- Section 4.4: block-2 intercept -0.70 and block-3 slope 0.86: `real_recal_summary.json` `fit.logit_block2.intercept` -0.6969, `fit.logit_block3.slope` 0.8629.
- Section 4.5: min to max per rule: `llm_pundit_log.csv`, rows `stage == B_heldout` (computed per run: ACC 98.2 to 99.8, BRIER 98.5 to 99.5, IG 0.0 to 1.0, IG-SUM 0.5 to 10.0, BSS 5.5 to 24.5). 4,000-token limit: `llm_pundit.py` lines 37, 129, 140, 152.
- Section 4.6: skill recovery 0.27 to 0.41 and 0.37 to 0.62: `sim_summary.csv` `skill_rho_main`, main condition (same rows as A13). "27.3 to 11.6 (10-seed pilot)": `sim_summary.csv` main/IG 27.32 and R3/IG 11.6.
- Appendix D: all constants from the code files named at its head. Line numbers are in `review_response.md`. EB floor 38.5% and 7.5%: `sim_eb_constants.json`, `share_tau2_floored(kappa>1e6)`.

## Review round, pass 2 (new numbers in paper.tex; sources in `results/E03/`)
- PEER, PEER-SUM, FE-BRIER (Section 4.1, Table A-newrules): `review_x1_rules_summary.csv` columns pct, ci_lo, ci_hi, seed_min, seed_max, best_handcoded, best_handcoded_pct, copy_crowd_pct, copy_lo, copy_hi. Text values: PEER main 46.0 [43.7, 48.3], copy-crowd 14.2 [13.7, 14.6]; PEER-SUM main 46.8, copy 12.6; FE-BRIER main 43.2 [41.6, 44.8]; peer rules under R1 about 52.5 (PEER 52.5, PEER-SUM 52.7); abstract "43 to 47" is the main-condition range of the three rules (43.2, 46.0, 46.8); "10th to 23rd percentile" is the range of copy-crowd over all nine cells (10.3 to 22.5). 16 rules = 13 + 3.
- Skill and volume (Section 4.6, Table A-skillvol): `review_x2_skill_volume.csv` columns rho_skill, rho_volume, main. IG-SUM 0.36 / 0.74; EB0-IG 0.45 / 0.61; PEER 0.60, PEER-SUM 0.66, FE-BRIER 0.59 skill with volume about 0. "0.26 to 0.39" absolute rules and "0.45 to 0.66" crowd-relative and peer rules: min and max over ACC, BRIER, EB-BRIER (0.26, 0.32, 0.39) and over EB0-IG, BSS, IG, EB-IG, BRIER-GAIN, PEER, PEER-SUM, FE-BRIER excluding IG-SUM (0.45 to 0.66).
- EB diagnostics (Limitations): `review_x3_eb_floor.csv`; 40% of Brier worlds (241/600), 8% of IG worlds (51/600); EB-IG 42.7 at the floor vs 41.8 above; EB0-IG 46.1 (moments) vs 39.8 (Paule-Mandel) under R2: `review_x1_rules_summary.csv`, rule EB0-IG-PM, cond R2. About 300 flooded claims: `review_x1_policies.csv` (median 316 in main), `review_facts.md`.
- Misspecified distortion (Section 4.3, Table asym): `review_x4_asym_summary.csv` cond R2asym_none, R2asym_logit, R2asym_iso. IG-SUM 92.4 [92.0, 92.8], 29.2 [25.8, 32.6] (seed_max 48.1), 56.6 [53.7, 59.1]; gamma 2.1036; mean error 0.044 (target), 0.045 (eligible events); baseline error 0.045 / 0.027 / 0.032. Abstract "29th against 92nd".
- Manifold (Section 4.4): `real_v3_summary.json` and `review_results.md` X5: signature 0.416 (user CI 0.380 to 0.452; market-cluster CI 0.321 to 0.393); price-thresholded ACC 0.223; directional IG stability 0.12 / 0.24 / 0.36 random and 0.11 / 0.25 / 0.30 early-late at 20 / 50 / 100 claims (`real_v3_stability.csv`, rule DIR-IG; IG temporal 0.07 / 0.12 / 0.18 from the same file, 0.065 / 0.115 / 0.185). Horizon medians 180 and 18 days: `real_v3_horizon.csv`. Look-ahead: `review_manifold_lookahead.json` (81 / 261 / 469 fit markets, 1 / 3 / 42 resolved after the block start, 9.0% in block 3).
- LLM correction (Section 4.5): one gemma-4-26b-a4b-it run, ACC target, pair 1, 17 claims, BSS percentile 100: `llm_pundit_log.csv`; BSS target runs 5.5 to 24.5 (Table A8).
- 30-seed Table 2 removed from the body (duplicate of Table A2 = tab:A1). Table A9 (old, main vs R2 for six crowd-relative rules) removed: its cells are all in A2 (tab:A1) rows BSS, IG, EB-IG, EB0-IG, IG-SUM, BRIER-GAIN.
