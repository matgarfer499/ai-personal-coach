# Review guide

What matters when reviewing this repo. Reviewers read this before reporting.

## What counts as a failure here

- A number the client sees that the model computed itself instead of taking it from
  `uv run python -m coach ... --json`.
- A constant in `coach/` with no knowledge-rule comment (or `# convention:` listed in
  `docs/conventions.md`), or one that no longer matches the rule it cites.
- Advice below the calorie floors, a deficit after a positive screen, or a red flag that fires
  without the deferral line from `docs/safety.md`.
- Personal data in the repo: anything from `data/` or a real workout export or food log in
  fixtures, docs, issues or commits.
- A knowledge rule whose Evidence states a fact that its cited source's `Supports:` line does not
  contain, or a `Supports:` quote that is not verbatim (cuts only with `...`). A condensed summary
  is labelled `Condensed:` and is not a quote.
- A risk-gate change that lets a risky PR pass: an approval not tied to the commit Matías
  reviewed, or an error (failed API call, cut-off file list) that passes instead of failing.

## How to report

- Report correctness, security and behaviour regressions; style, naming and formatting belong to the linters.
- Cite `file:line` from code you opened for every finding.
- Mark findings that predate this change as **pre-existing**.
- Open with a summary: the number of findings, or the line "No issues found."

## Ignore

- `uv.lock`, `assets/`
- `knowledge/index.md` (built by `scripts/build_knowledge_index.py`)
- `foods/base.csv` (built by `scripts/build_food_table.py` from `foods/base_ids.tsv`; review the
  ID list instead)

## Risky paths

Listed in `.github/risk-paths`. A PR touching them merges only with Matías's `human-ok` label.
