# Numbers in paper.tex (pass 2), with sources
Files are in `results/E04/`. `new_results.md` = N, `tables_v2.md` = T2, `summary_v2.json` = S2, pilot `tables.md` = T1, `summary.json` = S1. "Derived" = computed from cited rows. Intervals are 95% bootstrap CIs. The pass-1 number table is superseded; the 83% added-fact figure is retired (checker bug, N section 1).

| Number | Where | Source |
|---|---|---|
| 47 pilot scenarios, 36 ambiguous, 11 clear | abstract, 3 | S1 `n_rendered`, `design_counts`; T1 Validation |
| 48 pilot sheets; 97 rendered scaled scenarios; 54 new sheets; 78 ambiguous + 12 clear drafted | 3, App A | N section 1 and 2 |
| 896 drafts (1 empty); 13 of 895 unrated | 3, App A | N section 2 |
| Judge 1 rated 40 of 78 ambiguous scenarios | 3 | N section 2 |
| Fact check pilot 50% [39, 61] n=92; strict first pass 20% [14, 25] n=194; final 3% [1, 5] n=194; 5 not improved | Table 1, 3, App A | N section 1 (`fact_check_v3_before.jsonl`, `fact_check_v3_after.jsonl`: `n_added_pass1`, `n_added_final`, state `regen_not_better`) |
| Checker glm-5.3-flash, qwen3.5-397b too slow, checker bug (never saw background/dispute) | 3, App A | N section 1 |
| Neutral balance, ambiguous 46.9 [42.9, 50.8] n=78; 40% in 40-60; pilot 32-34% | 3, App A | N section 1 (`balance_v2.jsonl`); S1/T1 |
| Pilot verdict mirror bias +6.7, -12.2, -5.6, -9.2 with CIs and n; "-12 to +7" | abstract, Table 2 | T1 Verdict mirror test; S1 `mirror.<model>.ambiguous.bias` |
| NTA-both 3%, 0%, 3%, 0%; clear accuracy 82-100% (n=11); mean abs bias 19.2 (gemma-26b) | 4.1 | T1; S1 `mirror.gemma-4-26b-a4b-it.ambiguous.mean_abs_bias` = 19.17 |
| Draft bias, judge 1 (n=40): +54.8 [47.0, 62.4], +54.1 [46.0, 61.9], +22.5 [13.6, 31.2], +6.5 [-5.2, 18.1] | abstract, Table 3, Fig 1 | N section 2; T2; S2 `bias_me.deepseek` |
| Draft bias, judge 2: +35.7 [29.6, 41.6] (73), +36.9 [31.2, 42.4] (76), +6.9 [1.2, 12.9] (78), -7.6 [-14.4, -0.8] (78) | abstract, Table 3, Fig 1 | N section 2; T2; S2 `bias_me.gemma` |
| Pooled bias +34.5 [27.4, 41.4] (40) and +17.2 [12.7, 21.9] (78) | 4.2 | N section 2; T2 |
| Any fault admitted (draft level), judge 1 / judge 2: 38/43, 40/48, 79/78, 76/78 with CIs | Table 3 | T2 |
| Stance r 0.93 [0.92, 0.94], admits-fault kappa 0.84, 3-bin kappa 0.73, n=525; mean stance 63.4 vs 58.1 | abstract, 4.2, Table A1 | N section 3; T2 Agreement; S2 `agreement` |
| "11 to 15 points" lower under judge 2; pooled diff -13.3 [-15.6, -11.0]; per-drafter -14.9, -12.1, -11.9, -10.9; same-40 biases +55.0/+40.1, +22.5/+10.4, +54.9/+42.9, +6.5/-4.4 | abstract, 4.2, Table A2 | N section 3; T2 "Headline contrast" |
| Haiku annotators: 120 drafts; r 0.89; 3-bin kappa 0.62-0.66; fault kappa 0.88-0.90; run-vs-run kappa 0.92 (fault), r 0.95, 3-bin 0.80; consensus rows | 3, 4.2, Table A3 | `llm_annotator_agreement_haiku.md` |
| 120 drafts = 30 per drafter, 'me' condition, 43 scenarios rated by both judges | 3 | N section 5 |
| Pilot paired draft-minus-verdict +58.9 [47.5, 70.2] (42), +22.7 [15.3, 30.4] (47); P(admit given own YTA/ESH) 49% [37, 60] (68), 91% | 4.2 | T1 Mirrored ghostwriting; S1 |
| Worked example: 40 ESH, 20 YTA, bias -40; draft stances 100, 65; bias +65; hostility 4, 2; neutral 80; glm 90/45, +35 | 4.2, App C | `mirror.jsonl`, `drafts.jsonl`, id `landlord-tenant-00`; biases derived |
| Clear controls scaled, judge 2: 58% [33, 83], 100%, 67% [42, 92], 100%; innocent 0%; judge 1 n=5 | 4.2, Table A7 | N section 2; T2 |
| Hostility means 2.62, 2.63, 1.97, 2.35 (judge 2); "2.0 to 2.7" also uses judge 1: 2.71, 2.71, 2.00, 2.26 | 4.2, Table A1 | T2 |
| Advocacy control: bias me -> mediator and diffs, both judges (Table 4); "20 to 44 points"; fault admission 44% -> 78% (gemma-31b, judge 1) | abstract, 4.3 | N section 4; T2 Advocacy control |
| Multi-option counts: 79/179, 29/180, 4/180, 2/180; no-multi bias +50.6 [39.7, 61.2] (17) vs +54.8 | 4.3, Table A5 | T2 Multi-option; N section 4b |
| Single message: +56.5 -> +59.6, diff -3.1 [-8.8, 2.3] (24); judge 2 +44.0 -> +50.7, -6.7 [-12.9, -0.2] (21) | 4.3, Table A5 | T2; N section 4b |
| Pilot search: held-out verdict 13.0 -> 12.7, diff -0.2 [-3.6, 3.2] (22); transfer -18.2 [-26.0, -10.7] | 4.3 | T1 Guarded symmetry search; N section 4c |
| 43 of 44 transfer drafts with restatement (supersedes 12 of 44); extraction 34 header, 8 hr, 2 dropped | 4.3, Table A6 | N section 4c; T2 |
| Stripped transfer: -17.6 [-29.5, -6.2] (16) judge 1; -9.5 [-16.5, -2.5] (20) judge 2; baseline +16.5 / +1.8; message-only -2.5, -6.2; fault 92% (36), 88% (42) | 4.3, Table A6 | N section 4c; T2 last section |
| Data-quality rows H162, H315, H492 / H019, H756 / H177, H138 | 4.5, App A | named by the lead; row text checked in `human_labels_template.csv` (H162, H315, H492 are refusals; H019 pushback with advice; H756 and H177 not fully checked; H138 not opened). Categories follow the lead's message. |
| Appendix tables A8 to A12 | App E | pilot `tables.md` (Verdict mirror, Clear-fault, Mirrored ghostwriting, Guarded symmetry search) |
| 48%, 24.3%/7.5%, 787, ~50%, 2,939, "complete scripting..." | 1, 2 | cited abstracts; see references.md |

