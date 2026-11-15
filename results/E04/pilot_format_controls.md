# Pilot format controls (no API calls)

Source: drafts.jsonl (pilot, deepseek-v4-flash judge). Multi-option = regex `MULTI` in pilot_format_controls.py.

## 1. Multi-option drafts

| drafter | multi-option drafts | mirror bias ambiguous, all (n) | excluding scenarios with a multi-option draft (n) | paired: mean stance of multi vs single drafts |
|---|---|---|---|---|
| gemma-4-31b-it | 29 of 92 | 50.3 [41.2, 59.2] (33) | 51.2 [38.8, 63.2] (17) | multi 77.5 (n=28) vs single 74.3 (n=63) |
| glm-5.3-flash | 1 of 94 | 16.8 [9.0, 24.5] (36) | 16.8 [8.8, 24.9] (35) | multi 50.0 (n=1) vs single 58.4 (n=93) |
