# Figures

No figure files exist in `results/E04/` yet. Needed (plot from the rerun, after `analyze.py`):

**Figure 1 (main, Section 5): mirror bias by model, verdict against draft.**
- Question answered: does the model's draft take the narrator's side more than its verdict does?
- Type: dot plot with 95% CI bars, one row per model (two drafters in the pilot; four if scale-up lands), two markers per row (verdict, draft), zero line, x axis "mirror bias (points)". Positive means sides with narrator.
- Data: `results/E04/summary.json` keys `mirror.<model>.ambiguous.bias` (est, lo, hi, n) and `drafts.<model>` ambiguous draft bias (check the key; values are in `tables.md` "Mirrored ghostwriting"). For paired same-scenario values use `verdict_vs_draft`.
- Pilot values: gemma-4-31b-it verdict -12.2 [-19.4, -4.7], draft +50.3 [+41.2, +59.2]; glm-5.3-flash verdict -9.2 [-13.9, -4.6], draft +16.8 [+9.0, +24.5]. Add the four verdict-only models as verdict markers.
- Add advocacy-control draft markers when available.

**Figure 2: fault admission.**
- Question: do drafts follow the model's own verdict?
- Type: grouped bars, x = drafter, groups = own verdict (YTA or ESH, NTA or NAH), y = share of drafts admitting any fault, with CI.
- Data: `drafts.jsonl` joined to `mirror.jsonl` on id, model, telling; or the pre-computed values in `tables.md` columns "P(admit fault given own YTA/ESH)" and "P(admit given own NTA/NAH)".
- Pilot values: gemma 49% [37, 60] and 10% [0, 24]; glm 91% [83, 97] and 39% [21, 57].

**Figure 3: escalation (Section 7).** Needs the multi-turn simulation.
- Type: line plot, x = turn, y = mean judged hostility (and a second panel for concessions), one line per condition (baseline, advocacy control, guarded prompt), CI bands.
- Data: [[PENDING: simulation output file, from E04 experiments]]; columns expected: dispute id, turn, side, condition, hostility, concessions, threat.
