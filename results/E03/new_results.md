# E03 new results (post hoc, Sun 15 Nov 2026)

Everything here was produced after the pre-registered pilot (README sections 1-8) and is labelled post hoc. All
simulation CIs are 95% percentile-bootstrap CIs over seeds (10,000 resamples, `analyze_v2.py`), n = number of seeds. A
seed's percentile is the mean over 20 held-out worlds x 3 replicate draws, as in the original run. "Percentile" = share of
honest skilled sources (about 200 per world) that the learned zero-skill cheater outscores; 50 = the median honest
source. The CEM optimizer gives only a **lower bound** on exploitability: a rule that "resists" here has resisted this
search budget (40 iterations, population 64), not every possible cheater.
Code: `experiments/E03_track_record/{run_seeds30.py, sim_recal.py, analyze_v2.py, real_minclaims.py, real_recal.py, llm_pundit.py, analyze_llm.py}`.
No original result file was overwritten; all outputs below are new files.

## Item 2: 30 seeds, main and R2 (all 13 rules)
- Command: `uv run python -I experiments/E03_track_record/run_seeds30.py` then
  `uv run python -I experiments/E03_track_record/analyze_v2.py` (stdout: `results/E03/analyze_v2_stdout.txt`).
- Seeds 0-9 are the cached seeds of the original run (identical numbers); seeds 10-29 are new. Raw: `results/E03/sim_main_30seeds.json`,
  `results/E03/sim_R2_30seeds.json`; summary `results/E03/sim_30seeds_summary.csv` (columns: pct, CI, sd over seeds, seed min/max,
  mean of first 10 and of new 20 seeds, share of test worlds above median with CI); BSS per seed: `results/E03/sim_30seeds_bss_per_seed.json`.

Learned-cheater percentile, mean [95% CI], n = 30 seeds, and seed range (min to max):

| rule | main | main seed range | R2 | R2 seed range |
|---|---|---|---|---|
| ACC | 98.9 [98.8, 99.0] | 97.9 to 99.4 | 99.2 [99.2, 99.3] | 98.9 to 99.6 |
| BRIER | 99.8 [99.8, 99.9] | 99.4 to 99.9 | 99.9 [99.8, 99.9] | 99.5 to 100.0 |
| LOG | 99.9 [99.8, 99.9] | 99.5 to 100.0 | 99.9 [99.7, 99.9] | 98.4 to 100.0 |
| DW-ACC | 98.2 [97.9, 98.4] | 96.2 to 99.2 | 98.5 [98.2, 98.7] | 95.0 to 99.1 |
| DW-BRIER | 99.7 [99.6, 99.8] | 98.0 to 100.0 | 99.8 [99.8, 99.9] | 99.2 to 100.0 |
| TOPIC-BRIER | 99.7 [99.7, 99.8] | 99.1 to 100.0 | 99.6 [99.5, 99.7] | 98.6 to 100.0 |
| EB-BRIER | 100.0 [100.0, 100.0] | 100.0 to 100.0 | 100.0 [100.0, 100.0] | 100.0 to 100.0 |
| BSS | **72.5 [68.9, 75.7]** | **39.2 to 89.4** | 76.9 [73.0, 80.8] | 54.1 to 93.7 |
| IG | 27.8 [25.6, 29.9] | 16.5 to 40.3 | 40.5 [38.5, 42.5] | 30.0 to 51.3 |
| EB-IG | 41.9 [41.4, 42.3] | 38.4 to 44.3 | 42.6 [41.7, 43.4] | 36.4 to 48.4 |
| EB0-IG | 11.3 [10.9, 11.8] | 8.7 to 13.5 | 46.1 [44.7, 47.5] | 38.1 to 56.5 |
| IG-SUM | 11.5 [10.9, 12.0] | 6.9 to 13.6 | **81.1 [80.3, 81.8]** | 75.4 to 84.7 |
| BRIER-GAIN (post hoc rule) | 21.7 [19.8, 23.5] | 12.3 to 30.2 | 27.8 [26.0, 29.6] | 19.0 to 41.0 |

- **BSS spread.** Main: mean 72.5, SD over seeds 9.8, range 39.2 to 89.4 (the original 10 seeds gave 69.4, range 39 to 89;
  the 20 new seeds gave mean 74.1). Per-seed values are in the BSS json. R2: SD 11.1, range 54.1 to 93.7. BSS is the
  highest-variance rule: the percentile is roughly the chance that all ~11 favourites win, so single seeds are noisy.
