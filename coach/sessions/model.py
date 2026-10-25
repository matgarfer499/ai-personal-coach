"""The normalised, source-agnostic session log: one ExerciseSet per logged set."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime
from itertools import groupby

KNOWN_SET_TYPES = ("normal", "warmup", "dropset", "failure")


@dataclass(frozen=True)
class ExerciseSet:
    source: str  # importer name, e.g. "hevy_csv"
    start_time: datetime  # session start, naive local time
    exercise: str
    exercise_index: int  # position of the exercise block in the session (0-based)
    set_index: int  # position of the set within the block (0-based)
    set_type: str = "normal"  # unknown types are kept as given
    weight_kg: float | None = None  # None for bodyweight exercises
    reps: int | None = None
    rir: float | None = None
    rpe: float | None = None
    distance_km: float | None = None
    duration_s: int | None = None
    session_title: str = ""
    notes: str = ""

    @property
    def date(self) -> date:
        return self.start_time.date()

    @property
    def is_empty(self) -> bool:
        """No reps, weight, duration or distance: a template leftover, not a performed set. A
        duration-only set (a plank) or a bodyweight set with reps is not empty."""
        return (
            self.reps is None
            and self.weight_kg is None
            and self.duration_s is None
            and self.distance_km is None
        )

    @property
    def session_id(self) -> str:
        return f"{self.source}:{self.start_time.isoformat()}"

    @property
    def key(self) -> tuple:
        """Identity for de-duplication across overlapping exports.

        The plan's key (source, start_time, exercise, set_index) plus exercise_index, because
        Hevy restarts set_index for each block and the same exercise can appear twice in one
        session.
        """
        return (self.source, self.start_time, self.exercise, self.exercise_index, self.set_index)


@dataclass
class Session:
    source: str
    start_time: datetime
    title: str
    sets: list[ExerciseSet] = field(default_factory=list)

    @property
    def session_id(self) -> str:
        return f"{self.source}:{self.start_time.isoformat()}"


def sort_key(s: ExerciseSet) -> tuple:
    return (s.start_time, s.source, s.exercise_index, s.set_index)


def group_sessions(sets: list[ExerciseSet]) -> list[Session]:
    sessions = []
    ordered = sorted(sets, key=sort_key)
    for (source, start), rows in groupby(ordered, key=lambda s: (s.source, s.start_time)):
        group = list(rows)
        sessions.append(Session(source, start, group[0].session_title, group))
    return sessions
