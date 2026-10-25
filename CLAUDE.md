# AI personal coach

An evidence-based personal coach that runs inside Claude Code. Claude Code is the runtime: each coach
command is a project skill in `.claude/skills/<name>/SKILL.md`; every number comes from the `coach`
Python package (`uv run python -m coach ... --json`), never from the model's own arithmetic. The
evidence base lives in `knowledge/`.

## Where things are

- `knowledge/*.md`: rules with grades and `[Sxxx]` source IDs. `knowledge/sources.md`: the sources.
- `docs/research-methodology.md`, `docs/dropped-claims.md`: how the evidence was gathered.
- `coach/`: the numbers package. `tests/` mirrors it. `scripts/`: knowledge checks and index build.

## Changing the code

1. Test first. Then code.
2. Run the checks below; fix root causes, never weaken a test or a check.
3. Commit style: `feat(coach): ...`, `docs(knowledge): ...`, `chore: ...`.
4. Never force-push, never change repo visibility.

## Checks

```
uv run pytest
uv run ruff check .
uv run ruff format --check .
uv run python scripts/check_knowledge.py        # before any commit touching knowledge/
uv run python scripts/build_knowledge_index.py  # after editing knowledge/ (also updates the README
                                                # rule and source counts), then re-check
```

The same checks run in CI (`.github/workflows/checks.yml`).

## Rules

- **Privacy:** personal data lives only in `data/` (gitignored) or the folder `COACH_DATA_DIR`
  names. Test fixtures are synthetic and written fresh; never copy anything from a real workout
  export, food log or other personal data, your own included, into fixtures, docs, issues or
  commits. Never open `data/` unless the person asks.
- **Constants:** every constant in `coach/` comes from a knowledge rule, and its comment names the
  file and rule heading, e.g. `# nutrition.md: "Default RMR equation: Mifflin-St Jeor"`. A number
  with no rule is labelled `# convention:` and listed in `docs/conventions.md`.
- **Knowledge format:** `### <rule>` headings, exactly one `**Grade:**` (strong, moderate or
  emerging) per rule, `[Sxxx]` IDs that exist in `sources.md`, no en or em dashes, and an
  `Evidence checked on YYYY-MM-DD` header line.
- **Loading knowledge:** read `knowledge/index.md` first, then only the sections you need
  (`coach.knowledge.section(file, heading)`). Never read `sources.md` whole; grep it by ID
  (`grep -n -A6 '^### S123$' knowledge/sources.md`).
- **Safety:** skills end advice with the deferral line from `docs/safety.md` when a red flag fired
  and never prescribe below the calorie floors or a deficit after a positive screen.
