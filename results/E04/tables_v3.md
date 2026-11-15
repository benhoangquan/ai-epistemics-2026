# E04 round 2 tables (post hoc, 15 Nov)

## 2a. Refusals and non-messages, all v2 drafts

Refusal = hard refusal in the first 300 characters (regex `REF` in analyze_v3.py; polite disclaimers like "Since I am an AI, I cannot provide legal advice, but ..." are NOT counted). Truncated = final character is not sentence-ending punctuation or markup (heuristic; approximate).

| drafter | condition | drafts | refusals | refusal rate [CI over drafts] | truncated (heuristic) | role mismatch (name heuristic) |
|---|---|---|---|---|---|---|
| gemma-4-31b-it | me | 180 | 2 | 1% [0, 3] | 0 | 0 |
| gemma-4-31b-it | mediator | 32 | 0 | 0% [0, 0] | 0 | 0 |
| gemma-4-31b-it | single | 48 | 0 | 0% [0, 0] | 0 | 0 |
| glm-5.3-flash | me | 180 | 6 | 3% [1, 6] | 4 | 0 |
| glm-5.3-flash | mediator | 32 | 0 | 0% [0, 0] | 2 | 0 |
| gemma-4-26b-a4b-it | me | 180 | 6 | 3% [1, 6] | 1 | 0 |
| gemma-4-26b-a4b-it | mediator | 32 | 0 | 0% [0, 0] | 0 | 0 |
| qwen3.8-27b | me | 180 | 38 | 21% [16, 27] | 3 | 0 |
| qwen3.8-27b | mediator | 32 | 0 | 0% [0, 0] | 1 | 0 |

## 2a/2b/2c. Headline draft mirror bias ('for me', ambiguous) after exclusions (scenario dropped if either side's draft is excluded)

### judge = deepseek

| drafter | all drafts | excluding refusals | excluding refusals + truncated | excluding refusals + truncated + name-role mismatch |
|---|---|---|---|---|
| gemma-4-31b-it | 54.8 [47.0, 62.4] (40) | 54.8 [47.0, 62.4] (40) | 54.8 [47.0, 62.4] (40) | 54.8 [47.0, 62.4] (40) |
| glm-5.3-flash | 22.5 [13.6, 31.2] (40) | 22.5 [13.6, 31.2] (40) | 23.8 [15.3, 32.4] (39) | 23.8 [15.3, 32.4] (39) |
| gemma-4-26b-a4b-it | 54.1 [46.0, 61.9] (40) | 55.3 [47.3, 62.9] (39) | 54.3 [46.3, 62.1] (38) | 54.3 [46.3, 62.1] (38) |
| qwen3.8-27b | 6.5 [-5.2, 18.1] (40) | 19.2 [4.8, 33.0] (25) | 18.9 [2.6, 33.7] (23) | 18.9 [2.6, 33.7] (23) |

### judge = gemma

| drafter | all drafts | excluding refusals | excluding refusals + truncated | excluding refusals + truncated + name-role mismatch |
|---|---|---|---|---|
| gemma-4-31b-it | 35.7 [29.6, 41.6] (73) | 35.7 [29.6, 41.6] (73) | 35.7 [29.6, 41.6] (73) | 35.7 [29.6, 41.6] (73) |
| glm-5.3-flash | 6.9 [1.2, 12.9] (78) | 7.7 [1.9, 13.7] (75) | 8.2 [2.2, 14.3] (72) | 8.2 [2.2, 14.3] (72) |
| gemma-4-26b-a4b-it | 36.9 [31.2, 42.4] (76) | 38.4 [32.9, 43.8] (73) | 37.8 [32.4, 43.3] (72) | 37.8 [32.4, 43.3] (72) |
| qwen3.8-27b | -7.6 [-14.4, -0.8] (78) | 6.6 [-0.9, 14.2] (46) | 6.7 [-0.9, 14.5] (44) | 6.7 [-0.9, 14.5] (44) |

## 3. Judge level calibration on the 120 blinded rows (annotators are Claude Haiku 5.5 runs, NOT humans)

| source | n rows | mean stance | mean diff vs annotator mean [CI] | mean abs diff | Pearson r with annotator mean [CI] |
|---|---|---|---|---|---|
| Haiku annotator mean (reference) | 120 | 65.5 | | | |
| judge deepseek | 120 | 67.4 | +2.0 [+0.0, +3.9] | 9.0 | 0.93 [0.90, 0.95] |
| judge gemma | 120 | 61.8 | -3.7 [-5.8, -1.7] | 9.2 | 0.90 [0.86, 0.94] |

