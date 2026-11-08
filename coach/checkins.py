"""Daily check-ins: data/checkins.csv (one row per day; a later check-in that day fills in or
overrides only the fields it gives, and appends its notes)."""

from __future__ import annotations

import csv
from dataclasses import astuple, dataclass, fields, replace
from datetime import date
from pathlib import Path

# Plausibility limits for typed-in values (convention: input validation, not coaching).
RANGES = {
    "weight_kg": (25.0, 400.0),
    "waist_cm": (40.0, 250.0),
    "intake_kcal": (0.0, 15000.0),
    "sleep_hours": (0.0, 24.0),
}


# convention: a typo check, not coaching: nutrition.md "Read the scale with weekly averages"
# puts normal within-week swings near 0.35% of body weight, so a change of more than 1 kg per
# day from the nearest other weigh-in is flagged for the client to confirm; the allowance stops
# growing after a week, so a typo after a long gap is still caught.
JUMP_KG_PER_DAY = 1.0
JUMP_MAX_DAYS = 7


def weight_jump(checkin: Checkin, earlier: list[Checkin]) -> str | None:
    """A warning when the new weight is implausibly far from the nearest other weigh-in."""
    others = [c for c in earlier if c.weight_kg is not None and c.date != checkin.date]
    if checkin.weight_kg is None or not others:
        return None
    near = min(others, key=lambda c: abs((c.date - checkin.date).days))
    change, days = checkin.weight_kg - near.weight_kg, abs((near.date - checkin.date).days)
    if abs(change) <= JUMP_KG_PER_DAY * min(days, JUMP_MAX_DAYS):
        return None
    return (
        f"weight {checkin.weight_kg:g} kg is {abs(change):g} kg away from {near.weight_kg:g} kg on "
        f"{near.date} ({days} day{'s' if days > 1 else ''}): stored; confirm it is not a typo"
    )


@dataclass
class Checkin:
    date: date
    weight_kg: float | None = None
    waist_cm: float | None = None
    intake_kcal: float | None = None
    sleep_hours: float | None = None
    notes: str = ""


FIELDS = [f.name for f in fields(Checkin)]


def _parse(row: dict[str, str]) -> Checkin:
    def number(name: str) -> float | None:
        return float(row[name]) if row.get(name) else None

    return Checkin(
        date=date.fromisoformat(row["date"]),
        weight_kg=number("weight_kg"),
        waist_cm=number("waist_cm"),
        intake_kcal=number("intake_kcal"),
        sleep_hours=number("sleep_hours"),
        notes=row.get("notes") or "",
    )


def read_checkins(path: Path) -> list[Checkin]:
    path = Path(path)
    if not path.exists():
        return []
    # utf-8-sig: a file saved by a spreadsheet may start with a byte-order mark.
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        if "date" not in (reader.fieldnames or []):
            raise ValueError(f"{path} has no 'date' column; expected {','.join(FIELDS)}")
        return [_parse(row) for row in reader]


def append_checkin(checkin: Checkin, path: Path) -> Checkin:
    """Stores the day's check-in, merged with any earlier one that day; returns the stored row."""
    for name, (low, high) in RANGES.items():
        value = getattr(checkin, name)
        if value is not None and not low <= value <= high:
            raise ValueError(f"{name} {value} is outside {low}-{high}")
    path = Path(path)
    rows = read_checkins(path)
    for earlier in (c for c in rows if c.date == checkin.date):
        given = {k: v for k, v in vars(checkin).items() if v is not None and v != ""}
        if earlier.notes and checkin.notes:
            # notes add up (a symptom noted earlier must stay); a part stored once is not repeated
            parts = earlier.notes.split("; ")
            parts += [p for p in checkin.notes.split("; ") if p not in parts]
            given["notes"] = "; ".join(parts)
        checkin = replace(earlier, **given)
    rows = [c for c in rows if c.date != checkin.date] + [checkin]
    rows.sort(key=lambda c: c.date)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        for row in rows:
            writer.writerow(["" if v is None else v for v in astuple(row)])
    return checkin


def weigh_ins(checkins: list[Checkin]) -> list[tuple[date, float]]:
    return [(c.date, c.weight_kg) for c in checkins if c.weight_kg is not None]
