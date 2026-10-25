"""A plain CSV anyone can write by hand or export from a spreadsheet.

Required columns: `date` (YYYY-MM-DD, or YYYY-MM-DD HH:MM for two sessions on one day) and
`exercise`. Optional: `weight_kg` or `weight_lbs`, `reps`, `rir`, `rpe`, `set_type` (normal,
warmup, dropset, failure; blank means normal), `distance_km` or `distance_miles`, `duration_s`,
`session` (a title) and `notes`. Rows with the same `date` value form one session; consecutive
rows of the same exercise form one block, in file order.
"""

from __future__ import annotations

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

REQUIRED = {"date", "exercise"}
OPTIONAL = {
    "weight_kg",
    "weight_lbs",
    "reps",
    "rir",
    "rpe",
    "set_type",
    "distance_km",
    "distance_miles",
    "duration_s",
    "session",
    "notes",
}


def _start(text: str, line: int) -> datetime:
    try:
        return datetime.fromisoformat(text.strip())
    except ValueError:
        raise ImporterError(f"line {line}: date {text!r} is not YYYY-MM-DD[ HH:MM]") from None


class GenericCsv:
    name = "generic_csv"

    def can_read(self, path: Path) -> bool:
        header = set(read_header(path))
        return REQUIRED <= header and header <= REQUIRED | OPTIONAL

    def read(self, path: Path) -> list[ExerciseSet]:
        require_columns(read_header(path), REQUIRED, path)
        rows = read_rows(path)
        starts = [_start(r["date"], n) for n, r in enumerate(rows, start=2)]
        exercises = [r["exercise"].strip() for r in rows]
        blocks = block_indexes(starts, exercises, [None] * len(rows))
        return [
            ExerciseSet(
                source=self.name,
                start_time=start,
                exercise=exercise,
                exercise_index=exercise_index,
                set_index=set_index,
                set_type=(row.get("set_type") or "normal").strip().lower(),
                weight_kg=metric(row, "weight_kg", "weight_lbs", KG_PER_LB, line),
                reps=number(row, "reps", line, int),
                rir=number(row, "rir", line),
                rpe=number(row, "rpe", line),
                distance_km=metric(row, "distance_km", "distance_miles", KM_PER_MILE, line),
                duration_s=number(row, "duration_s", line, int),
                session_title=(row.get("session") or "").strip(),
                notes=(row.get("notes") or "").strip(),
            )
            for line, (row, start, exercise, (exercise_index, set_index)) in enumerate(
                zip(rows, starts, exercises, blocks, strict=True), start=2
            )
        ]


register(GenericCsv())
