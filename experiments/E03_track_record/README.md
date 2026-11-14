# E03 Track-Record Ledger: which reliability score survives a learning cheater? (P2.1a, Track 2)

Pilot plus kill test, run 2026-11-14 by a coding agent. No LLM calls are planned (budget: 0, cap 200, tag `E03`).
Sections 1–3 were written before the main simulation run and before any real data was downloaded (about four probe
requests to three Manifold endpoints were made to check that the API answers without a token).

## 1. Question
Source-reliability leaderboards ("this pundit is right 87% of the time") score sources on the claims they chose to
make. A source with no information can still choose *which* events to claim, *what* probability to state and *how
many* claims to make. If we let a zero-skill source **learn** that choice against a given scoring rule, how far up the
ranking of honest, skilled sources can it climb? We compare common rules (accuracy, mean Brier, mean log score),
difficulty-weighted and per-topic variants, empirical-Bayes shrinkage by volume, and crowd-relative rules (Brier skill
score against the crowd prior, information gain over the crowd). The goal is a ranking of rules by *learned-cheater
inflation*, with a short argument for why some rules resist. A real-data check on Manifold Markets bets asks whether
the same rules are stable on real sources and whether real users show the gaming signature (high accuracy, low
information gain).

## 2. Kill test
Copied from `brainstorm.yaml` (P2.1a): *Drop real data if we can't collect around 500 dated, attributed, resolved
claims by Saturday evening. Run on fully simulated sources instead.*

Signal threshold added for this pilot (from the task brief), pre-registered:
- **Signal present** if a learned zero-skill cheater's held-out percentile among honest skilled sources is above 50
  (the median honest skilled source) with the 95% bootstrap CI over seeds entirely above 50 under **accuracy or mean
  Brier**, **and** at least one rule keeps it below 50 with the CI entirely below 50.
- If neither widely used rule is inflated above the median, or no rule holds, we say so plainly and the verdict is
  DROP (or PIVOT if a different, clearly stated signal appears).
- Real data: KEEP the real-data arm only if ≥ 500 resolved, dated, attributed claims are collected. Its pre-registered
  checks are (a) split-half rank stability per rule and (b) a gaming signature: among users with ≥ 20 claims, the
  share of claims made on near-certain markets (crowd prior ≥ 0.9 in the claimed direction) correlates positively
  with (accuracy rank − information-gain rank).

## 3. Design
### Part A: simulation (numpy, CPU)
**World.** 3,000 binary events per world, 5 topics with public mean log-odds μ_t ∈ {−2.5, −1.25, 0, 1.25, 2.5}
(base rates from about 8% to 92%). Event *i* has a public log-odds component a_i ~ N(μ_t, 1.5²) and a private component
b_i ~ N(0, σ_i²), σ_i ~ U(0.25, 2.5) (events with large σ_i are hard). Outcome y_i ~ Bernoulli(sigmoid(a_i + b_i)).
- **Crowd prior** c_i = E[sigmoid(a_i + b) | a_i, σ_i]: the calibrated forecast given public information, computed by
  Gauss–Hermite quadrature. It is recorded before any source claims.
- **Honest sources** (200 per world): skill k ~ U(0.1, 0.9). A source sees s = b_i + e, with e scaled so that its
  posterior mean of b is k·s (k = share of private variance it can explain). It reports the calibrated posterior
  E[sigmoid(a + b) | a, s]. Volume n ~ log-uniform(10, 500); events chosen uniformly at random. All 200 count as
  "honest skilled sources"; the median one has k ≈ 0.5.
- **Zero-skill sources** see only (c_i, topic_i). Hand-coded policies: copy the crowd; always 0.5; cherry-pick
  near-certain events (crowd ≥ 0.95 either way); cherry-pick + extremize to 0.99; extremize the crowd everywhere
  (logit ×3); flood (1,000 claims, copy crowd); abstain on hard events (claim only crowd confidence ≥ 0.75); pick the
  most lopsided topic; low-volume gamble (10 claims, extremized); cherry-pick + flood.