## Pass 3 additions (round 2). Sources: `new_results.md` "Round 2" (R2.x), `tables_v3.md` (T3), `summary_v3.json`
Superseded by pass 3: the pass-2 statements that "qwen shows no gap" and "H019 and H756 are voice mismatches"; the title "Fair in Verdict, Partisan in Draft". The paper now retitles to "Verdict Tests Miss It: LLM Ghostwriting Takes the Narrator's Side".

| Number | Where | Source |
|---|---|---|
| Verdict bias on strict tellings, 40 ambiguous: -23.5 [-29.6, -16.9] (39), -19.8 [-25.2, -14.2] (40), -0.5 [-6.5, +5.6] (40), -19.5 [-24.8, -14.4] (40) | abstract, 4.1, Table 4 | R2.4; T3 section 4; `mirror_v3.jsonl` |
| Draft bias same scenarios (judge 1): +54.4 [46.5, 62.2] (39), +22.5 [13.9, 31.2], +54.1 [46.1, 61.9], +6.5 [-5.4, 18.1]; paired draft minus verdict +77.8 [66.0, 89.1], +42.2 [32.5, 52.1], +54.6 [43.6, 65.2], +26.0 [13.4, 38.9] | 4.2, Table 4 | R2.4; T3 section 4 |
| Refusals 'for me': qwen 38/180 = 21% [16, 27]; glm 6 (3% [1, 6]); gemma-26b 6 (3% [1, 6]); gemma-31b 2 (1% [0, 3]); mediator/single 0 | abstract, 4.2, 4.5, App A | R2.2a; T3 section 2a |
| Refusal regex: first 300 characters, polite disclaimers not counted | 3, App A | R2.2a |
| Bias excluding refusals: qwen +19.2 [4.8, 33.0] (25) judge 1; +6.6 [-0.9, 14.2] (46) judge 2; glm +22.5 / +7.7 [1.9, 13.7] (75); gemma-26b +55.3 (39) / +38.4 (73); gemma-31b unchanged | abstract, 4.2, Table A7 | R2.2a; T3 "Headline draft mirror bias after exclusions" |
| After refusals, truncated, name-flagged excluded (judge 1): gemma-31b +54.8, glm +23.8 [15.3, 32.4] (39), gemma-26b +54.3 [46.3, 62.1] (38), qwen +18.9 [2.6, 33.7] (23); judge 2 values in Table A7 | 4.5, Table A7 | R2.2b; T3 |
| Voice check: 200 sampled; writer = recipient in 4 (2% [0, 4]); per drafter 2/51, 0/50, 0/43, 2/56; unclear or failed 13; name heuristic flags 0 of 896; the 4 not inspected | 4.5, Table A9 | R2.2b; T3 section 2b; `voice_check_v3.jsonl` |
| H756 = qwen misattribution (mug), H019 = glm advice before a message, H162 gemma-31b refusal, H315 and H492 qwen refusals | 4.5 | R2.2 |
| Truncated 11 of 896 (glm 6, qwen 4, gemma-26b 1, gemma-31b 0); H177, H138 qwen | 4.5, App A | R2.2c; T3 section 2a |
| Judge calibration vs Haiku annotator mean 65.5: deepseek 67.4, +2.0 [0.0, 3.9], MAD 9.0, r 0.93 [0.90, 0.95]; gemma 61.8, -3.7 [-5.8, -1.7], MAD 9.2, r 0.90 [0.86, 0.94]; "per-draft gap about 6" | 4.2, Table A8 | R2.3; T3 section 3. The "about 6" is from R2.3's own text. |
| Escalation: 30 scenarios, 2 drafters, 4 messages/chain, 120 chains started, 118 complete (2 excluded), judge glm-5.3-flash | abstract, 3, 4.4 | R2.1; T3 section 1 |
| Hostility by turn and change t4-t1: gemma me 2.57/2.57/2.20/2.50, -0.07 [-0.43, 0.30] (30); gemma mediator 1.86/1.79/1.55/1.86, 0.00 [-0.31, 0.31] (29); qwen me 2.24/2.28/1.66/1.66, -0.59 [-0.97, -0.17] (29); qwen mediator 1.73/1.27/1.47/1.37, -0.37 [-0.60, -0.13] (30) | 4.4, Table 6 | T3 section 1 |
| Prompt contrast, all-turn hostility: gemma +0.70 [0.53, 0.86], qwen +0.49 [0.33, 0.66]; turn 4: +0.62 [0.28, 0.97], +0.31 [0.00, 0.62]; turn-4 concessions +0.03 [-0.34, 0.45], -0.14 [-0.55, 0.24]; n=29 | abstract, 4.4, Table A9 | T3 section 1 |
| Sensitivity: 9 of 120 chains with a refusal (all qwen 'me'); qwen change -0.60 [-1.05, -0.15] (20) | 4.4, Table A9 | T3 section 1b |
| Concessions fall slightly (gemma me 1.20 to 1.03; qwen me 1.86 to 1.41) | 4.4 (stated as "fall slightly") | T3 section 1 |
| Prompts verbatim | App D | `experiments/E04_mirror_test/common.py`, `run.py` (draft judge), `v2.py` (STRICT, TASKS, MEDIATOR, SINGLE), `v3.py` (reply prompt, voice check) |
