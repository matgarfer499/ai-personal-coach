"""data/sessions.csv: read the log, and append imported sets without duplicates.

When an incoming set has the same key as a stored one (for example a re-export after editing a
set in the workout app), the stored row wins and the incoming one counts as a duplicate.
"""

from __future__ import annotations

import csv
import os
from dataclasses import dataclass, fields
from datetime import datetime
from pathlib import Path

from coach.sessions.model import ExerciseSet, sort_key

FIELDS = [f.name for f in fields(ExerciseSet)]
_INTS = {"exercise_index", "set_index", "reps", "duration_s"}
_FLOATS = {"weight_kg", "rir", "rpe", "distance_km"}


class StoreError(ValueError):
    pass


@dataclass
class AppendResult:
    added: int
    duplicates: int


def _parse(row: dict[str, str]) -> ExerciseSet:
    values: dict = {}
    for name in FIELDS:
        raw = row.get(name, "")
        if name == "start_time":
            values[name] = datetime.fromisoformat(raw)
        elif name in _INTS:
            values[name] = int(raw) if raw != "" else None
        elif name in _FLOATS:
            values[name] = float(raw) if raw != "" else None
        else:
            values[name] = raw
    return ExerciseSet(**values)


def _format(s: ExerciseSet) -> list[str]:
    out = []
    for name in FIELDS:
        value = getattr(s, name)
        if value is None:
            out.append("")
        elif isinstance(value, datetime):
            out.append(value.isoformat())
        else:
            out.append(str(value))
    return out


def read_sets(path: Path) -> list[ExerciseSet]:
    """Read the log. utf-8-sig tolerates a BOM left by a spreadsheet; a header that is not
    exactly the store's columns is refused rather than guessed (a missing column would read as
    blanks, an extra one would be lost on the next write)."""
    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        header = reader.fieldnames or []
        missing, extra = set(FIELDS) - set(header), set(header) - set(FIELDS)
        if missing or extra:
            raise StoreError(
                f"{path}: unexpected header (missing: {', '.join(sorted(missing)) or 'none'}; "
                f"extra: {', '.join(sorted(extra)) or 'none'}); restore the columns {FIELDS}"
            )
        sets = []
        for line, row in enumerate(reader, start=2):
            try:
                sets.append(_parse(row))
            except (TypeError, ValueError) as err:
                raise StoreError(f"{path}: line {line}: {err}") from None
        return sets


def append(sets: list[ExerciseSet], path: Path) -> AppendResult:
    path = Path(path)
    stored = read_sets(path)
    seen = {s.key for s in stored}
    added = []
    for s in sets:
        if s.key not in seen:
            seen.add(s.key)
            added.append(s)
    rows = sorted(stored + added, key=sort_key)
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        writer.writerows(_format(s) for s in rows)
    os.replace(tmp, path)
    return AppendResult(added=len(added), duplicates=len(sets) - len(added))