- The original 10-seed CIs were consistent with the 30-seed ones; no rule changed verdict. Ordering of verdicts
  unchanged: absolute rules about 98-100 (gameable), BSS 72.5 (gameable, noisy), IG 27.8, EB-IG 41.9, EB0-IG 11.3, IG-SUM 11.5 (below median in main).
- Under R2 the original 10-seed IG-SUM figure (81.9 [80.7, 83.0]) is reproduced at 30 seeds: 81.1 [80.3, 81.8].

## Item 1: recalibrated-crowd baseline (closes R2 for the learned cheater with a logistic recalibration; isotonic fails)
- Command: `uv run python -I experiments/E03_track_record/sim_recal.py --seeds 30` (log: `results/E03/run.log`),
  summary `uv run python -I experiments/E03_track_record/analyze_v2.py`. Raw: `results/E03/sim_recal_all.json`
  (per seed caches `results/E03/sim_cache_recal/`); summary `results/E03/sim_recal_summary.csv`; learned policies
  (median over seeds) `results/E03/sim_recal_policies.csv`. 9 conditions x 30 seeds, 13 rules each.
- **Design.** Same world generator and same random stream as the original R2/main (worlds are paired with the original runs).
  Events are in time order and split into 4 blocks of 750. Claims (honest and cheater) use only blocks 1-3 (2,250 events). The
  baseline for a block-b event is the crowd prior recalibrated by a map fitted **only** on (published crowd prior, outcome) of
  events in blocks < b: so the baseline is fitted on already-resolved events, never on events being scored, and the cheater
  cannot influence it (the fit uses outcomes of events, not anyone's claims). The cheater sees the published crowd c and
  chooses events, a probability map sigmoid(alpha*logit c + beta) and volume, as in the original CEM; it does not see the
  baseline. Honest sources are rescored against the same baseline (a source with fewer than 2 eligible claims is dropped;
  mean honest sources kept: 200.0 of 200). Modes: `none` (raw crowd baseline, same eligible events: control), `logit` (logistic
  regression of outcome on logit c, ~unregularised), `iso` (isotonic regression, outputs clipped to [0.01, 0.99]).
  Bias conditions: `main` (calibrated crowd), `R2` (crowd = sigmoid(0.75 logit(true)), as original R2), `R2tail` (identity inside |logit| <= 2,
  slope 0.6 outside: a bias a 2-parameter logistic fit cannot represent exactly).

Learned-cheater percentile, mean [95% CI], n = 30 seeds (source: `sim_recal_summary.csv`). IG-SUM and EB0-IG are the rules that failed under R2:

| condition | baseline | IG-SUM | EB0-IG | IG | BRIER-GAIN | BSS |
|---|---|---|---|---|---|---|
| main (calibrated crowd) | none (raw) | 13.8 [12.9, 14.6] | 13.3 [12.7, 13.9] | 27.8 [25.9, 29.7] | 21.8 [20.0, 23.8] | 72.3 [67.5, 76.7] |
| main | logistic recal | 15.5 [14.0, 17.3] | 13.7 [12.8, 14.8] | 27.6 [25.7, 29.5] | 20.8 [19.1, 22.6] | 73.5 [69.2, 77.3] |
| main | isotonic recal | **65.8 [64.5, 67.1]** | 41.2 [38.9, 43.3] | 24.1 [22.7, 25.5] | 21.9 [20.3, 23.6] | 71.0 [67.2, 74.6] |
| R2 (crowd longshot bias) | none (raw) | **85.2 [84.3, 86.1]** | **52.3 [50.3, 54.2]** | 39.7 [36.6, 42.5] | 25.8 [24.2, 27.3] | 79.4 [74.6, 83.7] |
| R2 | **logistic recal** | **16.2 [14.7, 18.0]** | **13.3 [12.6, 14.0]** | 25.5 [23.3, 27.6] | 20.9 [19.3, 22.5] | 80.1 [75.7, 84.2] |
| R2 | isotonic recal | **68.2 [66.6, 69.7]** | 42.6 [41.1, 44.0] | 22.3 [20.9, 23.7] | 22.6 [21.0, 24.2] | 79.1 [74.8, 83.1] |
| R2tail | none (raw) | 24.5 [21.5, 27.7] | 18.7 [17.0, 20.5] | 35.4 [33.2, 37.6] | 21.5 [20.1, 23.0] | 75.5 [70.1, 80.4] |
| R2tail | logistic recal | 20.6 [18.4, 22.8] | 16.6 [15.6, 17.6] | 32.3 [29.9, 34.8] | 20.0 [18.8, 21.2] | 78.3 [73.6, 82.4] |
| R2tail | isotonic recal | 64.5 [62.8, 66.2] | 39.7 [38.3, 41.2] | 23.8 [22.1, 25.4] | 23.2 [22.2, 24.3] | 78.4 [74.1, 82.3] |

Findings:
1. **Logistic recalibration restores resistance under R2.** IG-SUM falls from 85.2 [84.3, 86.1] (raw baseline, same events) to
   16.2 [14.7, 18.0]; EB0-IG from 52.3 to 13.3; IG from 39.7 to 25.5. The learned IG-SUM policy under R2+logistic
   recal: alpha median 1.44 and ~41 claims instead of alpha 1.30 and ~990 claims (`sim_recal_policies.csv`): the flood-and-invert strategy no
   longer pays. Worst seed for IG-SUM under R2+logistic: 31.8 (range 10.0 to 31.8), so all 30 seeds are below the median. (Caveat: the logistic map
   is well-specified here, since the injected bias is exactly logistic-in-logit; this is the favourable case.)
2. **Cost when the crowd is already calibrated:** with logistic recalibration IG-SUM is 15.5 [14.0, 17.3] vs 13.8 [12.9, 14.6] raw
   (CIs overlap slightly; a small, possible cost in resistance, not a failure).
3. **Isotonic recalibration FAILS, even with no bias.** IG-SUM 65.8 [64.5, 67.1] in `main` and 68.2 [66.6, 69.7] in R2. Mechanism
   (from `sim_recal_policies.csv`): the cheater floods (~980 claims) and copies the published crowd (alpha 1.00, beta 0). A step-function
   fit on <= 2,250 noisy outcomes has error (mean |baseline - truth| 0.031 vs 0.012 for logistic, `sim_recal_summary.csv`
   columns `cal_err_*`), so the baseline is *worse than the raw calibrated crowd* and copying the raw crowd earns positive
   summed IG. The zero-skill bound needs a baseline that is calibrated in expectation, not merely fitted; estimation noise in the baseline
   is exploitable by volume. This is the "attack on the recalibration" in its simplest form, found by the optimizer unprompted.
4. **Attack on the fit (short test).** The CEM cheater already chooses event bins and volume freely, so it can flood where the fit is weak
   (this is what it does against isotonic, finding 3). Against the logistic fit the best it finds in R2 is IG-SUM 16.2 (below median, all 30 seeds); I did not run a separate hand-crafted poisoning attack beyond this. **The R2tail test is weak**: under my construction the
   tail bias barely hurts the raw baseline (IG-SUM 24.5, mean crowd error 0.004 vs 0.044 for R2), so it does not stress the logistic
   map; logistic recal gives 20.6 [18.4, 22.8] there, no worse than raw. A stronger misspecified bias was not tested.
5. **Not fixed by recalibration:** BSS stays at 71-80 under every baseline (it is a ratio and exploitable regardless; the baseline
   only changes the denominator), and EB-IG stays at 40-42. Absolute rules are unaffected (97.5-100).
6. Limitations: eligible events are 2,250 of 3,000 (so `none` numbers differ slightly from the original conditions: ACC 97.5 vs 98.9);
   only block-wise (3 fits on 750, 1,500 and 2,250 events) fits; honest sources in this simulation have no miscalibration (R1 not combined with recal).
   n = 30 seeds per cell; the optimizer is a lower bound.

## Item 3: Manifold stability at higher minimum volume
- Command: `uv run python -I experiments/E03_track_record/real_minclaims.py 50` and `... 100`; stdout `results/E03/real_min50_stdout.txt`,
  `results/E03/real_min100_stdout.txt`. Outputs: `results/E03/real_min50/` and `results/E03/real_min100/` (`real_stability_main.csv`,
  `real_summary_main.json`, `real_rule_corr_main.csv`, `real_user_scores_main.csv`, `fig2_manifold.png`).
  Same code, ledger and sampling as the original (first buy per user and market; 500 bootstrap resamples over users; random split = mean over 20 splits).
- Users remaining: **min 20 (original): 1,855 users, 83,298 claims; min 50: 488 users, 42,336 claims; min 100: 112 users, 17,077 claims**
  (`real_summary_main.json` in each directory). These are heavy users, a selected subset.

Split-half Spearman rho [95% CI over users]. Random-split CIs are bootstrapped over 5 of the 20 splits (original design).

| rule | min 20 random (orig, n=1,855) | min 50 random (n=488) | min 50 temporal | min 100 random (n=112) | min 100 temporal |
|---|---|---|---|---|---|
| ACC | 0.35 | 0.47 [0.42, 0.52] | 0.46 [0.39, 0.53] | 0.67 [0.57, 0.76] | 0.63 [0.48, 0.73] |
| DW-ACC | 0.23 | 0.33 [0.28, 0.39] | 0.32 [0.23, 0.40] | 0.54 [0.42, 0.65] | 0.52 [0.36, 0.64] |
| BRIER | 0.10 | 0.18 [0.11, 0.24] | 0.18 [0.10, 0.27] | 0.35 [0.15, 0.46] | 0.34 [0.15, 0.52] |
| LOG | 0.10 | 0.18 [0.11, 0.24] | 0.18 [0.09, 0.26] | 0.33 [0.13, 0.44] | 0.32 [0.13, 0.49] |
| DW-BRIER | 0.04 | 0.10 [0.03, 0.17] | 0.10 [0.02, 0.18] | 0.29 [0.10, 0.38] | 0.23 [0.06, 0.40] |
| TOPIC-BRIER | 0.09 | 0.16 [0.09, 0.23] | 0.17 [0.09, 0.26] | 0.33 [0.13, 0.44] | 0.32 [0.14, 0.50] |
| EB-BRIER | 0.12 | 0.20 [0.12, 0.27] | 0.18 [0.10, 0.27] | 0.37 [0.16, 0.48] | 0.36 [0.15, 0.53] |
| BSS | 0.07 | 0.16 [0.10, 0.24] | 0.10 [0.01, 0.19] | 0.39 [0.25, 0.53] | 0.22 [0.05, 0.39] |
| IG | 0.07 | 0.18 [0.11, 0.26] | 0.12 [0.02, 0.20] | 0.39 [0.23, 0.53] | 0.18 [0.00, 0.37] |
| EB-IG | 0.10 | 0.20 [0.13, 0.28] | 0.11 [0.01, 0.20] | 0.39 [0.23, 0.52] | 0.16 [-0.02, 0.36] |
| EB0-IG | 0.10 | 0.20 [0.14, 0.28] | 0.11 [0.02, 0.20] | 0.40 [0.24, 0.52] | 0.16 [-0.02, 0.36] |
| IG-SUM | 0.10 | 0.21 [0.14, 0.28] | 0.11 [0.01, 0.20] | 0.40 [0.24, 0.53] | 0.15 [-0.04, 0.35] |
| BRIER-GAIN | 0.08 | 0.17 [0.11, 0.25] | 0.11 [0.01, 0.19] | 0.40 [0.25, 0.53] | 0.23 [0.05, 0.40] |

(Min-20 column is the original `results/E03/real_stability_main.csv` point estimate; its CIs are in the README.)
- Random-split stability rises with volume for every rule (BRIER 0.10 -> 0.18 -> 0.35; IG 0.07 -> 0.18 -> 0.39; ACC 0.35 -> 0.47 -> 0.67). At min 100 crowd-relative
  rules reach random-split rho about 0.40, **but their temporal (early vs late) rho is only 0.15 to 0.23, with CIs reaching 0** (n = 112),
  while accuracy stays at 0.63. The random-split numbers use a split-half of one ledger, so they are optimistic relative to the temporal split.
  Accuracy is still the most stable rule at every volume, and (original finding) is largely a selection habit.
- The gaming signature strengthens with volume: Spearman(near-certain share, ACC rank minus IG rank) = 0.52 [0.47, 0.58] (min 50, n=488)
  and 0.56 [0.39, 0.67] (min 100, n=112), vs 0.42 [0.38, 0.45] at min 20 (`real_summary_main.json` in each directory, key
  `spearman_nearcertain_vs_accrank_minus_igrank`).
- Caveat: the population-EB constants are re-estimated on the subset, and heavy users differ from typical users, so this says
  stability rises with volume on this population, not that rules are equally valid.

## Item 5 (stretch): recalibrated baseline on the real Manifold ledger: **negative result**
- Command: `uv run python -I experiments/E03_track_record/real_recal.py` (stdout `results/E03/real_recal_stdout.txt`; outputs
  `results/E03/real_recal_summary.json`, `results/E03/real_recal_stability.csv`).
- Design: claims bucketed by claim time into 4 equal-count blocks (168,701 claims); claims in blocks 1-3 (126,526) are scored against
  p_before recalibrated (logistic on logit, or isotonic) using only claims whose market's last observed claim is before the block start
  (proxy for "resolved by then"; resolution time is not in the derived ledger). Users with >= 20 claims in the eligible set: 1,394 (59,587
  claims); >= 50: 336 (28,250 claims).
- **The recalibrated baseline is worse than the raw market price out of sample.** Mean log2 score of the baseline on eligible claims:
  raw p_before -0.790, logistic -0.832, isotonic -0.833 (`baseline_mean_log2score_eligible_claims`); the recalibrated map is worse in blocks 2 and 3 and slightly
  better in block 1. Fitted logistic slope/intercept drift across blocks (0.93/-0.07, 0.93/-0.70, 0.86/-0.37): the crowd's miscalibration on
  Manifold is non-stationary, so a past-fitted map does not transfer. Population mean IG becomes +0.045 bits (raw -0.001), i.e. the
  baseline got worse for the average user.
- Rank stability did not improve: temporal split-half rho (min 20, n=1,394): IG 0.064 [0.006, 0.110] raw -> 0.011 [-0.035, 0.058] logistic; IG-SUM
  0.072 [0.017, 0.119] raw -> 0.087 [0.046, 0.130] logistic; BSS 0.074 -> 0.008. User IG rankings correlate only 0.37 (logistic) with the raw-baseline
  IG ranking (min 20), 0.46 at min 50. Gaming signature remains (rho 0.42 logistic, 0.39 isotonic, vs 0.43 raw).
- Interpretation: recalibration is a simulation fix for a *stationary* bias; on real Manifold data this simple time-split version does not
  help, so no claim that it improves real leaderboards should be made. Not tuned further.

## Item 6 (stretch): LLM "pundit" that chooses what to claim
- Command: `uv run python -I experiments/E03_track_record/llm_pundit.py --pairs 2` then `uv run python -I experiments/E03_track_record/analyze_llm.py`
  (stdout `results/E03/llm_pundit_stdout.txt`, `results/E03/analyze_llm_stdout.txt`). Raw log (every attempt, strategy text, features):
  `results/E03/llm_pundit_log.csv`; summary `results/E03/llm_pundit_summary.csv`. `epi.llm` tag E03, workers 2.
  **Calls: 223 in total for E03 (4 errors), $0.117** (`python -m epi.llm`), under the 400 cap.
- Design: the pundit is in the simulated main-condition world (`sim.make_world`): it sees 300 events (id, topic label T0-T4, published crowd
  probability; outcomes hidden, so there is no question text to leak outcomes), told the leaderboard rule and that it has no information beyond the crowd,
  and may claim 10-60 events with any probabilities. Reference population: that world's 200 honest skilled sources (same percentile scale as the CEM cheater).
  Per (model, rule, world pair): round 1 = 4 samples on pool A; best by the target rule's percentile; round 2 = 4 samples shown its best strategy and percentile
  (best-of-8 / one-step bandit); the winning *strategy text* is then applied to an unseen pool B from a different world (1 call; one retry if invalid), and
  scored on B. NONE = no rule named ("be a well-calibrated forecaster"), 4 samples per model and pair straight on B.
- Models: gemma-4-31b-it and gemma-4-26b-a4b-it. **Deviation:** deepseek-v4-flash was planned as the second model but used its whole 4,000-token output on reasoning and
  returned empty text, so it was dropped (a few wasted calls). Two world pairs per model only (not three) to stay inside the call budget. A first version on anonymised real Manifold
  markets was abandoned after 9 smoke calls because honest Manifold users' IG scores are about 0 by construction, so percentile against them was meaningless.
  One held-out B run (gemma-4-31b-it, pair 1, IG) returned an invalid claim set twice, hence n = 1 for that cell.

Held-out (pool B) percentile of the target rule among 200 honest skilled sources, pooled over both models (n = held-out runs, bootstrap CI over runs; n is tiny, so also see min to max):

| rule | n | held-out pct [CI] | min to max | share above median | best-of-8 pct on pool A (in-sample) | share of claims on >= 90% favourites | mean claims |
|---|---|---|---|---|---|---|---|
| ACC | 4 | 98.8 [98.3, 99.4] | 98.2 to 99.8 | 4/4 | 99.5 | 0.9 | 42.8 |
| BRIER | 4 | 99.0 [98.6, 99.4] | 98.5 to 99.5 | 4/4 | 98.4 | 0.9 | 56.0 |
| IG | 3 | 0.7 [0.0, 1.0] | 0.0 to 1.0 | 0/3 | 34.1 | 1.0 | 34.7 |
| IG-SUM | 4 | 5.2 [1.8, 8.8] | 0.5 to 10.0 | 0/4 | 9.8 | 0.7 | 36.5 |
| BSS | 4 | 13.8 [7.2, 20.6] | 5.5 to 24.5 | 0/4 | 15.1 | 0.9 | 51.2 |
| NONE (rule not stated) | 16 | ACC 64.3, BRIER 67.9, IG 11.3, IG-SUM 11.8, BSS 13.7 (means over all rows) | | | | 0.5 | 55.9 |

Reference policies on the same pool B: copy the crowd on the 40 most confident events: ACC 97.2, BRIER 96.8, IG 11-12, IG-SUM 11, BSS 13.8; copy the crowd on 40 random events: ACC 22.4, BRIER 41.0, IG-SUM 11.
- **The LLM rediscovers cherry-picking when told the rule is accuracy or Brier**: held-out 98.8 and 99.0, and the strategy text says so
  (it claims favourites and extremizes lightly, mean alpha 1.1 and 1.0, `llm_pundit_summary.csv`). It does this about as well as copying the crowd on the 40 most
  confident events (97.2/96.8), i.e. it recovers the hand-coded cheat, nothing cleverer.
- **It does not climb under the rules that resisted the CEM cheater**: IG 0.7, IG-SUM 5.2 and BSS 13.8 held-out, all below the median in every run.
  Held-out IG and IG-SUM are *below* copying the crowd (11-12); the LLM's contrarian or extremizing tweaks lose. Notably it did **not** find the BSS exploit that CEM found
  (72.5 at 30 seeds: ~11 claims on >= 95% favourites): its BSS is 13.8, with 51 claims on average. The LLM is a weaker exploiter than the optimizer, consistent with the
  CEM result being a lower bound; an LLM failing to find an exploit is not evidence that none exists.
- Even with no rule named, the default pundit is already above the median for ACC (64.3) and BRIER (67.9) because half its claims sit on >= 90% favourites,
  i.e. an unprompted LLM tends to pick safe questions.
- Limits: 4 held-out runs per rule from 2 models and 2 world pairs; the claims pool is 300 events with at most 60 claims (CEM: 3,000 events, floods of 1,000); one-step
  best-of-8 selection, not a full bandit. In-sample A percentiles for IG (34.1) exceed held-out ones (0.7): feedback overfits to the pool's outcomes.

## Things that failed, deviated or were not done
- Item 1: R2tail attack too weak to stress the logistic recalibration (above); no hand-crafted poisoning attack beyond the CEM cheater; isotonic recalibration fails; real-data
  recalibration backtest (item 5) is negative.
- Item 3 `real_min*` outputs include their own `fig2_manifold.png`; the duplicate `real_claims_main.csv.gz` written by the reused script was deleted (same file as the original).
- Item 6: deepseek dropped (empty outputs), 2 not 3 world pairs, simulated rather than real questions (see above), one invalid held-out run.
- Pre-registered README sections were not edited. `sim_main.json`, `sim_R2.json`, `sim_summary.csv` etc. (10-seed originals) are untouched.
