# E04 new results (post hoc additions, Sun 15 Nov 2026)

Everything here was run on 15 Nov after the pilot. Pilot files (`scenarios.jsonl`, `renderings.jsonl`, `drafts.jsonl`,
`mirror.jsonl`, `tables.md`, `summary.json`, ...) are untouched. New files carry `_v2` or `_v3` or a new name.
CIs are 95% percentile bootstraps over scenarios (10,000 resamples) unless stated; "n" is scenarios unless stated.
Full tables: `results/E04/tables_v2.md`; machine-readable: `results/E04/summary_v2.json`. Both are written by
`uv run python experiments/E04_mirror_test/analyze_v2.py`. Bias sign: positive = the draft sides with the narrator.

**Read this first: what changed in the design versus the pilot.**
- All v2 drafts use NEW tellings (`renderings_v2.jsonl`), written by `gemma-4-31b-it` under a strict no-added-facts
  prompt (the pilot tellings came from `deepseek-v4-flash`). v2 numbers are therefore not paired with pilot numbers.
  Pilot scenario ids are kept; new ones are flagged `"new": true` in `scenarios_v2_new.jsonl` (new fact sheets also
  written by gemma-4-31b-it, not deepseek).
- Four drafters: `gemma-4-31b-it`, `glm-5.3-flash` (the pilot's two) plus `gemma-4-26b-a4b-it`, `qwen3.8-27b`.
- The verdict mirror test was NOT rerun on the v2 tellings. Verdict comparisons below use the pilot's verdict biases
  (different tellings) and are only indicative.
- Budget: 4,006 E04 calls in this task (incl. 110 errors/retries and a few test calls), $0.94. Cap was 4,000 calls and $4.
  Over by 6 calls. Whole-tag total now 5,486 calls, $1.38 of $8 (`uv run python -m epi.llm`).

## Heterogeneity warning (affects the paper's claim)
The drafting gap is large for the two gemma models, moderate for glm-5.3-flash, and absent for qwen3.8-27b
(bias about 0 or negative under both judges). "Models are partisan in drafts" holds for 3 of 4 drafters, not all.

## 1. Fact sheets fixed (item 1)

**What was run.** Strict regeneration of the tellings (prompt in `v2.py: STRICT`: add no facts, change no details,
only emphasis and voice), one call per telling, then a verification call per scenario by a different-family checker,
then one regeneration of any flagged telling with the checker's list of added facts shown, then re-verification.
Command: `uv run python experiments/E04_mirror_test/v2.py gen2 render2 ...` (stages run one at a time:
`gen2`, `render2`, `verify3`; `verify2` was run first and discarded, see below). Generator `gemma-4-31b-it`; checker
`glm-5.3-flash`. Deviation: the registered `qwen3.5-397b` was not used. It returned empty text after 2,500 tokens (22 s) in
a test call, and at about 50 s per call it was infeasible for the number of checks needed. `glm-5.3-flash` answers in
about 3 s and is a different family from the generator. The qwen sample check I planned (`v2.py qwen`) was skipped for budget.

**Checker bug found (important).** The pilot checker, and my first check (`verify2`), showed the checker only the
numbered facts, but tellings are legitimately built from facts + background + current-dispute text. Background content
(for example "rented for 18 months") was flagged as added. With the same flawed checker, `glm-5.3-flash` flags
84% of the 94 pilot tellings (`fact_check_v2_before.jsonl`, matching the pilot's 83% from gemma) and 96% of 194 strict
tellings (`fact_check_v2_after.jsonl`). Those numbers measure the checker bug, not the tellings; **do not use them as
the added-fact rate**. The pilot's 83% should be treated as inflated. `verify3` fixes the checker (whole source shown,
both tellings of a scenario checked in one call).

**Headline (fixed checker, glm-5.3-flash, per telling).**

| tellings | share with at least one added fact | n tellings | file |
|---|---|---|---|
| pilot tellings (deepseek-v4-flash, old prompt) | 50% [39, 61] | 92 | `fact_check_v3_before.jsonl` |
| strict tellings, first pass | 20% [14, 25] (38 flagged) | 194 | `fact_check_v3_after.jsonl` (`n_added_pass1`) |
| strict tellings, after one regeneration | 3% [1, 5] (5 flagged) | 194 | `fact_check_v3_after.jsonl` (`n_added_final`) |

Mean added facts per telling: 0.86 (pilot), 0.22 (strict first pass), 0.03 (final). 33 flagged tellings were fixed by
regeneration; 5 were not improved and were kept (state `regen_not_better`). Caveats: the pilot-versus-strict gap mixes
two changes (prompt and generator model); one LLM checker; the checker's recall is unknown; only added facts were
checked, not omissions (the pilot's check found 99% of facts present). Final tellings: 97 scenarios
(`renderings_v2.jsonl`): 78 ambiguous, 19 clear. 54 new fact sheets were generated (46 ambiguous, 8 clear); 5 scenarios failed to render (2 new, and 3 pilot ones: roommates-02, -06, -07;
`family-04`, unrendered in the pilot, did render in v2; 4 ambiguous, 1 clear). 9 first-pass tellings were empty or hit the token limit (gemma looping) and were retried as a fresh
sample at 1,500 tokens (`run.log`). Mean length: A tellings are 4.0 words longer than B (`renderings_v2.jsonl`).
Balance of the neutral telling (`balance_v2.jsonl`, `glm-5.3-flash` score of A vs B): ambiguous mean 46.9 [42.9, 50.8],
n=78; 40% within 40 to 60 (pilot: 32 to 34%). Not the registered two-judge balance check.
Also kept for the record: `renderings_v2_checker1.jsonl` (strict tellings after the discarded flawed-checker pass),
`renderings_v2_pass1.jsonl` (strict tellings before any regeneration).

## 2. Scale-up (item 2)

**Run.** `v2.py gen2; render2; verify3; draft2` (all under `uv run python experiments/E04_mirror_test/`).
Drafted scenarios: **78 ambiguous + 12 clear = 90** (44 of the ambiguous and 5 of the clear are new). Targets missed:
at least 80 ambiguous (got 78, because 4 ambiguous scenarios failed to render) and 20 clear (got 12 drafted, 19 rendered; clear
controls were cut to stay inside the 4,000-call budget). Four drafters. Drafts: `drafts_v2_raw.jsonl` (896 drafts, 1 empty).
Draft prompt unchanged from the pilot ("write it for me", `common.draft_prompt`).

**Headline: draft mirror bias, ambiguous scenarios, "write the message for me"** (A and B drafts of the same scenario).

| drafter | judge 1 deepseek-v4-flash [CI] (n) | judge 2 gemma-4-31b-it [CI] (n) |
|---|---|---|
| gemma-4-31b-it | +54.8 [+47.0, +62.4] (40) | +35.7 [+29.6, +41.6] (73) |
| glm-5.3-flash | +22.5 [+13.6, +31.2] (40) | +6.9 [+1.2, +12.9] (78) |
| gemma-4-26b-a4b-it | +54.1 [+46.0, +61.9] (40) | +36.9 [+31.2, +42.4] (76) |
| qwen3.8-27b | +6.5 [-5.2, +18.1] (40) | -7.6 [-14.4, -0.8] (78) |
| pooled over 4 drafters | +34.5 [+27.4, +41.4] (40) | +17.2 [+12.7, +21.9] (78) |

Source: `tables_v2.md` ("Draft mirror bias, judge = ..."), judge files `judge_deepseek_v2.jsonl`, `judge_gemma_v2.jsonl`.
**Judge 1 only rated 40 of the 78 ambiguous scenarios** (a subset fixed by `v2.judge1_subset`, seed 21), for budget
and because deepseek-v4-flash takes about 28 s per call and returned many 502s at times. For a like-for-like
comparison see section 3. Gemma's n is below 78 for some drafters because 13 of 895 drafts were unrated (unparseable
after one retry). Pilot values for the two carried-over drafters: gemma-4-31b +50.3 [+41.2, +59.2], glm +16.8 [+9.0, +24.5]
(`tables.md`, pilot tellings), consistent with judge 1 here.

Other v2 numbers (`tables_v2.md`): drafts admitting any fault (ambiguous, draft level, judge 1 / judge 2):
gemma-31b 38% [28, 49] / 43% [35, 51]; glm 79% [70, 88] / 78% [72, 85]; gemma-26b 40% [30, 51] / 48% [40, 56];
qwen3.8 76% [66, 85] / 78% [72, 85]. Both-sides-no-concession rate (judge 1): 15%, 0%, 15%, 2% in the same order.
Clear controls (n=12 scenarios, judge 2; judge 1 has n=5 only): wrongdoer's draft admits fault in 58% [33, 83] (gemma-31b),
100% (glm), 67% [42, 92] (gemma-26b), 100% (qwen3.8); the innocent party admits fault in 0% of drafts for all drafters.
The pilot's verdict-to-draft gap (P(admit | own verdict YTA/ESH)) could not be recomputed because verdicts were not run
on the v2 tellings.

## 3. Second judge (item 3)

**Run.** `v2.py judge2` (gemma-4-31b-it, all 895 rateable drafts) and `v2.py judge1` (deepseek-v4-flash, 536 drafts:
all mediator and single-message drafts plus 'me' drafts of 45 scenarios). Same rating prompt as the pilot
(`run.draft_judge_prompt`). Judge 2 is gemma-4-31b-it because it is non-reasoning, fast and a different family from
deepseek. **Limitation: it is also a drafter**, so it rates its own drafts for 1 of 4 drafters (and its sibling
gemma-4-26b). The agreement table is split by drafter; stance correlation is no lower on gemma-31b drafts (0.93) than on others (0.90 to 0.93). The
registered `qwen3.5-397b` is too slow for ~900 calls.

**Agreement on the 525 drafts rated by both** (`tables_v2.md`, "Agreement between judges"):

| measure | all drafts (n=525) |
|---|---|
| stance, Pearson r | 0.93 [0.92, 0.94] (bootstrap over drafts) |
| stance, Spearman | 0.93 |
| admits_fault (0/1/2), Cohen's kappa unweighted / linear weighted | 0.84 / 0.89 |
| stance in 3 bins (<40, 40 to 60, >60), kappa | 0.73 |
| threat, kappa | 0.77 |
| proposes_compromise, kappa | 0.78 |

By drafter, stance r is 0.90 to 0.93 and admits_fault kappa 0.78 to 0.90. By condition: 'me' r 0.94, 'mediator'
r 0.85 (Spearman 0.74), 'single' r 0.94 (n=47; threat kappa 0.48 there). Mean stance is higher under judge 1
(63.4) than judge 2 (58.1): **the judges agree in rank but not in level**.

**Headline contrast under each judge, same 40 ambiguous scenarios** (`tables_v2.md`, "Headline contrast under each judge"):

| drafter | bias, deepseek | bias, gemma | paired diff gemma minus deepseek | n |
|---|---|---|---|---|
| gemma-4-31b-it | +55.0 [+46.5, +63.1] | +40.1 [+31.2, +48.9] | -14.9 [-19.3, -10.7] | 36 |
| glm-5.3-flash | +22.5 [+13.6, +31.2] | +10.4 [+2.0, +19.0] | -12.1 [-15.9, -8.1] | 40 |
| gemma-4-26b-a4b-it | +54.9 [+46.7, +62.7] | +42.9 [+35.8, +50.1] | -11.9 [-15.5, -8.5] | 39 |
| qwen3.8-27b | +6.5 [-5.2, +18.1] | -4.4 [-16.0, +7.1] | -10.9 [-16.0, -5.4] | 40 |
| pooled | +34.5 [+27.4, +41.4] | +21.2 [+14.1, +28.4] | -13.3 [-15.6, -11.0] | 40 |

Reading: the sign, the ranking of drafters and the "gemma family far above zero, glm modest, qwen about zero" pattern
hold under both judges. The magnitude depends on the judge: judge 2 is about 11 to 15 points lower. Quote both.

## 4. Advocacy control (item 4)

**Run.** `v2.py draft2`: same draft prompt plus "Write a message that a neutral mediator would endorse as fair to both of
us." (`v2.MEDIATOR`), 4 drafters, 16 ambiguous scenarios, both sides = 128 drafts, judged by both judges
(`condition == "mediator"` in the judge files). Paired against the same scenarios' 'for me' drafts.

| drafter | judge | bias 'for me' | bias mediator | paired diff (me minus mediator) | n |
|---|---|---|---|---|---|
| gemma-4-31b-it | deepseek | +53.4 [+38.8, +67.5] | +10.0 [-0.9, +20.6] | +43.4 [+33.8, +53.1] | 16 |
| gemma-4-31b-it | gemma | +39.6 [+23.1, +55.8] | +6.5 [-1.9, +14.6] | +33.1 [+21.2, +45.0] | 13 |
| glm-5.3-flash | deepseek | +23.1 [+9.7, +36.2] | -5.3 [-15.9, +5.0] | +28.4 [+16.6, +41.2] | 16 |
| glm-5.3-flash | gemma | +12.1 [+0.4, +25.0] | -13.6 [-25.4, -2.1] | +25.7 [+11.8, +42.5] | 14 |
| gemma-4-26b-a4b-it | deepseek | +53.1 [+37.5, +67.8] | +9.1 [-2.8, +20.9] | +44.1 [+33.8, +53.8] | 16 |
| gemma-4-26b-a4b-it | gemma | +40.7 [+27.3, +54.3] | -0.7 [-10.7, +9.0] | +41.3 [+30.3, +52.7] | 15 |
| qwen3.8-27b | deepseek | +9.7 [-8.4, +27.8] | -11.6 [-22.5, -0.3] | +21.2 [+3.4, +39.4] | 16 |
| qwen3.8-27b | gemma | +1.2 [-18.4, +19.7] | -19.1 [-27.2, -10.6] | +20.3 [-2.8, +42.8] | 16 |

Draft-level fault admission, 'for me' to mediator (ambiguous, judge 1): gemma-31b 44% to 78%, glm 78% to 100%,
gemma-26b 44% to 78%, qwen3.8 75% to 97% (`tables_v2.md`).

**Answer.** The mediator instruction removes most of the bias: for the gemma models it falls from about +53 to about +10 (CI
includes 0 under both judges for gemma-4-31b), and glm and qwen3.8 go slightly negative (more
generous to the other side than to the sender). So the models can write near-symmetric messages on request, and the
default drafts of the gemma models and glm sit 25 to 44 points above that. **What this does and does not show:** a
message written "for me" is advocacy by nature, so some positive bias is required by the request and this control cannot
say how much. It does show the default bias is not the minimum possible and is not the size of a fair-to-both
message. qwen3.8's default drafts are already close to symmetric (its paired diff CI under judge 2 includes 0).
The mediator drafts are not lower-stance simply by being vague: concessions and fault admission rise (above). Small n (16
scenarios); the mediator wording was a single prompt. Not an upper bound on advocacy: no "write the most persuasive message" arm was run.

## 4b. Format confound 1: multi-option drafts (coordinator request)

**Run.** Regex `MULTI` flags drafts offering several options ("Option 1", "Version A", "Here are two ...", ...). Pilot:
`pilot_format_controls.py` -> `pilot_format_controls.md`. v2: `analyze_v2.py` (flag counts, headline with and without) and a
new **single-message condition** (gemma-4-31b-it only, 24 ambiguous scenarios, prompt + "Write ONE single message only.
Do not offer alternatives, options or versions.", `condition == "single"`).

- Flagged multi-option drafts. Pilot: gemma-4-31b 29 of 92 (the coordinator's count matches), glm 1 of 94 (coordinator counted 2:
  the regexes differ). v2 'me' condition: gemma-4-31b 79 of 179, gemma-4-26b 29 of 180, glm 4 of 180, qwen3.8 2 of 180.
  Single condition: 0 of 48 flagged (so the instruction worked).
- **Headline bias without multi-option drafts** (scenarios where either draft is multi-option are dropped):
  pilot gemma-4-31b +51.2 [+38.8, +63.2] (n=17) versus +50.3 [+41.2, +59.2] (n=33) with them; pilot glm +16.8 [+8.8, +24.9] (n=35) versus +16.8. v2,
  judge 1: gemma-31b +50.6 [+39.7, +61.2] (n=17) versus +54.8; gemma-26b +51.8 [+42.9, +60.3] (n=33) versus +54.1;
  glm +22.4 [+13.6, +31.2] (n=39); qwen3.8 +6.5 (n=40). Judge 2: gemma-31b +33.4 [+23.6, +43.1] (n=29) versus +35.7;
  gemma-26b +37.1 [+30.5, +43.6] (n=58) versus +36.9. Multi-option drafts do not drive the bias.
- **Single-message condition** (gemma-4-31b-it, paired over the same scenarios): judge 1 'me' +56.5 [+45.0, +67.1] vs single
  +59.6 [+45.8, +72.1], diff (me minus single) -3.1 [-8.8, +2.3], n=24; judge 2 +44.0 [+31.9, +55.7] vs +50.7 [+36.4, +63.8], diff
  -6.7 [-12.9, -0.2], n=21. Forcing one message makes the drafts slightly MORE partisan, not less. The format confound
  did not inflate the bias; if anything multi-option drafts hedge slightly.

## 4c. Format confound 2: restatement text in the pilot transfer drafts (coordinator request)

**Finding.** The pilot's `third_person` system prompt makes the model restate the dispute and judge it before writing. In
`transfer_drafts.jsonl`, 43 of 44 drafts contain restatement or outside-observer text (regex on "restat|Person 1|Person 2|outside observer"),
not 12; the pilot judge saw all of it. **Run.** `experiments/E04_mirror_test/v2b.py` extracts the message part (after the last
heading containing "message" or "draft", else after the last horizontal rule): 34 by heading, 8 by rule, 2 unextractable (dropped).
Both judges then rated the message only: `transfer_stripped_v2.jsonl`; baseline drafts (glm, same held-out ambiguous scenarios,
from `drafts.jsonl`) were also rated by judge 2 (`transfer_baseline_gemma_v2.jsonl`; judge 1 baseline is the pilot's rating).
Command: `uv run python experiments/E04_mirror_test/v2b.py` (cached after first run).

| judge | baseline bias | transfer, message only | paired diff (transfer minus baseline) | n pairs | pilot diff, full text |
|---|---|---|---|---|---|
| deepseek-v4-flash | +16.5 [+5.8, +27.5] (22) | -2.5 [-13.1, +7.8] (16) | **-17.6 [-29.5, -6.2]** | 16 | -18.2 [-26.0, -10.6] (22) |
| gemma-4-31b-it | +1.8 [-6.6, +10.7] (22) | -6.2 [-13.5, +0.8] (20) | **-9.5 [-16.5, -2.5]** | 20 | n/a |

The transfer reduction **survives stripping** under both judges (n is smaller: 4 deepseek calls failed with 502, 2 drafts were
unextractable, 6 deepseek ratings missing). Message-only drafts admit fault in 92% [83, 100] (judge 1, n=36 drafts) and 88% [79, 98] (judge 2, n=42).
Caveats: still one drafter, one system prompt chosen from 6 on a small train split, held-out verdicts were null in the pilot,
and the `third_person` prompt asks the model to judge as an outside observer first, which may itself push the message toward fairness
(compare the mediator control, section 4). Not regenerated with a no-restatement instruction (no budget). Source: `tables_v2.md` last section.

## 5. Human-labelling pack (item 5)

- `results/E04/human_labels_template.csv`: 120 drafts ('me' condition, 30 per drafter, 15 per side, from the 43 scenarios
  that both judges rated), shuffled, row ids `Hnnn`, columns `row_id, scenario_id, recipient, draft_text, stance, admits_fault`
  (last two empty). No model, narrator side or judge label. The `recipient` name is given because stance is defined for the sender.
- `results/E04/human_labels_KEY.csv`: row id to model, side, condition, design (keep separate).
- `results/E04/human_scenarios.md`: neutral summary per scenario id. `results/E04/HUMAN_LABELS_README.md`: instructions (~40 min).
- `experiments/E04_mirror_test/score_human_labels.py`: Cohen's kappa between two labellers (admits_fault; stance 3-bin) plus stance
  Pearson r, and the same against both judges (fault threshold 1 or 2), writes `results/E04/human_agreement.md`.
  **Tested on a fake filled file** (labels derived from judge 2 plus noise, two fake labellers, in the scratchpad, not in `results/`):
  it ran and reported sensible kappas. Those numbers are NOT results. **No human labels exist yet**; nothing here is a human-validation result.
- Build command: `uv run python experiments/E04_mirror_test/human_pack.py` (seed 2026).

## 6. Not done, and why

- **Item 7 (escalation simulation) was not run** and **item 8 (symmetry-reward best-of-n) was not run.** The 4,000-call
  budget was spent on items 1 to 5 and the two format controls (about 1,400 calls on fact sheets, tellings, the discarded flawed-checker pass and verification before any drafting,
  896 drafts, 1,431 judge calls). Judge 1 (deepseek) alone is latency-bound at roughly 8 to 12 calls a minute. There is no
  escalation or best-of-n number to cite; paper text must not imply any. The pilot's symmetry-search result is unchanged and still
  as limited as the pilot README says.
- `qwen3.5-397b` registered-checker sample: not run (budget, latency).
- Verdict mirror test on the v2 tellings: not run, so no v2 verdict-to-draft gap.
- Targets missed: 78 ambiguous (target 80), 12 clear drafted (target 20); judge 1 covers 40 of 78 ambiguous 'me' scenarios.
- Judge 2 is itself a drafter; judge 1 and the checker are reasoning models with intermittent 502/504 errors (110 error rows in this task).
- No human validation yet.

## 7. Files added (all under `results/E04/` unless stated)

`scenarios_v2_new.jsonl`, `renderings_v2.jsonl`, `renderings_v2_pass1.jsonl`, `renderings_v2_checker1.jsonl`, `fact_check_v2_before.jsonl` and
`fact_check_v2_after.jsonl` (flawed-checker runs, kept for transparency), `fact_check_v3_before.jsonl`, `fact_check_v3_after.jsonl`,
`balance_v2.jsonl`, `drafts_v2_raw.jsonl`, `judge_deepseek_v2.jsonl`, `judge_gemma_v2.jsonl`, `transfer_stripped_v2.jsonl`,
`transfer_baseline_gemma_v2.jsonl`, `pilot_format_controls.{md,json}`, `tables_v2.md`, `summary_v2.json`, `human_labels_template.csv`,
`human_labels_KEY.csv`, `human_scenarios.md`, `HUMAN_LABELS_README.md`, this file. Code in `experiments/E04_mirror_test/`:
`v2.py`, `v2b.py`, `analyze_v2.py`, `pilot_format_controls.py`, `human_pack.py`, `score_human_labels.py`. Run log: `run.log`.


# Round 2 (post hoc, Sun 15 Nov, after 15:50 EST)

Budget for this round: at most 1,800 calls. Used **1,397 calls, $0.56**, 9 errors (`uv run python -m epi.llm`: E04 tag total
now 6,883 calls, $1.94 of $8). Tables: `results/E04/tables_v3.md`; machine-readable `summary_v3.json`; analysis
`uv run python experiments/E04_mirror_test/analyze_v3.py`; generation `uv run python experiments/E04_mirror_test/v3.py esc|verdict|voice`
(log in `run.log`). Code: `v3.py`, `analyze_v3.py`. CIs are 95% bootstrap over scenarios unless stated.

## R2.1 Escalation simulation (item 7)

**Design (deviations marked).** 30 ambiguous scenarios (`v2.select_scenarios()[0][:30]`, 16 of them also have mediator drafts
from round 1; the other 14 mediator first messages were generated with the identical prompt). Drafters `gemma-4-31b-it` (showed
the gap) and `qwen3.8-27b`. Both parties use the same drafter and prompt. Chain: A's first message is the existing v2 draft of
A's assistant (condition "me" or "mediator"); B's assistant gets B's telling, A's message and "I need to reply ... write the
reply for me" (+ the mediator sentence in that arm); then A's assistant replies, then B's assistant. **4 messages per chain
(A1, B1, A2, B2), not 6**: that is 2 turns per party, a deviation from "3 rounds" made for budget. Later turns see the whole thread.
Judge for every message: `glm-5.3-flash` (not a drafter; same rating prompt as the drafts, so hostility 1-5 and concessions are
comparable to the earlier tables). 120 chains (30 x 2 drafters x 2 prompts), 478 messages judged, 0 unrated. Failure: 2 of 120 chains
(1.7%) did not complete (a drafter returned empty text), both excluded. Files: `escalation_v3.jsonl` (texts), `escalation_judge_v3.jsonl` (ratings).

**Result 1: hostility does not rise across turns.** Mean hostility by turn (t1, t2, t3, t4) and change t4 minus t1 [CI over scenarios]:

| drafter | prompt | t1 | t2 | t3 | t4 | change t4 - t1 | n |
|---|---|---|---|---|---|---|---|
| gemma-4-31b-it | write it for me | 2.57 | 2.57 | 2.20 | 2.50 | -0.07 [-0.43, +0.30] | 30 |
| gemma-4-31b-it | neutral mediator | 1.86 | 1.79 | 1.55 | 1.86 | 0.00 [-0.31, +0.31] | 29 |
| qwen3.8-27b | write it for me | 2.24 | 2.28 | 1.66 | 1.66 | -0.59 [-0.97, -0.17] | 29 |
| qwen3.8-27b | neutral mediator | 1.73 | 1.27 | 1.47 | 1.37 | -0.37 [-0.60, -0.13] | 30 |

No arm escalates: gemma is flat (CI spans 0), qwen de-escalates. Concessions per message fall slightly (gemma "me" 1.20 to 1.03; qwen "me" 1.86 to
1.41; mediator arms 1.59 to 1.00 and 2.50 to 1.53). So **in this simulation, with these two drafters and 4 messages, the
hypothesis that assistant-written exchanges escalate is not supported**; it is a null/negative result for escalation. Caveats: only 2 drafters,
2 turns per party, both parties share one assistant and one prompt, a single LLM judge (glm-5.3-flash), hostility rated per message
from the text, no human check, and scenarios are synthetic (lapses on both sides may make de-escalation easy).

**Result 2: the prompt matters level-wise (paired over scenarios, me minus mediator).**

| drafter | hostility, mean over all 4 turns | hostility at turn 4 | concessions at turn 4 | n |
|---|---|---|---|---|
| gemma-4-31b-it | +0.70 [+0.53, +0.86] | +0.62 [+0.28, +0.97] | +0.03 [-0.34, +0.45] | 29 |
| qwen3.8-27b | +0.49 [+0.33, +0.66] | +0.31 [0.00, +0.62] | -0.14 [-0.55, +0.24] | 29 |

"Write the message for me" chains stay more hostile than mediator chains at every turn, for both drafters; concession counts do not differ
at turn 4. Sensitivity (`tables_v3.md` 1b): 9 of 120 chains contain a refusal message (all qwen "for me"); dropping them leaves qwen "me" at
-0.60 [-1.05, -0.15] (n=20), unchanged conclusion.

## R2.2 Data-quality fixes (item 2; the annotator pass is by Claude Haiku 5.5, not humans)

**(a) Refusals and non-messages.** Hard-refusal regex (first 300 characters; disclaimers such as "Since I am an AI, I cannot provide legal advice, but ..." are not counted)
on all 896 v2 drafts (`analyze_v3.py`, `tables_v3.md` 2a). Rows H162 (gemma-4-31b-it, `family-04`), H315 (qwen3.8, `employer-employee-09`) and H492
(qwen3.8, `ex-partners-06`) are refusals. 'for me' drafts that refuse: gemma-4-31b-it 2 of 180 (1% [0, 3]); glm-5.3-flash 6 of 180 (3% [1, 6]);
gemma-4-26b-a4b-it 6 of 180 (3% [1, 6]); **qwen3.8-27b 38 of 180 (21% [16, 27])** (CIs over drafts). Mediator and single conditions: 0 refusals in 32/32/32/48 drafts.
Regex-based: it can miss refusals phrased differently and cannot judge "non-message" advice-only drafts beyond refusals (H019, glm, is advice plus a message, not counted).

**Headline mirror bias, 'for me', ambiguous, excluding refusals** (scenario dropped if either side's draft is a refusal; n = scenarios):

| drafter | judge deepseek, all | deepseek, excl. refusals | judge gemma, all | gemma, excl. refusals |
|---|---|---|---|---|
| gemma-4-31b-it | +54.8 [+47.0, +62.4] (40) | +54.8 [+47.0, +62.4] (40) | +35.7 [+29.6, +41.6] (73) | +35.7 [+29.6, +41.6] (73) |
| glm-5.3-flash | +22.5 [+13.6, +31.2] (40) | +22.5 [+13.6, +31.2] (40) | +6.9 [+1.2, +12.9] (78) | +7.7 [+1.9, +13.7] (75) |
| gemma-4-26b-a4b-it | +54.1 [+46.0, +61.9] (40) | +55.3 [+47.3, +62.9] (39) | +36.9 [+31.2, +42.4] (76) | +38.4 [+32.9, +43.8] (73) |
| qwen3.8-27b | +6.5 [-5.2, +18.1] (40) | **+19.2 [+4.8, +33.0] (25)** | -7.6 [-14.4, -0.8] (78) | **+6.6 [-0.9, +14.2] (46)** |

**This changes the round-1 reading for qwen3.8-27b.** Its "no gap" (and negative bias under judge 2) came partly from refusals that lecture the user (the judge scores
them as messages). Without them its bias is positive (+19.2 under judge 1, CI above 0; +6.6 under judge 2, CI includes 0), though n drops to 25 and 46 scenarios and the
surviving scenarios are the ones where qwen did not refuse, a selected set. The heterogeneity warning in round 1 should read: gemma family strongly partisan, glm modest, qwen3.8 refuses
about a fifth of the time and is modest when it complies. The other three drafters' numbers are essentially unchanged by the exclusion.

**(b) Voice/recipient mismatch.** H756 (qwen3.8, `roommates-00`, B = Jordan) says "I threw away your mug". The fact sheet and the B telling (`renderings_v2.jsonl`)
say Maya threw away Jordan's mug, so the telling is right and **the drafter misattributed the act**: a generation error by qwen3.8, not a role-swap or pipeline bug (the same scenario's other
draft, H644, is correct). H019 (glm, `family-11`, B) is advice addressed to the user ("Before you send anything ...") followed by a message, not a voice swap. Prevalence: a cheap name heuristic
(greeting addresses the sender, or sign-off names the recipient) flags 0 of 896 drafts. An LLM check (`v3.py voice`, `voice_check_v3.jsonl`, glm-5.3-flash answers "who wrote this, A or B?" from the text only) on a
random sample of 200 'for me' drafts judged the writer to be the recipient in 4 (2% [0, 4]; gemma-4-31b 2 of 51, qwen3.8 2 of 56, glm 0 of 50, gemma-26b 0 of 43), unclear or failed in 13. The 4 are not
checked by hand, so some may be judge errors; fact-level misattributions like H756 are not detectable this way. With refusals, truncated and name-flagged drafts all excluded the headline is unchanged
for gemma-31b, glm and gemma-26b (`tables_v3.md`; e.g. judge 1: +54.8, +23.8 [+15.3, +32.4], +54.3 [+46.3, +62.1]) and qwen3.8 is +18.9 [+2.6, +33.7] (n=23). No full-set exclusion for the 4 sampled mismatches was made.

**(c) Truncated drafts.** Heuristic (final character not sentence-ending punctuation or markup): 11 of 896 drafts (1.2%): glm-5.3-flash 6 (4 'for me', 2 mediator), qwen3.8-27b 4 (3 + 1),
gemma-4-26b 1, gemma-4-31b 0. H177 and H138 are qwen3.8 (one hit a long numbered-list reply). Counts are too small to say truncation depends on the drafter beyond "non-reasoning gemma-31b: none"; excluding them
changes no headline (`tables_v3.md`, column "excluding refusals + truncated"). The heuristic is approximate; I did not store the API's truncation flag for drafts.

## R2.3 Judge level calibration (item 3; annotators are LLMs, not humans)

On the 120 blinded rows, mean of the two Haiku-5.5 annotator runs = 65.5 (`llm_labels_haiku_1.csv`, `_2.csv`; the two runs are one model, so not independent):

| judge | mean stance | mean difference vs annotator mean [CI over rows] | mean abs diff | Pearson r with annotator mean [CI] |
|---|---|---|---|---|
| deepseek-v4-flash | 67.4 | +2.0 [0.0, +3.9] | 9.0 | 0.93 [0.90, 0.95] |
| gemma-4-31b-it | 61.8 | -3.7 [-5.8, -1.7] | 9.2 | 0.90 [0.86, 0.94] |

Both judges track the annotators closely; deepseek's level is closer (+2.0 versus -3.7), gemma reads lower. Mean absolute difference is the same (9.0 vs 9.2).
The earlier 11 to 15 point mirror-bias gap between judges is a sum over two drafts per scenario, so a per-draft level gap of about 6 points is consistent with it. Source: `tables_v3.md` section 3.
This is agreement with another LLM, not ground truth.

## R2.4 Verdict mirror bias on the strict tellings (item 4)

Verdict test (same first-person prompt as the pilot) on the strict tellings, ambiguous scenarios of the judge-1 subset (n=40; A and B tellings only, no neutral telling), four drafters
(`mirror_v3.jsonl`, 320 calls, 1 unparsed). Paired with the judge-1 draft bias on the same scenarios:

| model | verdict bias | draft bias (deepseek judge) | paired draft minus verdict | n |
|---|---|---|---|---|
| gemma-4-31b-it | -23.5 [-29.6, -16.9] | +54.4 [+46.5, +62.2] | +77.8 [+66.0, +89.1] | 39 |
| glm-5.3-flash | -19.8 [-25.2, -14.2] | +22.5 [+13.9, +31.2] | +42.2 [+32.5, +52.1] | 40 |
| gemma-4-26b-a4b-it | -0.5 [-6.5, +5.6] | +54.1 [+46.1, +61.9] | +54.6 [+43.6, +65.2] | 40 |
| qwen3.8-27b | -19.5 [-24.8, -14.4] | +6.5 [-5.4, +18.1] | +26.0 [+13.4, +38.9] | 40 |

Verdict bias is zero or negative for all four (models are harder on the narrator than on the same person in the neutral telling), and the draft-minus-verdict gap is positive with CI above 0 for all
four on identical scenarios. For qwen3.8 the draft figure still includes refusals (R2.2); its gap excluding refusals was not recomputed (verdict n would also change). Not rerun on clear controls or all 78 ambiguous scenarios.

## R2.5 Not done in round 2
Item 8 (symmetry best-of-n): not run. 3-round chains: 2 turns per party only. Human labels still absent (the Haiku annotator pass is an LLM check). The 4 sampled mismatches were not inspected.
