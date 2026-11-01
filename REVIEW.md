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

## How to report

- Report correctness, security and behaviour regressions; style, naming and formatting belong to the linters.
- Cite `file:line` from code you opened for every finding.
- Mark findings that predate this change as **pre-existing**.
- Open with a summary: the number of findings, or the line "No issues found."

## Ignore

- `uv.lock`, `assets/`
- `knowledge/index.md` (built by `scripts/build_knowledge_index.py`)
- `foods/base.csv`, `regions/*/foods.csv` (built by `scripts/build_food_table.py` from the
  `*_ids.tsv` lists; review the ID lists instead)

## Risky paths

Listed in `.github/risk-paths`. A PR touching them merges only with Matías's `human-ok` label.