## 1. Escalation simulation (both parties use an assistant; judge glm-5.3-flash)

Chains started 120; complete with all 4 messages judged: 118; failure rate 1.7%. 4 messages per chain: A1 (A's draft), B1 (B's assistant replies), A2, B2. Rounds = 2 per party, a deviation from the requested 3.

Mean hostility (1-5) and concessions per message, by turn; per-scenario means over the two sides' chains, CI over scenarios.

| drafter | prompt | turn 1 hostility | turn 2 | turn 3 | turn 4 | change turn 4 minus turn 1 [CI] | concessions turn 1 -> turn 4 | n scenarios |
|---|---|---|---|---|---|---|---|---|
| gemma-4-31b-it | me | 2.57 | 2.57 | 2.20 | 2.50 | -0.07 [-0.43, 0.30] | 1.20 -> 1.03 | 30 |
| gemma-4-31b-it | mediator | 1.86 | 1.79 | 1.55 | 1.86 | 0.00 [-0.31, 0.31] | 1.59 -> 1.00 | 29 |
| qwen3.8-27b | me | 2.24 | 2.28 | 1.66 | 1.66 | -0.59 [-0.97, -0.17] | 1.86 -> 1.41 | 29 |
| qwen3.8-27b | mediator | 1.73 | 1.27 | 1.47 | 1.37 | -0.37 [-0.60, -0.13] | 2.50 -> 1.53 | 30 |

Prompt contrast (paired over scenarios, 'me' minus 'mediator'), mean hostility averaged over all turns and at turn 4:

| drafter | all-turn mean hostility diff [CI] | turn-4 hostility diff [CI] | turn-4 concessions diff [CI] | n scenarios |
|---|---|---|---|---|
| gemma-4-31b-it | 0.70 [0.53, 0.86] | 0.62 [0.28, 0.97] | 0.03 [-0.34, 0.45] | 29 |
| qwen3.8-27b | 0.49 [0.33, 0.66] | 0.31 [0.00, 0.62] | -0.14 [-0.55, 0.24] | 29 |

## 4. Verdict mirror bias on the strict tellings (same 40 ambiguous scenarios as the judge-1 headline)

| model | verdict bias [CI] | n | draft bias, deepseek judge, same scenarios [CI] | paired draft minus verdict [CI] | n |
|---|---|---|---|---|---|
| gemma-4-31b-it | -23.5 [-29.6, -16.9] | 39 | 54.4 [46.5, 62.2] | 77.8 [66.0, 89.1] | 39 |
| glm-5.3-flash | -19.8 [-25.2, -14.2] | 40 | 22.5 [13.9, 31.2] | 42.2 [32.5, 52.1] | 40 |
| gemma-4-26b-a4b-it | -0.5 [-6.5, 5.6] | 40 | 54.1 [46.1, 61.9] | 54.6 [43.6, 65.2] | 40 |
| qwen3.8-27b | -19.5 [-24.8, -14.4] | 40 | 6.5 [-5.4, 18.1] | 26.0 [13.4, 38.9] | 40 |

## 2b. Voice check on a random sample of 200 'for me' drafts (judge glm-5.3-flash: who wrote it?)

| drafter | sampled | judged writer = true sender | judged writer = recipient | unclear / failed |
|---|---|---|---|---|
| gemma-4-31b-it | 51 | 45 | 2 | 4 |
| glm-5.3-flash | 50 | 49 | 0 | 1 |
| gemma-4-26b-a4b-it | 43 | 40 | 0 | 3 |
| qwen3.8-27b | 56 | 49 | 2 | 5 |

Total sampled 200; writer judged to be the recipient in 4 (2% [0, 4]).

## 1b. Escalation sensitivity: chains with any refusal message dropped

Chains containing at least one refusal message: 9 of 120 (Counter({('qwen3.8-27b', 'me'): 9})).

| drafter | prompt | hostility t1 | t2 | t3 | t4 | change t4 - t1 [CI] | n scenarios |
|---|---|---|---|---|---|---|---|
| gemma-4-31b-it | me | 2.57 | 2.57 | 2.20 | 2.50 | -0.07 [-0.43, 0.30] | 30 |
| gemma-4-31b-it | mediator | 1.86 | 1.79 | 1.55 | 1.86 | 0.00 [-0.31, 0.31] | 29 |
| qwen3.8-27b | me | 2.20 | 2.20 | 1.70 | 1.60 | -0.60 [-1.05, -0.15] | 20 |
| qwen3.8-27b | mediator | 1.73 | 1.27 | 1.47 | 1.37 | -0.37 [-0.60, -0.13] | 30 |
