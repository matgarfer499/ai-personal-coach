# Adding a workout-app importer

The coach keeps one source-agnostic log, `data/sessions.csv`: one row per set, as
`coach.sessions.model.ExerciseSet`. An importer turns one exported file from some app into a list
of `ExerciseSet`s. It never writes anything: `coach import` hands the list to the store, which
de-duplicates and saves.

Built-in importers: `hevy_csv` (Hevy's CSV export) and `generic_csv` (a hand-written CSV, columns
listed in `coach/sessions/importers/generic_csv.py`). Hevy's private web API is a possible future
importer; it is not built.

## The protocol

```python
class Importer(Protocol):
    name: str  # stored in every row's `source`

    def can_read(self, path: Path) -> bool: ...  # cheap check, usually the CSV header
    def read(self, path: Path) -> list[ExerciseSet]: ...
```

`coach.sessions.importers.base.register(importer)` adds it to the registry. `coach import FILE`
asks every importer `can_read` and refuses the file if none or more than one says yes, so make
`can_read` specific (check the full header, not one column). `coach import FILE --importer NAME`
skips detection.

### What each `ExerciseSet` field means

| Field | Meaning |
|---|---|
| `source` | the importer's `name` |
| `start_time` | session start, naive local time (drop any timezone) |
| `exercise` | the app's exercise name, as written |
| `exercise_index` | 0-based position of the exercise block in the session |
| `set_index` | the app's 0-based set number within the block (gaps allowed); if the app has none, the set's position in the block |
| `set_type` | `normal`, `warmup`, `dropset` or `failure`, lower-case; keep unknown values as they are |
| `weight_kg` | kilograms; `None` for bodyweight sets (never 0) |
| `reps`, `rir`, `rpe` | as logged; `None` when blank |
| `distance_km`, `duration_s` | for cardio rows |
| `session_title`, `notes` | free text |

`date` and `session_id` are derived from `start_time` and `source`.

### Rules the store and calculators rely on

- **De-duplication key:** `(source, start_time, exercise, exercise_index, set_index)`. Exports
  usually contain the whole history, so the same set arrives again and again. Make the key stable:
  the same set must get the same values in every export. When a stored row and an incoming row
  share a key (for example after the user edited a set in the app), **the stored row wins** and the
  incoming one counts as a duplicate.
- **Blocks:** if the app does not number exercise blocks, use `base.block_indexes`, which starts a
  new block when the session or exercise changes or when the app's set number restarts (the same
  exercise twice in one session).
- **Units:** convert to kg and km with `base.KG_PER_LB` and `base.KM_PER_MILE` (exact definitions).
  `base.metric(row, "weight_kg", "weight_lbs", KG_PER_LB, line)` reads whichever column is present.
- **Warm-ups** must be marked `warmup`: weekly hard sets and progression skip them.
- **Dates:** parse month names with an explicit English table, not `strptime("%b")`, which follows
  the machine's locale. Raise `ImporterError` naming the bad value rather than dropping a row: a
  lost timestamp removes a whole session from every weekly figure.
- **Encoding:** open CSVs with `encoding="utf-8-sig"` (`base.read_rows` does) so a BOM does not end
  up in the first column's name. `base.read_rows` keeps identical rows: within one export they
  are real sets (three straight sets of 100 x 5). Overlap between exports is the store's job.
- **Empty sets:** return them as they are. `coach import` skips every set with no reps, weight,
  duration or distance (`ExerciseSet.is_empty`: a routine-template leftover) and reports the count
  and names in `warnings`; a duration-only set such as a plank is kept.
- **Bad input:** a row with more fields than the header (often a decimal comma), a non-finite
  number or a fractional rep count raises `ImporterError` with the line number; `base.number`
  does this for you.

## Worked example

A fictional app, "LiftLog", exports `Day,Lift,Set,Kg,Reps,Warmup` with dates like `2025-08-20`.
This is the whole importer, about 30 lines of code (the test suite runs this exact code):

```python
from datetime import datetime
from pathlib import Path

from coach.sessions.importers import base
from coach.sessions.model import ExerciseSet


class LiftLogCsv:
    name = "liftlog_csv"

    def can_read(self, path: Path) -> bool:
        return base.read_header(path) == ["Day", "Lift", "Set", "Kg", "Reps", "Warmup"]

    def read(self, path: Path) -> list[ExerciseSet]:
        rows = list(enumerate(base.read_rows(path), start=2))  # (line, row)
        try:
            starts = [datetime.fromisoformat(r["Day"]) for _, r in rows]
        except ValueError as err:
            raise base.ImporterError(f"{path}: {err}") from None
        numbers = [base.number(r, "Set", line, int) for line, r in rows]
        if None in numbers:
            raise base.ImporterError(f"{path}: every row needs a Set number")
        lifts = [r["Lift"] for _, r in rows]
        blocks = base.block_indexes(starts, lifts, [n - 1 for n in numbers])
        return [
            ExerciseSet(
                self.name,
                start,
                row["Lift"],
                block,
                set_index,
                set_type="warmup" if row["Warmup"] == "yes" else "normal",
                weight_kg=base.number(row, "Kg", line),
                reps=base.number(row, "Reps", line, int),
            )
            for (line, row), start, (block, set_index) in zip(rows, starts, blocks, strict=True)
        ]


base.register(LiftLogCsv())
```

To ship it, save it as `coach/sessions/importers/liftlog_csv.py` and import it in
`coach/sessions/importers/__init__.py` so it registers.

## Fixtures and tests

1. **Write fixtures by hand.** Put small synthetic CSVs under `tests/fixtures/<app>/`. Never copy
   a real export, not even "anonymised": workout logs are personal data, and personal data lives
   only in `data/` (gitignored).
2. **One fixture per quirk.** Cover a BOM, the app's date format, warm-ups, bodyweight sets with no
   weight, unit variants, a repeated exercise in one session, and an overlapping second export.
   See `tests/fixtures/hevy/` and `tests/sessions/test_importers.py` for the Hevy set.
3. **Assert the normalised values,** not just the row count: `start_time`, `weight_kg`
   (converted), `set_type`, `exercise_index` and `set_index`.
4. **Check de-duplication through the store:** import the first export, then the overlapping one,
   and assert `AppendResult(added, duplicates)`.
5. **Check detection:** `base.detect(path).name` should be your importer for your fixtures, and no
   other importer's fixture should be claimed by yours.

Run `uv run pytest` and `uv run ruff check .` before committing.
