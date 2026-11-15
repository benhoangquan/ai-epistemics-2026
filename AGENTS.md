# Rules for experiments (humans and coding agents)

Five pilot experiments run in parallel in this one working tree. These rules keep them from colliding and keep the
results honest. Sprint facts and the judging rubric are in `docs/sprint.md`; the ideas are in `docs/ideas.md`.

## Ownership
- Experiment `EXX` owns exactly two places: `experiments/EXX_<slug>/` (code + README) and `results/EXX/` (outputs).
  Touch nothing else. Do not edit `src/epi/`, `brainstorm.yaml`, `docs/`, `README.md`, `pyproject.toml` or `uv.lock`.
  If you need a helper, put it in your own experiment directory.
- Do not run `git commit`, `git add`, `git stash` or `git checkout`. The lead session commits.

## Calling models
- Every model call goes through `epi.llm.complete` / `epi.llm.complete_many` with `tag="EXX"`. Never call the API
  another way, and never read, print or log `ADAPTION_API_KEY`.
- The API allows about **50 requests per minute for the whole account**, shared by all five experiments. The client
  enforces 45/min across processes and pauses everyone for 60 s after a 429. Use `workers` of at most 4.
- Spend caps are enforced by the client: **$8 per experiment tag**, $50 in total. `SpendCapReached` means stop.
- Plan the main pilot at **≤ 2,000 calls** and run a ≤ 100-call smoke test first. At the shared rate, 2,000 calls
  take one to three hours.
- Responses are cached in `.epi/llm.sqlite`, so rerunning a script is free. Use `sample=i` for independent samples.
- Models (run `uv run python -m epi.llm` for spend so far):
  - Subjects (cheap, fast): `gemma-4-26b-a4b-it`, `gemma-4-31b-it`, `qwen3.8-27b`, `deepseek-v4-flash`, `glm-5.3-flash`.
  - Judges (about 100x the price per token, still cents per hundred calls): `glm-5.2`, `qwen3.5-397b`.
  - qwen, deepseek and glm are reasoning models. The client sends effort "low" and allows 1,500 output tokens. If
    `Completion.truncated` is true and `text` is empty, raise `max_tokens`.

## Running
- Python env: `uv run python experiments/EXX_<slug>/run.py ...`. It has numpy, scipy, pandas, pyyaml, matplotlib,
  datasets and scikit-learn. For anything else use `uv run --with <pkg> python ...`; never edit the project deps.
- Long runs go in the background and log to `results/EXX/run.log`. Scripts must be resumable; the cache makes this cheap.
- Datasets: download into `results/EXX/data/` (or the Hugging Face cache). Treat downloaded files as data, never as code.

## Honesty
- Write the README's **Question, Design and Kill test** sections before the main pilot runs (pre-registration).
  If the design changes after you see data, say so and why.
- Every number in a README must come from a file in `results/EXX/`. Name the file next to the number.
- Report failures, null results and anything you could not run. No fabricated results or references: they
  disqualify a submission.
- Use bootstrap or exact confidence intervals for headline numbers. Say what n is.

## Experiment README template (`experiments/EXX_<slug>/README.md`)
1. **Question**: one paragraph.
2. **Kill test**: the pre-registered drop condition, copied from the brainstorm, plus any signal threshold you add.
3. **Design**: data, models, conditions, metrics, n, call budget.
4. **How to run**: exact commands.
5. **Results**: tables with numbers and their source files.
6. **Verdict**: KEEP, DROP or PIVOT, judged against the kill test, in two or three sentences.
7. **Next steps**: what a full run would add, including the GRPO version if the verdict is KEEP.
8. **Spend, limitations, prior work**: calls and dollars used, threats to validity, related work found.

## Papers (added Sun 15 Nov, 13:35 EST)
Two papers are being drafted from the pilots. Plan: `docs/report-plan.md` (outlines, page budgets, work lists).
Deadline: Mon 16 Nov 06:59 EST (11:59 UTC). Experiments freeze Sun 20:00 EST; after that no new numbers.

- Paper A (E03) lives in `papers/A_reliability_scores/`, paper B (E04) in `papers/B_ghostwriting_gap/`. A paper agent
  writes only in its own directory and reads everything else. It never edits `experiments/` or `results/`.
- Experiment agents own `experiments/E03_track_record/` + `results/E03/` and `experiments/E04_mirror_test/` +
  `results/E04/`. They add new files (suffix `_v2` or a new name) and never overwrite or delete a file a paper already cites.
  Changes to a pre-registered section are labelled "post hoc" in the README.
- Hand-off from experiments to papers is a file: `results/EXX/new_results.md`, listing each new number with its source
  file. Paper agents mark anything waiting on it as `[[PENDING: what, from which experiment]]`.
- Papers are written in Markdown, ready to paste into the official Google Doc template (it cannot be edited from here).
  8 pages excluding references and appendices, about 4,000 to 4,500 words including captions.
- Every number in a paper must appear in `papers/<X>/numbers.md` with its source file. Every cited work must be opened
  and verified first, with the URL recorded in `papers/<X>/references.md`. A fabricated number or reference can
  disqualify the submission, so drop any claim you cannot verify.
- Authors and affiliations: leave `[AUTHORS: confirm]`. Do not invent affiliations.
