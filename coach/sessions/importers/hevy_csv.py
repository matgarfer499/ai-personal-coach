"""Hevy's CSV export (Hevy app: Settings > Export Data).

Reads one row per set, with the columns in COMMON plus either the kilogram and kilometre pair
(`weight_kg`, `distance_km`) or the pound and mile pair (`weight_lbs`, `distance_miles`), which
are converted to metric. Dates look like "24 Jul 2026, 11:25" with English month names whatever
the phone's language; ISO timestamps are accepted too. Hevy numbers sets within each exercise
block, so the importer derives the block position from those numbers (the same exercise twice in
one session stays two blocks). It returns every row, including rows with no reps, weight,
duration or distance that Hevy leaves for routine-template sets that were never filled in;
`coach import` skips and reports those.
"""

from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from coach.sessions.importers.base import (
    KG_PER_LB,
    KM_PER_MILE,
    ImporterError,
    block_indexes,
    metric,
    number,
    read_header,
    read_rows,
    register,
    require_columns,
)
from coach.sessions.model import ExerciseSet

COMMON = {
    "title",
    "start_time",
    "end_time",
    "description",
    "exercise_title",
    "superset_id",
    "exercise_notes",
    "set_index",
    "set_type",
    "reps",
    "duration_seconds",
    "rpe",
}
UNIT_VARIANTS = ({"weight_kg", "distance_km"}, {"weight_lbs", "distance_miles"})

# English month abbreviations, not %b: strptime's %b follows the locale (Spanish here).
MONTHS = {
    m: i
    for i, m in enumerate(
        ["jan", "feb", "mar", "apr", "may", "jun", "jul", "aug", "sep", "oct", "nov", "dec"],
        start=1,
    )
}
HEVY_DATETIME = re.compile(
    r"^\s*(\d{1,2})\s+([A-Za-z]{3})[a-z]*\.?\s+(\d{4}),\s*(\d{1,2}):(\d{2})\s*$"
)


def parse_datetime(text: str) -> datetime:
    if match := HEVY_DATETIME.match(text):
        day, month, year, hour, minute = match.groups()
        month = month.lower()
        if month in MONTHS:
            try:
                return datetime(int(year), MONTHS[month], int(day), int(hour), int(minute))
            except ValueError:
                raise ImporterError(f"impossible timestamp {text!r}") from None
    try:
        parsed = datetime.fromisoformat(text.strip())
    except ValueError:
        raise ImporterError(f"unparseable timestamp {text!r}") from None
    return parsed.replace(tzinfo=None)


class HevyCsv:
    name = "hevy_csv"

    def can_read(self, path: Path) -> bool:
        header = set(read_header(path))
        return COMMON <= header and any(v <= header for v in UNIT_VARIANTS)

    def read(self, path: Path) -> list[ExerciseSet]:
        header = read_header(path)
        unit_columns = next((v for v in UNIT_VARIANTS if v <= set(header)), UNIT_VARIANTS[0])
        require_columns(header, COMMON | unit_columns, path)
        rows = read_rows(path)
        starts = [parse_datetime(r["start_time"]) for r in rows]
        keys = [(start, r["title"]) for start, r in zip(starts, rows, strict=True)]
        set_indexes = [number(r, "set_index", n, int) for n, r in enumerate(rows, start=2)]
        blocks = block_indexes(keys, [r["exercise_title"] for r in rows], set_indexes)
        sets = []
        for line, (row, start, (exercise_index, set_index)) in enumerate(
            zip(rows, starts, blocks, strict=True), start=2
        ):
            sets.append(
                ExerciseSet(
                    source=self.name,
                    start_time=start,
                    exercise=row["exercise_title"].strip(),
                    exercise_index=exercise_index,
                    set_index=set_index,
                    set_type=(row["set_type"] or "normal").strip().lower(),
                    weight_kg=metric(row, "weight_kg", "weight_lbs", KG_PER_LB, line),
                    reps=number(row, "reps", line, int),
                    rpe=number(row, "rpe", line),
                    distance_km=metric(row, "distance_km", "distance_miles", KM_PER_MILE, line),
                    duration_s=number(row, "duration_seconds", line, int),
                    session_title=row["title"].strip(),
                    notes=row["exercise_notes"].strip(),
                )
            )
        return sets


register(HevyCsv())
