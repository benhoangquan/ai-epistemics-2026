# TODO: what waits on other work

Owner for all items: E04 experiments agent. Hand-off file: `results/E04/new_results.md` (and any `_v2` files it names). Then rerun the second pass on `paper.md`.

| Item | Where it lands in the paper | File to appear in |
|---|---|---|
| Fixed fact sheets, rerun fact check (registered judge) | Section 3 validation, abstract threat sentence, Table 1 | results/E04/new_results.md |
| Second drafting judge from a different family, agreement | Section 3, Section 5, Discussion (c) and (e) | same |
| Human-labelled pack (100+ drafts), Cohen's kappa. Labels come from the team | Section 3, Section 5, abstract | same, plus labels file |
| Advocacy control ("message a neutral mediator would endorse") | Abstract, Section 1, 5, 6, 8. Do not claim the gap exceeds the instruction until it lands | same |
| Scale to ~120 scenarios and four drafters | Re-derive every number, Figure 1, abstract | same, plus new tables (`_v2`) |
| Multi-turn escalation simulation | Section 7 and Figure 3. If not done, shorten Section 7 and move its page to Section 5 or 8 | same |
| Symmetry-reward best-of-n | Section 6 | same |
| Single-message drafts / message-only extraction (multi-option drafts, restatement text) | Section 5 format note, Section 6 | same |

Paper-side tasks for pass two:
- Replace every `[[PENDING ...]]` and re-derive `numbers.md`.
- Re-check the abstract word count (150 to 250) and the 8-page limit after export to the Google Doc template.
- Paste verbatim prompts into appendix D from `experiments/E04_mirror_test/common.py` (the appendix currently paraphrases the README).
- Make figures from the final data (see `figures/FIGURES_TODO.md`).
- Re-verify references on the day of submission. Resolve the unverified items in `references.md` or leave them out.
- Confirm authors and affiliations.
