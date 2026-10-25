"""The importer protocol, the registry, and helpers shared by CSV importers.

An importer turns one exported file into normalised `ExerciseSet`s. It never writes; the store
de-duplicates. See docs/adding-an-importer.md.
"""

from __future__ import annotations

import csv
import math
from collections.abc import Hashable, Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from coach.sessions.model import ExerciseSet

# Exact unit definitions (international pound and mile), not coaching numbers.
KG_PER_LB = 0.45359237
KM_PER_MILE = 1.609344


class ImporterError(ValueError):
    pass


@runtime_checkable
class Importer(Protocol):
    name: str

    def can_read(self, path: Path) -> bool: ...

    def read(self, path: Path) -> list[ExerciseSet]: ...


IMPORTERS: list[Importer] = []


def register(importer: Importer) -> Importer:
    IMPORTERS.append(importer)
    return importer


def get(name: str) -> Importer:
    for importer in IMPORTERS:
        if importer.name == name:
            return importer
    raise ImporterError(
        f"no importer named {name!r}; known: {', '.join(i.name for i in IMPORTERS)}"
    )


def detect(path: Path) -> Importer:
    matches = [i for i in IMPORTERS if i.can_read(Path(path))]
    if not matches:
        raise ImporterError(f"no importer can read {path}")
    if len(matches) > 1:
        names = ", ".join(i.name for i in matches)
        raise ImporterError(f"more than one importer can read {path} ({names}); pick one by name")
    return matches[0]


def read_header(path: Path) -> list[str]:
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        return next(csv.reader(handle), [])


def read_rows(path: Path) -> list[dict[str, str]]:
    """Rows as dicts, in file order. utf-8-sig strips the BOM some exports carry, which would
    otherwise become part of the first column's name.

    Identical rows are kept: within one export they are real sets (three straight sets of
    100 x 5, or an exercise repeated with the same numbers). Overlap between exports is the
    store's job, through the de-duplication key."""
    with Path(path).open(newline="", encoding="utf-8-sig") as handle:
        rows = list(csv.DictReader(handle))
    for line, row in enumerate(rows, start=2):
        if None in row:
            raise ImporterError(
                f"{path}: line {line} has more fields than the header "
                "(a decimal comma such as 12,5? use 12.5)"
            )
    return rows


def require_columns(header: Iterable[str], needed: Iterable[str], path: Path) -> None:
    missing = sorted(set(needed) - set(header))
    if missing:
        raise ImporterError(f"{path}: missing columns {', '.join(missing)}")


def number(row: dict[str, str], name: str, line: int, kind: type = float) -> float | int | None:
    raw = (row.get(name) or "").strip()
    if raw == "":
        return None
    try:
        value = float(raw)
    except ValueError:
        raise ImporterError(f"line {line}: {name} {raw!r} is not a number") from None
    if not math.isfinite(value):
        raise ImporterError(f"line {line}: {name} {raw!r} is not a finite number")
    if kind is int:
        if not value.is_integer():
            raise ImporterError(f"line {line}: {name} {raw!r} must be a whole number")
        return int(value)
    return value


def metric(
    row: dict[str, str], metric_name: str, imperial_name: str, factor: float, line: int
) -> float | None:
    """A value from the metric column, or the imperial one converted."""
    value = number(row, metric_name, line)
    if value is None and (imperial := number(row, imperial_name, line)) is not None:
        value = imperial * factor
    return value


@dataclass
class _SessionBlocks:
    block: int = -1  # current exercise_index
    exercise: str | None = None  # exercise of the previous row
    last_set_index: int | None = None  # logged set_index of the previous row
    position: int = 0  # position of the next row within the block


def block_indexes(
    keys: list[Hashable], exercises: list[str], set_indexes: list[int | None]
) -> list[tuple[int, int]]:
    """(exercise_index, set_index) for rows in file order.

    A new block starts when the session or the exercise changes, or when the logged set_index
    stops increasing (the same exercise done twice in one session). Missing set indexes are
    numbered within their block.
    """
    # Per-session state, so a session whose rows are not contiguous keeps counting its blocks.
    sessions: dict[Hashable, _SessionBlocks] = {}
    out = []
    for key, exercise, set_index in zip(keys, exercises, set_indexes, strict=True):
        if key not in sessions:
            sessions[key] = _SessionBlocks()
        state = sessions[key]
        restarted = (
            set_index is not None
            and state.last_set_index is not None
            and set_index <= state.last_set_index
        )
        if exercise != state.exercise or restarted:
            state.block += 1
            state.position = 0
        out.append((state.block, state.position if set_index is None else set_index))
        state.position += 1
        state.exercise = exercise
        state.last_set_index = set_index
    return out
