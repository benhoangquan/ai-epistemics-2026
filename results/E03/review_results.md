# E03 review-round results (15 Nov, post hoc)
Setup: all simulation numbers are the learned zero-skill cheater's held-out percentile among ~200 honest skilled sources (50 = median), mean [95% bootstrap CI over seeds], n = 30 seeds, same CEM budget (40 iterations, population 64, 12 elites, 6 worlds per iteration) and same rng stream as the original run. CEM is a lower bound on exploitability. Code: `experiments/E03_track_record/{sim_v3.py, analyze_review.py, sim_recal_asym.py, real_v3.py, check_fe_approx.py}`. Raw: `sim_v3_{main,R1,R2}.json`, `sim_cache_v3/`. The first 13 rules reproduce the original run (e.g. main BSS 72.5, IG-SUM 11.5, same as `new_results.md`).
Deviation: none in seed counts (30 everywhere). X3 REML not done; Paule-Mandel (PM) was added as the better estimator.

## X1. New rules (source: `review_x1_rules_summary.csv`, `review_x1_policies.csv`)
Definitions in the header of `sim_v3.py`. PEER = mean over peered claims of [log2 r_y minus the mean log2 score of the honest peers who claimed the same event; the source's own claim is left out for honest sources]; claims on events with no peers are dropped. PEER-SUM = sum of the same. FE-BRIER = minus the source effect of a two-way fixed-effects fit (alternating least squares, 25 sweeps, mean honest effect 0); the cheater's effect is solved with the honest-fitted event effects held fixed (checked against a full fit with the cheater included: 20 worlds, 3 policies, mean percentile differs by at most 0.1 and the largest single-world difference is 2.0; `review_fe_check.json`).

| rule | cond | learned cheater | seed range | best hand-coded | **copy-the-crowd** [CI] |
|---|---|---|---|---|---|
| PEER | main | 46.0 [43.7, 48.3] | 32.8 to 61.3 | cherry-pick 43.3 | **14.2 [13.7, 14.6]** |
| PEER | R1 | 52.5 [49.9, 55.1] | 34.4 to 66.5 | cherry-pick 52.9 | 22.5 [21.9, 23.2] |
| PEER | R2 | 49.5 [47.6, 51.4] | 40.0 to 62.5 | cherry-pick 37.2 | 10.4 [10.1, 10.8] |
| PEER-SUM | main | 46.8 [45.9, 47.7] | 39.8 to 50.3 | cherry-pick 39.8 | **12.6 [12.3, 13.0]** |
| PEER-SUM | R1 | 52.7 [50.8, 54.8] | 43.5 to 71.7 | low-vol/cherry 55.8 | 19.2 [18.6, 20.0] |
| PEER-SUM | R2 | 47.7 [47.1, 48.4] | 43.7 to 50.9 | low-vol-gamble 34.5 | 10.3 [10.0, 10.6] |
| FE-BRIER | main | 43.2 [41.6, 44.8] | 35.6 to 51.2 | cherry-pick 48.3 | 14.6 [14.1, 15.1] |
| FE-BRIER | R1 | 47.3 [45.6, 48.9] | 36.6 to 56.7 | cherry-pick 50.8 | 18.9 [18.3, 19.6] |
| FE-BRIER | R2 | 46.3 [45.5, 47.1] | 42.0 to 50.7 | cherry-pick 47.7 | 11.4 [11.0, 11.8] |

- **The Jensen hypothesis is not supported.** Copying the calibrated crowd lands at the 10th to 23rd percentile under PEER and PEER-SUM in every condition, far below the median; the honest peers' private information makes them beat the crowd on average.
- The new rules do not resist as well as IG-SUM/EB0-IG in main: the learned cheater sits at 43 to 47 (CIs below 50 in main and R2 except noted) versus 11.5 for IG-SUM. Under R1 (miscalibrated honest sources) PEER and PEER-SUM are marginally above the median (52.5 [49.9, 55.1], 52.7 [50.8, 54.8]); seed maxima reach 61 to 72. They are not exploitable the way absolute rules are (98 to 100), but they are noisy and close to 50, i.e. the cheater gets about a median rank. Learned policies (`review_x1_policies.csv`): PEER cheater makes about 10 claims with alpha 2.8 (a variance gamble), PEER-SUM about 12 claims, alpha 1.2.
- R2 does not break PEER/FE-BRIER (no crowd-bias dependence): 49.5, 47.7, 46.3.

## X2. Honest-skill and volume recovery (source: `review_x2_skill_volume.csv`; mean over 20 test worlds per seed, then over 30 seeds; CIs are in the csv, half-widths about 0.01 or less)
Spearman(score, true skill k) / Spearman(score, claim volume N):

| rule | main k / N | R2 k / N | R1 k / N |
|---|---|---|---|
| ACC | 0.26 / -0.03 | 0.27 / -0.03 | 0.27 / -0.03 |
| BRIER | 0.32 / -0.03 | 0.32 / -0.03 | 0.32 / -0.03 |
| LOG | 0.33 / -0.04 | 0.33 / -0.04 | 0.32 / -0.04 |
| DW-ACC | 0.29 / -0.03 | 0.29 / -0.03 | 0.30 / -0.03 |
| DW-BRIER | 0.38 / -0.03 | 0.37 / -0.03 | 0.39 / -0.03 |
| TOPIC-BRIER | 0.32 / -0.03 | 0.33 / -0.04 | 0.33 / -0.03 |
| EB-BRIER | 0.39 / 0.01 | 0.40 / 0.00 | 0.39 / 0.00 |
| BSS | 0.53 / 0.03 | 0.51 / 0.01 | 0.50 / 0.03 |
| IG | 0.54 / 0.03 | 0.54 / 0.01 | 0.48 / 0.01 |
| EB-IG | 0.60 / -0.04 | 0.60 / -0.03 | 0.53 / -0.01 |
| EB0-IG | 0.45 / **0.61** | 0.41 / **0.68** | 0.44 / 0.46 |
| IG-SUM | 0.36 / **0.74** | 0.31 / **0.80** | 0.38 / 0.57 |
| BRIER-GAIN | 0.52 / 0.04 | 0.53 / 0.03 | 0.49 / 0.03 |
| PEER | 0.60 / 0.00 | 0.61 / 0.00 | 0.52 / -0.02 |
| PEER-SUM | 0.66 / -0.01 | 0.65 / -0.02 | 0.56 / 0.02 |
| FE-BRIER | 0.59 / 0.00 | 0.59 / 0.00 | 0.55 / -0.01 |
| EB-BRIER-PM | 0.40 / 0.01 | 0.40 / 0.01 | 0.40 / 0.01 |
| EB-IG-PM | 0.60 / -0.04 | 0.60 / -0.03 | 0.54 / -0.01 |
| EB0-IG-PM | 0.46 / 0.61 | 0.41 / 0.68 | 0.45 / 0.44 |

**The reviewer's concern is confirmed:** IG-SUM and EB0-IG rank honest sources more by volume (rho 0.74 and 0.61 in main; 0.80 and 0.68 in R2) than by skill (0.36 and 0.45). The rules that resist cheating best in main therefore also reward volume. Best skill recovery: PEER-SUM 0.66, PEER 0.60, EB-IG 0.60, FE-BRIER 0.59 (all with volume correlation near 0).

## X3. EB diagnostics (source: `review_x3_eb_floor.csv`; pooled over 600 test worlds, cluster bootstrap over seeds)
Between-source variance estimate at its floor (1e-12, complete pooling), method of moments (MoM):
- EB-BRIER: at floor in 40% of main worlds (241/600; R1 35%, R2 39%); the cheater is at 100.0 [100.0, 100.0] both at the floor (n = 241 worlds) and above it (n = 359). So the 100.0 is not an artefact of the floor.
- EB-IG: at floor in 8% (51/600): 42.7 [40.7, 44.4] vs above floor 41.8 [41.3, 42.3]. No difference.
- Paule-Mandel (PM) instead of MoM: EB-BRIER-PM at floor in 6% of worlds, still 100.0 [100.0, 100.0] in both groups (R1 at-floor 99.99). EB-IG-PM never at floor, 41.8 [41.8 over 600 worlds; CI 41.2 to 42.4], i.e. the same as MoM (41.9). EB0-IG-PM 11.6 (main), 19.9 (R1), 39.8 (R2) vs EB0-IG 11.3, 20.2, 46.1: a better estimator changes little in main/R1 and lowers EB0-IG's R2 failure from 46.1 to 39.8, still not a fix. Source: `review_x1_rules_summary.csv`.

## X4. Non-logistic crowd distortion (source: `review_x4_asym_summary.csv`, `sim_recal_asym_all.json`, `sim_cache_recal_asym/`; n = 30 seeds)
R2asym formula: for the true crowd probability p >= 0.5, c = 0.5 + 0.5 (2p - 1)^gamma with gamma = 2.1036 (favourites under-priced); for p < 0.5, c = p. gamma was chosen so mean |c - p| = 0.044 (achieved 0.044 on the 15,000-event calibration sample; 0.045 over the eligible events in the runs), the same as R2's 0.044. Blocks, fits and cheater are those of `sim_recal.py`. Learned-cheater percentile:

| baseline | IG-SUM | EB0-IG | IG | BRIER-GAIN | BSS |
|---|---|---|---|---|---|
| raw crowd | **92.4 [92.0, 92.8]** | 65.5 [63.8, 67.0] | 39.7 [37.8, 41.7] | 41.0 [38.5, 43.5] | 77.8 [73.4, 81.8] |
| logistic recal | 29.2 [25.8, 32.6] (seed max 48.1) | 17.4 [15.9, 18.9] | 26.1 [24.3, 28.0] | 25.9 [24.1, 27.7] | 81.7 [79.5, 83.9] |
| isotonic recal | **56.6 [53.7, 59.1]** | 34.6 [32.4, 36.6] | 24.5 [22.9, 26.2] | 23.3 [22.0, 24.7] | 80.3 [76.9, 83.4] |

Mean baseline error |baseline - truth|: raw 0.045, logistic 0.027, isotonic 0.032. Findings: with a misspecified (non-logit-linear) bias, logistic recalibration still holds IG-SUM below the median (29.2 [25.8, 32.6]) but with less margin than in the well-specified R2 case (16.2) and with one seed at 48.1; isotonic again fails (56.6 [53.7, 59.1]); BSS stays gameable (78 to 82). The residual baseline error (0.027, versus 0.012 well-specified) is the exploitable gap. A bias with different shape or larger size was not tested.

## X5. Manifold checks (source: `real_v3_summary.json`, `real_v3_stability.csv`, `real_v3_horizon.csv`, `review_manifold_lookahead.json`; `real_v3_stdout.txt`)
(a) Orientation. The original ACC is already trade-direction oriented (`real.py` score(): ACC = bet side won), and the original signature's favourite share is the crowd probability of the side bet on. Alternatives (signature rho = Spearman(share of claims on >= 90% favourites, ACC rank - IG rank), n = 1,855 users with >= 20 claims; user-bootstrap CI; market-cluster CI; 300 resamples):
- original (direction ACC, direction share): 0.416, user CI [0.380, 0.452], market-cluster CI [0.321, 0.393]
- ACC from post-bet price thresholded at 0.5, direction share: 0.223 [0.181, 0.266], market [0.123, 0.204]
- price ACC and price (market-favoured side) share: 0.231 [0.187, 0.273], market [0.134, 0.220]
- direction ACC, price share: 0.133 [0.091, 0.181], market [0.074, 0.156]
- direction ACC vs directional IG (b), direction share: 0.528 [0.498, 0.557], market [0.452, 0.532]
The signature depends on orientation: with price-thresholded ACC it halves to 0.22, so the claim "gaming signature 0.42" holds for direction-oriented accuracy. The market-cluster CI is wider and its upper end (0.39) does not reach the point estimate: the point estimate sits above the cluster-bootstrap interval, suggesting the cluster resampling shifts the statistic downward, so quote the user-bootstrap CI with that caveat. Split-half stability of ACC: direction 0.35 [0.32, 0.38] random / 0.32 [0.28, 0.36] temporal (n = 1,855); price-thresholded 0.08 [0.04, 0.11] / 0.08 [0.04, 0.13]. So ACC's stability is almost entirely the bet-direction selection habit.
(b) Directional IG: claim score log2 r' - log2 c with r' = sigmoid(logit c + 0.5 x direction); stability (random / temporal, CIs over all 20 splits in `real_v3_stability.csv`):
 - >= 20 claims (1,855 users): DIR-IG 0.12 [0.09, 0.16] / 0.11 [0.06, 0.15]; DIR-IG-SUM 0.17 [0.13, 0.21] / 0.15 [0.11, 0.20]; (IG 0.07, IG-SUM 0.10).
 - >= 50 (488): DIR-IG 0.24 [0.19, 0.30] / 0.25 [0.18, 0.34]; DIR-IG-SUM 0.27 / 0.26 [0.18, 0.35]; (IG 0.17 / 0.12).
 - >= 100 (112): DIR-IG 0.36 [0.22, 0.48] / 0.30 [0.13, 0.48]; DIR-IG-SUM 0.39 / 0.30 [0.10, 0.49]; (IG 0.39 / 0.18).
 Directional IG roughly doubles the temporal stability of crowd-relative scores at >= 20 and >= 50 claims, but it scores the direction of the trade, not its size or the price move, so it is closer to a direction-accuracy score against the crowd.
(c) Split-half CIs over all 20 random splits (and temporal), 300 user resamples: original rules at >= 20: ACC 0.35 [0.32, 0.38], BRIER 0.10 [0.06, 0.13], IG 0.07 [0.03, 0.11], IG-SUM 0.10 [0.06, 0.14], BSS 0.07 [0.04, 0.11]; at >= 50 and >= 100 see the csv (e.g. >= 100 IG 0.39 [0.25, 0.51], temporal 0.18 [-0.01, 0.36]). These are the corrected versions of the Table A4 CIs that used 5 of 20 splits.
(d) Resolution horizon (claim to resolution, claim-time quartiles; `real_v3_horizon.csv`): block 0 (to 2023-08) median 180 days [137, 218]; block 1 47 [37, 68]; block 2 47 [33, 68]; block 3 (2024-12 to 2026-11) 18 [12, 22]; share of claims with horizon above 30 days 74%, 58%, 58%, 38%. Later blocks are short-horizon (CIs by market bootstrap), which is right-censoring: only markets already resolved by 12 Nov 2026 are in the sample. The backtest is therefore affected by horizon selection; the recalibration fit for block 3 uses mostly long-horizon history and is scored on short-horizon claims. Look-ahead proxy check (`review_manifold_lookahead.json`): the fit sets use markets whose last claim precedes the block start; of the 81 / 261 / 469 fit markets (blocks 1 / 2 / 3), 1 / 3 / 42 actually resolved after the block start (1.2% / 1.1% / 9.0% of markets; 0.9% / 1.0% / 8.9% of fit claims), i.e. a small look-ahead leak, largest for block 3.

## Skipped or deviated
REML not run (Paule-Mandel used). Asymmetric distortion has one shape and one size only. Correction to `new_results.md` item 6: one ACC-targeted LLM run (gemma-4-26b-a4b-it, pair 1, 17 claims) scored BSS percentile 100, so the LLM did occasionally reach the BSS exploit, though never when told to optimise BSS (`llm_pundit_log.csv`).