**Scoring rules** (higher = better; each is computed per source over that source's claims):
| id | rule |
|---|---|
| ACC | accuracy, % of claims on the right side of 0.5 (0.5 counts as half right) |
| BRIER | −mean Brier score |
| LOG | mean log score (bits), probabilities clipped to [0.001, 0.999] |
| DW-ACC | difficulty-weighted accuracy, weight 4c(1−c) from the crowd prior, normalized per source |
| DW-BRIER | difficulty-weighted −Brier, same weights |
| TOPIC-BRIER | −(Brier − mean Brier of all claims in that topic): per-topic normalization |
| EB-BRIER | −Brier with empirical-Bayes shrinkage by volume toward the population mean |
| BSS | Brier skill score vs the crowd prior, 1 − ΣBrier(r)/ΣBrier(c) |
| IG | information gain over the crowd, mean [log₂ S(r) − log₂ S(c)] (the log market-scoring-rule payoff) |
| EB-IG | IG with EB shrinkage toward the population mean |
| EB0-IG | IG with EB shrinkage toward 0 (the zero-skill baseline) |
| IG-SUM | total IG (volume-sensitive, like a cumulative peer-score leaderboard) |

EB shrinkage: m̃ = (n·m + κ·target)/(n + κ), κ = σ²_within / τ²_between by method of moments over the honest
population of that world. Population statistics (topic means, EB constants) are computed from the honest sources; one
extra source changes them negligibly.

**Learning cheater.** A zero-skill policy with 14 parameters: selection logits over 6 crowd-confidence bins and 5
topics (events are sampled without replacement with these weights), a report map r = sigmoid(α·logit(c) + β), and
log₁₀ volume ∈ [1, 3] (10 to 1,000 claims). It is trained separately against each rule by the cross-entropy method
(derivative-free policy search: 64 candidates, 12 elites, 30 iterations, 4 training worlds per iteration drawn from
40 per seed). Reward = the cheater's percentile among the 200 honest sources (share it beats, ties count half). It
starts as "copy the crowd on 100 random events".

**Inflation metric.** Held-out percentile of the trained cheater on 20 fresh test worlds, averaged per seed; 10 seeds
per rule; 95% bootstrap CI over seeds. We also report the share of test worlds in which the cheater beats the median
honest source, and a transfer matrix (cheater trained on rule X, scored by rule Y).

**Pre-registered expectation (theory).** For a strictly proper rule S and a crowd prior c that is calibrated with
respect to everything the cheater can see, E[S(r, y) − S(c, y)] ≤ 0 for every claim the cheater picks, whatever its
selection rule, so crowd-relative rules (BSS, IG, EB0-IG, IG-SUM) should hold the cheater at or below zero skill.
Absolute rules (ACC, BRIER, LOG and their difficulty-weighted and per-topic versions) should be inflated by
cherry-picking near-certain events. EB shrinkage toward a positive population mean should be exploitable by
low-volume entry. Rank-based rewards favour variance, so low-volume gambling may buy a few percentile points even
under relative rules.

**Exploratory robustness conditions** (run if time allows, labelled exploratory): (R1) honest sources miscalibrated
(per-source logit scaling λ ~ logN(0, 0.3)); (R2) crowd prior miscalibrated with a favourite–longshot bias
(c' = sigmoid(0.75·logit c)), which breaks the theorem's assumption; (R3) minimum volume of 30 claims.

### Part B: real data (kill test for the real-data arm)
- **Source:** Manifold Markets public API (`api.manifold.markets/v0`, no token). About 700 resolved YES/NO binary
  markets with ≥ 20 unique bettors, sampled at random (fixed seed) from the top 2,000 resolved binary markets by
  popularity; up to 2,000 bets per market; one market-detail request per market for topic tags. Requests are capped at
  about 3 per second (the documented limit is 500 per minute). Raw responses are cached in `results/E03/data/`.
- **Claims:** each user's *first* filled buy on a market (amount > 0, not a redemption, not an ante) is one claim:
  direction = bet outcome, stated probability = market probability after the bet, crowd prior = probability before
  the bet, timestamp = bet time, outcome = market resolution. Sensitivity: all filled buys. MKT/N/A resolutions are
  excluded.
- **Analyses:** the same rules applied to users with ≥ 20 claims; topic = first matching coarse topic from the
  market's group tags. (a) Split-half rank stability per rule: Spearman correlation between rule scores on two halves
  of each user's claims, random split (mean of 20 splits) and temporal split (first vs second half by time),
  bootstrap 95% CI over users. (b) Gaming signature as stated in the kill test, plus the IG percentile of the top
  accuracy decile. (c) Exploratory: accounts flagged `isApi` (bots) vs others.

**Budget.** 0 LLM calls. CPU only (multiprocessing, ≤ 16 workers). About 2,000 HTTP requests to Manifold.

### Deviations from the pre-registration (written after the runs)
- **CEM budget:** raised from 30 iterations × 4 worlds to 40 × 6 after the smoke test and before the main run, to cut
  reward noise. A further exploratory run with about 5× the budget (80 iterations, 128 candidates, 8 worlds) is
  reported as `main_strong`.
- **Post-hoc rule `BRIER-GAIN`** = mean[Brier(c) − Brier(r)], the difference form of BSS. It was added after the
  first main run showed BSS being inflated. It is appended last, so the other rules are unaffected: rerunning
  reproduced the first run's learned percentiles for the 12 pre-registered rules exactly (max abs diff 0.0,
  `results/E03/rerun_check.json`). It is marked `*` and is excluded from the kill-test check.
- **Hand-coded "abstain-hard"** claims only events with crowd ≥ 0.8 either way (bins 3–5), not ≥ 0.75, to match the bin
  edges.
- **Manifold pool:** the search API caps `offset` at 1,000, so markets were sampled from the top **1,500** resolved
  binary markets (not 2,000). Bets were paged up to 10,000 per market, not 2,000, so that "first bet per user" is
  correct; the 2 markets with more bets were dropped (`truncated`). About 1,930 requests were made
  (`results/E03/fetch_stats.json`).
- **Extra real-data diagnostics (exploratory, not pre-registered):** a late-bet signature, a "selection habit" check,
  a top-decile cut for "near-certain-heavy" users, a sensitivity run without market creators' own bets, and a
  compact ledger with hashed user IDs.

## 4. How to run
```bash
# Part A: simulation (about 25 s per condition on 10 cores; exploratory strong run about 3 min)
for c in main R1 R2 R3; do uv run python -I experiments/E03_track_record/sim.py --cond $c --seeds 10 --workers 10; done
uv run python -I experiments/E03_track_record/sim.py --cond main --seeds 10 --workers 10 --strong
uv run python -I experiments/E03_track_record/analyze_sim.py        # tables, kill test, fig1
# Part B: Manifold (fetch is cached and resumable, about 25 min at 3 requests/s)
uv run python -I experiments/E03_track_record/fetch_manifold.py --n-markets 700
uv run python -I experiments/E03_track_record/real.py               # main analysis + fig2
uv run python -I experiments/E03_track_record/real.py --all-buys --boot 200
uv run python -I experiments/E03_track_record/real.py --no-creator --boot 200
```
Code: `rules.py` (all 13 scoring rules, shared), `sim.py` (worlds, honest sources, hand-coded cheats, CEM learning
cheater), `analyze_sim.py`, `fetch_manifold.py`, `real.py`. Logs are in `results/E03/run.log` and
`results/E03/fetch.log`.

## 5. Results
n for the simulation: 10 seeds per condition. Each seed has 40 training and 20 held-out test worlds, and each world
has 3,000 events and 200 honest sources. A seed's percentile is the mean over 20 test worlds × 3 replicate draws.
CIs are 95% bootstrap CIs over the 10 seeds. "Percentile" means the share of the 200 honest skilled sources that the
zero-skill cheater outscores (50 = the median honest source).

### 5.1 Kill test (simulation): passed
`results/E03/killtest_sim.json`: the learned cheater is above the median under **both** ACC and BRIER (CI entirely
above 50), and four pre-registered rules hold it below the median (CI entirely below 50): IG, EB-IG, EB0-IG and IG-SUM.
**Signal present.**

### 5.2 How far a learned zero-skill cheater climbs, by rule (main condition)
Source: `results/E03/sim_summary.csv` (rows `cond == main`); figure `results/E03/fig1_cheater_inflation.png`.

| rule | learned cheater percentile [95% CI] | share of test worlds above median | best of 10 hand-coded cheats (percentile) | copy-the-crowd | honest skill recovery: Spearman(k, score) |
|---|---|---|---|---|---|
| ACC | **98.9** [98.7, 99.0] | 1.00 | cherry+extremize (99.1) | 32.6 | 0.27 |
| BRIER | **99.8** [99.7, 99.9] | 1.00 | cherry-pick (99.8) | 29.5 | 0.33 |
| LOG | 99.8 [99.7, 99.9] | 1.00 | cherry-pick (99.8) | 29.2 | 0.34 |
| DW-ACC | 98.0 [97.5, 98.4] | 0.99 | cherry+extremize (99.0) | 29.6 | 0.30 |
| DW-BRIER | 99.8 [99.6, 99.9] | 1.00 | cherry-pick (99.9) | 24.3 | 0.40 |
| TOPIC-BRIER | 99.8 [99.6, 99.9] | 1.00 | cherry-pick (99.3) | 29.3 | 0.34 |
| EB-BRIER | 100.0 [100.0, 100.0] | 1.00 | cherry-pick (99.9) | 27.2 | 0.41 |
| BSS | **69.4** [59.9, 77.5] | 0.67 | low-vol-gamble (20.2) | 13.1 | 0.53 |
| IG | 27.3 [23.6, 30.9] | 0.33 | low-vol-gamble (17.3) | 12.3 | 0.55 |
| EB-IG | 41.2 [40.4, 41.9] | 0.15 | low-vol-gamble (23.3) | 8.1 | 0.62 |
| EB0-IG | **10.8** [10.2, 11.5] | 0.00 | copy-crowd (12.3) | 12.3 | 0.46 |
| IG-SUM | **10.7** [9.6, 11.7] | 0.00 | copy-crowd (12.3) | 12.3 | 0.37 |
| BRIER-GAIN * | 19.9 [17.4, 22.4] | 0.17 | low-vol-gamble (17.3) | 13.1 | 0.53 |

Skill recovery is the Spearman correlation between honest sources' true skill k and their score, over 50 fresh
worlds (CIs are all within ±0.02; `skill_rho_lo/hi` in the same file). Absolute rules are both gameable *and* poor at
recovering honest skill (ρ ≈ 0.27–0.41). Crowd-relative rules do better on both counts (ρ ≈ 0.37–0.62).

**What the learner found that hand-coding missed.** For the absolute, difficulty-weighted and per-topic rules, plain
cherry-picking already reaches the ceiling. Learning matters for the "robust-looking" rules:
- **BSS (ratio skill score): 69.4 learned vs 20.2 for the best hand-coded cheat.** The learned policy
  (`results/E03/sim_learned_policies.csv`) makes about 11 claims, all on events where the crowd is ≥ 95%, and
  extremizes mildly (α ≈ 1.3). When every favourite wins, ΣBrier(r) ≪ ΣBrier(c), so BSS is close to 1 and beats nearly
  every honest source. When one upset happens, BSS is only slightly negative. The percentile is therefore roughly the
  probability that all ~11 favourites win. The ratio form is not an average of proper-score differences, so the
  zero-skill bound does not apply. Rewriting it as a difference (BRIER-GAIN*) drops the cheater to 19.9 [17.4, 22.4].
- **EB-IG (shrink toward the population mean): 41.2 vs 23.3.** The learned policy makes the minimum 10 claims and
  roughly copies the crowd (α ≈ 1.1). Shrinkage then hands it about the population-mean IG (κ: median 151, IQR 103–337 across 200 test worlds;
  `results/E03/sim_eb_constants.json`), which places it just under the median. Shrinking toward the zero-skill baseline
  instead (EB0-IG) holds it at 10.8.
- **IG (mean): 27.3 vs 17.3.** The learner makes 10 claims on events where the crowd is 80–95%, extremized (α ≈ 3). This
  is the rank-competition variance gamble known from Lichtendahl & Winkler (2007): it loses IG in expectation but
  sometimes lands in the top half (33% of test worlds).
- **EB0-IG and IG-SUM** resisted every attack: no learned or hand-coded cheat beat copying the crowd (12.3), and the
  cheater was never above the median in any test world.

### 5.3 Robustness and optimizer strength
Source: `results/E03/sim_summary.csv` (learned-cheater percentile, mean [95% CI over 10 seeds]).

| rule | main | R1 miscalibrated honest | R2 crowd with longshot bias | R3 min 30 claims | main, ~5× CEM budget |
|---|---|---|---|---|---|
| ACC | 98.9 [98.7, 99.0] | 98.9 [98.8, 99.0] | 99.3 [99.2, 99.4] | 100.0 [99.9, 100.0] | 98.8 [98.4, 99.0] |
| BRIER | 99.8 [99.7, 99.9] | 99.7 [99.6, 99.8] | 99.9 [99.9, 99.9] | 100.0 [100.0, 100.0] | 99.9 [99.8, 99.9] |
| BSS | 69.4 [59.9, 77.5] | 73.8 [70.5, 77.2] | 74.5 [67.0, 81.5] | 44.7 [39.8, 48.9] | 73.8 [69.2, 78.4] |
| IG | 27.3 [23.6, 30.9] | 28.3 [25.5, 31.4] | 40.2 [37.1, 43.7] | 11.6 [10.2, 13.2] | 25.3 [22.1, 28.5] |
| EB-IG | 41.2 [40.4, 41.9] | 43.2 [42.4, 44.1] | 42.8 [41.4, 44.3] | 32.3 [31.7, 32.8] | 42.0 [41.4, 42.5] |
| EB0-IG | 10.8 [10.2, 11.5] | 20.3 [19.6, 21.0] | **46.0** [43.9, 48.0] | 6.7 [6.1, 7.2] | 9.2 [7.5, 10.8] |
| IG-SUM | 10.7 [9.6, 11.7] | 20.1 [19.5, 20.7] | **81.9** [80.7, 83.0] | 7.0 [6.6, 7.3] | 10.8 [10.0, 11.5] |
| BRIER-GAIN * | 19.9 [17.4, 22.4] | 21.3 [18.2, 24.5] | 28.1 [25.2, 31.6] | 9.7 [8.8, 10.7] | 19.6 [17.5, 21.5] |

- **R1:** the ranking of rules is unchanged. Relative rules sit at the copy-the-crowd level (20.6 under R1, because
  miscalibrated honest sources lose IG).
- **R2 is the main failure mode of the crowd-relative family.** When the crowd prior has a predictable bias, a
  zero-private-information source can earn positive IG by recalibrating it. The learned IG-SUM cheater floods (median
  ~994 claims) with α = 1.31, almost exactly the inverse of the injected bias (1/0.75 = 1.33;
  `sim_learned_policies.csv`, rows R2), and reaches the 81.9th percentile. This *is* information relative to the
  published crowd, but it is information about the crowd's bias, not about the world. Crowd-relative rules are only
  as cheat-proof as their baseline is calibrated.
- **R3:** a 30-claim minimum removes most of the variance gambles (IG 11.6, EB0-IG 6.7) but not the BSS ratio exploit
  (44.7) or cherry-picking under absolute rules.
- **Optimizer strength:** about 5× more search did not change any rule's verdict (all CIs overlap with main). This
  suggests the resistant rules are not resisting only because the optimizer is weak. It is still a lower bound on
  exploitability, not a proof.

Transfer (cheater trained on rule X, scored by rule Y): `results/E03/sim_transfer_main.csv`. A cheater trained on BSS
also scores 95.3 on ACC and 91.9 on BRIER. One trained on ACC scores 13.3 on IG and 9.9 on EB0-IG.

### 5.4 Why some rules resist (mechanism)
1. **Crowd-relative proper scores are selection-proof in expectation.** Let F be what the cheater sees when it claims
   an event and c = P(y = 1 | F) the crowd prior. For any proper score S and any F-measurable choice of whether to
   claim (z) and what to state (r), E[z·(S(r, y) − S(c, y))] = E[z·E[S(r, y) − S(c, y) | F]] ≤ 0. So which events,
   how many and what probability cannot raise the *expected* IG, BRIER-GAIN or IG-SUM of a zero-skill source above 0.
   Copying the crowd is optimal in expectation.
2. **Absolute scores are not.** E[Brier | copy crowd] = c(1 − c) and E[accuracy | follow crowd] = max(c, 1 − c). Both
   improve as the claimed events get easier, so cherry-picking is optimal. Per-source normalized difficulty weights
   (Σw·x/Σw) cancel when every claimed event is easy. Per-topic normalization removes base-rate differences between
   topics but not selection within a topic.
3. **What remains is variance, which rank-based leaderboards reward.** Two aggregations neutralize it: summing
   (IG-SUM, like Metaculus's summed peer scores) and shrinking toward 0 (EB0-IG). Two do not: a ratio (BSS), which is
   not an expectation of per-claim differences, and shrinking toward the population mean, which gives an unknown
   source the average source's credit.
4. **The bound needs a calibrated, pre-claim baseline** (R2). Practical fix (untested here): recalibrate the crowd on
   past resolved questions before using it as the baseline.

### 5.5 Real data: Manifold Markets (real-data kill test: passed)
Source: `results/E03/real_summary_main.json`, `results/E03/real_stability_main.csv`,
`results/E03/real_rule_corr_main.csv`, figure `results/E03/fig2_manifold.png`; derived ledger
`results/E03/real_claims_main.csv.gz` (hashed user IDs).

- **Collected:** 698 resolved YES/NO markets (2 dropped as truncated), 884,556 raw bets (`fetch_stats.json`) and
  528,404 filled buys. That gives **168,701 dated, attributed, resolved claims** (first buy per user and market) from
  28,704 users, dated 2021-12-28 to 2026-11-12. This is far above the 500-claim threshold. Analysed: **83,298 claims
  from 1,855 users with ≥ 20 claims.** Topics: politics 36,209, AI/tech 22,887, other 8,712, econ/finance 6,946,
  Manifold/personal 3,574, sports 2,270, science/health 1,940, culture 760.
- **Two near-orthogonal families.** User rankings under the absolute rules agree with each other (BRIER vs LOG
  ρ = 0.99, vs TOPIC-BRIER 0.99, vs EB-BRIER 0.97). So do rankings under the crowd-relative rules (IG vs BSS 0.96,
  vs IG-SUM 0.98). Across families they barely agree (BRIER vs IG ρ = 0.10), and ACC sits between them (vs IG
  ρ = 0.35).
- **(a) Split-half rank stability** (Spearman ρ, n = 1,855 users; random split = mean of 20 splits, early-vs-late =
  temporal split; 95% bootstrap CI over users, 500 resamples):

| rule | random split ρ [CI] | early vs late ρ [CI] |
|---|---|---|
| ACC | 0.35 [0.32, 0.38] | 0.32 [0.28, 0.36] |
| DW-ACC | 0.23 [0.19, 0.25] | 0.19 [0.15, 0.24] |
| EB-BRIER | 0.12 [0.07, 0.14] | 0.12 [0.07, 0.17] |
| BRIER | 0.10 [0.05, 0.12] | 0.10 [0.05, 0.14] |
| LOG | 0.10 [0.05, 0.12] | 0.09 [0.05, 0.14] |
| TOPIC-BRIER | 0.09 [0.04, 0.11] | 0.09 [0.05, 0.14] |
| DW-BRIER | 0.04 [−0.01, 0.07] | 0.06 [0.01, 0.11] |
| IG-SUM | 0.10 [0.07, 0.15] | 0.06 [0.01, 0.11] |
| EB-IG / EB0-IG | 0.10 [0.07, 0.14] | 0.07 [0.02, 0.11] |
| IG | 0.07 [0.04, 0.12] | 0.07 [0.02, 0.11] |
| BSS | 0.07 [0.04, 0.12] | 0.06 [0.01, 0.11] |
| BRIER-GAIN * | 0.08 [0.05, 0.12] | 0.07 [0.02, 0.11] |

  (The random-split CI is bootstrapped over 5 of the 20 splits, so the point estimate can sit near its edge. The
  population mean IG on Manifold is about 0 bits (−0.0001), so EB-IG and EB0-IG coincide here.)
- **Accuracy is the most stable rule, but it measures a selection habit.** The average crowd probability of the side a
  user bets on is itself stable (early vs late ρ = 0.56 [0.52, 0.59]). It correlates ρ = 0.70 with ACC and ρ = −0.06
  with IG (`real_summary_main.json` → `selection_habit`). On real data, stability is not validity.
- **(b) Gaming signature (pre-registered): present.** Across users, the share of claims on a ≥ 90% favourite
  correlates with (ACC percentile − IG percentile) at **ρ = 0.42 [0.38, 0.45]** (n = 1,855). The top decile of users by
  near-certain share (n = 188, share ≥ 18.5%) has a median **ACC percentile of 86.5** but a median **IG percentile of
  52.9**. Most top-accuracy users are not pure gamers, though: the top ACC decile (n = 186) has a median IG percentile
  of 69.9, and 25.8% of them are below the median on IG.
- **Exploratory:** late bets (last 10% of a market's life, 12.6% of claims) do *not* predict the ACC−IG gap (ρ = 0.01
  [−0.03, 0.06]). The 38 mostly-API (bot) accounts sit near the median on every crowd-relative rule (IG percentile
  50.7) and lower on the absolute rules (BRIER 34.0).
- **Sensitivity** (`real_summary_main_nocreator.json`, `real_summary_main_allbuys.json` and the matching
  `real_stability_*.csv`): dropping market creators' own bets changes nothing material (signature ρ = 0.42
  [0.39, 0.45]). Using all buys (438,615 claims, 3,428 users) keeps the signature (ρ = 0.39 [0.37, 0.43]) and raises
  early-vs-late stability (ACC 0.45, IG 0.21). Random-split stability rises more, but repeated bets on the same market
  then land in both halves, so that number is inflated.

## 6. Verdict
**KEEP**, with a reframing. The pre-registered signal is present. A learned zero-skill cheater reaches the 98.9th
(ACC) and 99.8th (BRIER) percentile of honest skilled sources, while IG, EB-IG, EB0-IG and IG-SUM hold it below the
median (EB0-IG 10.8, IG-SUM 10.7). The real-data arm passes its kill test with 168,701 claims, and the pre-registered
gaming signature is present (ρ = 0.42). The ACC/BRIER inflation alone is close to obvious, and selection incentives
under Brier are already documented (Sempere & Lawsen 2021). The novel contribution is the **learned-attacker audit**.
It found two exploits of rules that look robust and that our 10 hand-coded cheats missed: the BSS ratio (69 vs 20)
and shrinkage toward the population mean (41 vs 23). It also showed that every crowd-relative rule fails when the
baseline is predictably miscalibrated (IG-SUM 82 under R2).

## 7. Next steps
- **Full paper framing:** "Which reliability score survives a learning cheater?" Contributions: (i) a ranking of 13
  rules by learned-cheater inflation, (ii) the three-part mechanism in §5.4, (iii) a recommended rule (crowd-relative
  difference score, summed or shrunk to 0, minimum volume, time-stamped and recalibrated baseline), and (iv) the
  Manifold evidence that accuracy leaderboards reward a stable selection habit.
- **Close R2:** add a "recalibrated crowd" baseline (fit the crowd's calibration curve on past resolved markets) and
  show that it restores resistance. Also test a cheater that sees more public features than (c, topic), such as time
  to close or market liquidity.
- **Real data:** Metaculus (the API needed a token, so it was not tried) to get stated probabilities rather than
  market moves; longer user histories for crowd-relative rules (stability ≈ 0.07 at ≥ 20 claims is too noisy to rank
  individuals); backtest a recalibrated-baseline IG on Manifold.
- **Stronger attackers:** a policy-gradient cheater with per-event features, adaptive attackers against a scorer that
  is re-fit each round (bilevel), and a top-k-prize objective instead of expected percentile, which rewards variance
  more.
- **GRPO version:** a small LM acts as a "pundit" that picks which questions from a resolvable-question pool to make
  claims on and states probabilities, rewarded by its ledger percentile. Does it rediscover cherry-picking, the BSS
  ratio exploit and shrink-to-mean entry? Does it stop under EB0-IG or IG-SUM? That needs LLM calls via `epi.llm`
  (tag E03) or local GRPO on the RTX 3080.

## 8. Spend, limitations, prior work
**Spend:** 0 LLM calls, $0 for tag E03 (`uv run python -m epi.llm` shows no E03 spend). CPU: about 2 min for the four
main conditions and about 4 min for the strong run, on 10 cores. About 1,930 HTTP GET requests to the public Manifold
API at ≤ 3 per second, plus about 4 manual probes (`results/E03/fetch_stats.json`).

**Data hygiene:** the raw API cache in `results/E03/data/manifold/` is about 0.71 GB and contains Manifold user IDs.
We suggest *not* committing it; the hashed derived ledger `real_claims_main.csv.gz` (5 MB) is enough to reproduce
§5.5 apart from re-hashing.

**Limitations and threats to validity.**
- *Simulation assumptions:* Gaussian log-odds world; honest sources pick events uniformly at random and are calibrated
  (except R1); the crowd is calibrated (except R2); the cheater sees only (crowd prior, topic). With richer public
  features, or if honest sources also select, absolute rules become noisier still but the theory for relative rules
  is unchanged.
- *CEM is a lower bound on exploitability.* Seeds vary (BSS: 39 to 89 across seeds), and EB0-IG's learned cheater
  ended slightly *below* copy-the-crowd, i.e. under-optimized. The ~5× run did not change the conclusions.
- *Reward choice:* expected percentile. A winner-take-all objective would favour variance more.
- *EB constants:* the method-of-moments τ² hit its floor (complete pooling) in 38.5% of worlds for Brier and 7.5% for
  IG (`sim_eb_constants.json`). This is realistic for MoM, but a better estimator could change EB-BRIER/EB-IG
  numbers. It does not change EB0-IG's guarantee.
- *Population statistics* (topic means, EB) are fit on honest sources only; one cheater among 200 barely moves them.
- *Manifold:* play money; a bet is not a stated belief, so we use the post-bet price as the "stated probability" and
  IG then measures market impact, which scales with bet size. The sample is popularity-biased (top 1,500 resolved
  markets with 20–500 bettors). The topic mapping is a crude keyword match. There is no ground-truth skill, so the
  real data can show stability and signatures but not which rule is *right*. The share of claims on near-certain
  favourites is a correlational signature, not proof of intent.

**Dual use.** The learned policies are recipes for gaming reliability leaderboards (cherry-picking, low-volume
ratio-gaming, shrink-to-mean entry, baseline recalibration-flooding). Each attack is reported together with a rule
that resists it, which favours defenders. We publish no per-user labels: user IDs are hashed, and the signature is
reported only as an aggregate.

**Prior work found** (web search on 2026-11-14; abstracts or summaries read, not full texts):
- Sempere & Lawsen (2021), *Alignment Problems With Current Forecasting Platforms*, arXiv:2106.11248. Shows
  question-selection incentives under Brier and relative Brier scores; notes that maximizing summed relative scores
  removes them. This is the closest prior work for the cherry-picking result.
- Lichtendahl & Winkler (2007), *Probability Elicitation, Scoring Rules, and Competition Among Forecasters*,
  Management Science 53(11):1745–1755. Competition makes forecasters extremize; this explains our IG variance gamble.
- Witkowski, Freeman, Vaughan, Pennock & Krause, *Incentive-Compatible Forecasting Competitions*, AAAI 2018; Management
  Science 69(3):1354–1374 (2023). Proposes the ELF lottery mechanism for winner-take-all competitions.
- Murphy (1973) on hedging and skill scores, via Jolliffe & Stephenson (2008): skill scores are generally improper.
  Our BSS exploit is a learned, source-level instance of this.
- Hanson (2003), *Combinatorial Information Market Design*, Information Systems Frontiers 5(1). IG over the crowd is
  the logarithmic market-scoring-rule payoff.
- Metaculus Scores FAQ (metaculus.com/help/scores-faq): the peer score is a log-score difference against other
  forecasters, summed across questions, which is the analogue of our IG-SUM.
- Not found: prior work that trains an adaptive (learning) zero-skill source against a panel of reliability scores
  and ranks the scores by learned inflation. The search was brief, so this needs a proper literature check before
  any novelty claim.
