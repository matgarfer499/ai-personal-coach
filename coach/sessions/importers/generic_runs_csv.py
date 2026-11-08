"""A plain run log anyone can write by hand or export from a spreadsheet.

Required columns: `date` (YYYY-MM-DD, or YYYY-MM-DD HH:MM), `distance_km` or `distance_miles`,
and `duration_minutes` or `duration_seconds`. Optional: `avg_hr`, `max_hr` (bpm), `rpe`
(Borg 6-20) and `notes`. One row per run. `target = "runs"`: `coach import` stores these in
data/runs.csv, not in data/sessions.csv.
"""

from __future__ import annotations

from datetime import datetime
from pathlib import Path

from coach import runs
from coach.sessions.importers.base import (
    KM_PER_MILE,
    ImporterError,
    metric,
    number,
    read_header,
    read_rows,
    register,
)

DISTANCE = ("distance_km", "distance_miles")
DURATION = ("duration_minutes", "duration_seconds")
OPTIONAL = {"avg_hr", "max_hr", "rpe", "notes"}
SECONDS_PER_MINUTE = 60  # a unit definition, not a coaching number


class GenericRunsCsv:
    name = "generic_runs_csv"
    target = "runs"

    def can_read(self, path: Path) -> bool:
        header = set(read_header(path))
        return (
            "date" in header
            and bool(header & set(DISTANCE))
            and bool(header & set(DURATION))
            and header <= {"date", *DISTANCE, *DURATION, *OPTIONAL}
        )

    def read(self, path: Path) -> list[runs.Run]:
        out = []
        for line, row in enumerate(read_rows(path), start=2):
            try:
                day = datetime.fromisoformat(row["date"].strip()).date()
            except (KeyError, ValueError):
                raise ImporterError(
                    f"line {line}: date {row.get('date')!r} is not YYYY-MM-DD[ HH:MM]"
                ) from None
            km = metric(row, "distance_km", "distance_miles", KM_PER_MILE, line)
            # Unrounded: Run.key rounds minutes to 1 decimal, and rounding twice can move the key.
            minutes = metric(
                row, "duration_minutes", "duration_seconds", 1 / SECONDS_PER_MINUTE, line, None
            )
            if km is None or minutes is None:
                raise ImporterError(f"line {line}: every run needs a distance and a duration")
            run = runs.Run(
                day,
                km,
                minutes,
                avg_hr=number(row, "avg_hr", line, int),
                max_hr=number(row, "max_hr", line, int),
                rpe=number(row, "rpe", line, int),
                notes=(row.get("notes") or "").strip(),
                source=self.name,
            )
            try:
                runs.check(run)
            except ValueError as err:
                raise ImporterError(f"line {line}: {err}") from None
            out.append(run)
        return out


register(GenericRunsCsv())
