# Contributing

Thanks for helping. This repo is a template: people copy it, keep their own data private and
adapt it to their country. Contributions that make that easier for everyone fit best.

## Never share personal data

Do not paste anything from your `data/` folder (profile, screening answers, check-ins, workouts,
menus, plans) into an issue, a pull request, a commit or a test fixture. Describe the problem with
an invented client instead; `tests/skills/*/client.md` and
[`docs/testing-guide.md`](docs/testing-guide.md) have some. Test fixtures are synthetic and
written fresh.

When you open a pull request from your own copy, check the "base repository": GitHub may target
this public repo by default.

## What fits

- **Fixes** with the failing case shown: a test that fails before the fix and passes after, on
  input the coach really produces (a CLI call, a real export format, a skill step).
- **Evidence:** new or corrected rules in `knowledge/`, each with a grade and sources that exist
  in `knowledge/sources.md`. Prefer running `/research`, which records what was checked and what
  was dropped.
- **Regions and importers** that follow [`docs/adding-a-region.md`](docs/adding-a-region.md) and
  [`docs/adding-an-importer.md`](docs/adding-an-importer.md). Supermarket data goes in only when
  the chain's terms allow publishing it.
- **Docs** that close a real gap.

One concern per pull request.

## How to change the code

1. Write the test first, watch it fail, then write the code.
2. Every constant in `coach/` cites the knowledge rule it comes from; a number no rule gives is
   labelled `# convention:` and listed in [`docs/conventions.md`](docs/conventions.md).
3. Run the checks (CI runs the same):

   ```
   uv run pytest
   uv run ruff check .
   uv run python scripts/check_knowledge.py
   uv run python scripts/build_knowledge_index.py  # after editing knowledge/, then commit the result
   ```

4. Commit style: `feat(coach): ...`, `fix(coach): ...`, `docs(knowledge): ...`, `chore: ...`.

The full rules for working in the repo, for people and agents, are in [`CLAUDE.md`](CLAUDE.md).

## Safety changes

Changes that touch screening, red flags, calorie floors or the safety flags need a test for the
case they protect and an update to [`docs/safety.md`](docs/safety.md). If you are unsure whether
something is safe, open an issue first.

## Licence

By contributing you agree that code is released under the MIT licence ([`LICENSE`](LICENSE)) and
content under CC BY 4.0 ([`LICENSE-CONTENT.md`](LICENSE-CONTENT.md)).
