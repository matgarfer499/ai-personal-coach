"""Runs: data/runs.csv (one row per run), the weekly figures and the taper.

Runs are kept apart from data/sessions.csv (one row per lifting set): a run has a distance, a
duration and heart rates, and is summed per week in km, not in hard sets. `coach runs add` and
run importers (`coach import`) write here; `coach runs week` and `coach runs taper` read it.
"""

from __future__ import annotations

import csv
import os
from collections import Counter
from dataclasses import astuple, dataclass, fields
from datetime import date, timedelta
from pathlib import Path

from coach import safety, zones
from coach.profile import HR_MAX_RANGE, HR_REST_RANGE, Profile
from coach.safety import SafetyFlags

LOAD_RULE = (
    'cardio-health.md: "Running load progression: cap single-run spikes, not just weekly totals"'
)
TAPER_RULE = 'cardio-health.md: "Taper before a goal race"'

# cardio-health.md: "Running load progression: cap single-run spikes, not just weekly totals":
# a single run no more than about 10% longer than the longest run of the previous 30 days.
SPIKE_RATIO = 1.10
SPIKE_LOOKBACK_DAYS = 30
# cardio-health.md: "Taper before a goal race": about 2 weeks (up to 3 is reasonable), weekly
# distance cut progressively by about 41-60%, intensity and runs per week kept.
TAPER_WEEKS = 2
TAPER_MAX_WEEKS = 3
TAPER_CUT = (0.41, 0.60)

# Plausibility limits for typed-in values (convention: input validation, not coaching). Heart
# rates use the profile's resting floor and HRmax ceiling; RPE is the Borg 6-20 scale of
# `coach zones`.
RANGES = {"km": (0.1, 250.0), "minutes": (1.0, 2400.0)}
RUN_HR_RANGE = (HR_REST_RANGE[0], HR_MAX_RANGE[1])
RPE_RANGE = (6, 20)
# convention: tooling, not coaching: the same date, km (to 10 m) and minutes (to 0.1 min) is the
# same run, whoever logged it, so a re-import or a run added by hand and imported later counts once.
KEY_DECIMALS = (2, 1)

HR_METHODS = ("hrr", "hrmax")
NO_HR = "no_hr"  # zone_minutes key for runs logged without an average HR


@dataclass(frozen=True)
class Run:
    date: date
    km: float
    minutes: float
    avg_hr: int | None = None
    max_hr: int | None = None
    rpe: int | None = None  # Borg 6-20
    notes: str = ""
    source: str = "manual"  # `coach runs add`, or the importer's name

    @property
    def key(self) -> tuple:
        return (self.date, round(self.km, KEY_DECIMALS[0]), round(self.minutes, KEY_DECIMALS[1]))


FIELDS = [f.name for f in fields(Run)]
_INTS = ("avg_hr", "max_hr", "rpe")


def check(run: Run) -> None:
    for name, (low, high) in RANGES.items():
        if not low <= getattr(run, name) <= high:
            raise ValueError(f"{name} {getattr(run, name):g} is outside {low:g}-{high:g}")
    for name in ("avg_hr", "max_hr"):
        value = getattr(run, name)
        if value is not None and not RUN_HR_RANGE[0] <= value <= RUN_HR_RANGE[1]:
            raise ValueError(f"{name} {value} bpm is outside {RUN_HR_RANGE[0]}-{RUN_HR_RANGE[1]}")
    if run.avg_hr is not None and run.max_hr is not None and run.avg_hr > run.max_hr:
        raise ValueError(f"avg_hr {run.avg_hr} is above max_hr {run.max_hr}")
    if run.rpe is not None and not RPE_RANGE[0] <= run.rpe <= RPE_RANGE[1]:
        raise ValueError(f"rpe {run.rpe} is outside the Borg scale {RPE_RANGE[0]}-{RPE_RANGE[1]}")


def _parse(row: dict[str, str]) -> Run:
    return Run(
        date=date.fromisoformat(row["date"]),
        km=float(row["km"]),
        minutes=float(row["minutes"]),
        **{name: int(row[name]) if row.get(name) else None for name in _INTS},
        notes=row.get("notes") or "",
        source=row.get("source") or "manual",
    )


def read_runs(path: Path) -> list[Run]:
    path = Path(path)
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        reader = csv.DictReader(handle)
        missing = set(FIELDS) - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"{path}: missing columns {', '.join(sorted(missing))}")
        out = []
        for line, row in enumerate(reader, start=2):
            try:
                out.append(_parse(row))
            except (TypeError, ValueError) as err:
                raise ValueError(f"{path}: line {line}: {err}") from None
        return out


@dataclass
class AppendResult:
    added: int
    duplicates: int


def append_runs(new: list[Run], path: Path) -> AppendResult:
    """Validates and stores runs; a run already stored (same key) is a duplicate."""
    for run in new:
        check(run)
    path = Path(path)
    stored = read_runs(path)
    # Matched one for one: two identical runs in one log are two runs, and a re-import of that
    # log matches both stored copies.
    unmatched = Counter(r.key for r in stored)
    added = []
    for run in new:
        if unmatched[run.key]:
            unmatched[run.key] -= 1
        else:
            added.append(run)
    rows = sorted(stored + added, key=lambda r: (r.date, r.source))
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".csv.tmp")
    with tmp.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(FIELDS)
        writer.writerows(["" if v is None else v for v in astuple(r)] for r in rows)
    os.replace(tmp, path)
    return AppendResult(added=len(added), duplicates=len(new) - len(added))


def longest(runs: list[Run], start: date, end: date) -> float | None:
    """The longest run from start to end, both included."""
    return max((r.km for r in runs if start <= r.date <= end), default=None)


def spikes(runs: list[Run], start: date, end: date) -> list[dict]:
    """Runs from start to end more than SPIKE_RATIO longer than the longest run of the
    SPIKE_LOOKBACK_DAYS before their day. A run with no earlier run to compare is not flagged."""
    found = []
    for run in sorted(runs, key=lambda r: r.date):
        if not start <= run.date <= end:
            continue
        before = longest(
            runs, run.date - timedelta(days=SPIKE_LOOKBACK_DAYS), run.date - timedelta(days=1)
        )
        if before is not None and run.km > before * SPIKE_RATIO:
            found.append(
                {
                    "date": run.date,
                    "km": run.km,
                    "longest_previous_km": before,
                    "cap_km": before * SPIKE_RATIO,
                }
            )
    return found


def zones_to_describe(
    profile: Profile, flags: SafetyFlags, hr_rest: int | None, hr_max: int | None, today: date
) -> list[zones.Zone]:
    """Every HR zone, before the caps, so a capped client's hard minutes are reported, not
    lost; empty when the zones are not HR-based. Never prescribe from these."""
    every = zones.all_zones(profile, flags, hr_rest, hr_max, today)
    return every.zones if every.method in HR_METHODS else []


def week(
    runs: list[Run],
    end: date,
    shown: zones.Zones,
    every: list[zones.Zone],
    today: date | None = None,
    hold_progression: bool = False,
) -> dict:
    """The 7 days ending on `end`: totals, the week before, spikes, the next run's cap and,
    with HR zones, minutes per zone. `shown` is `coach zones` (capped); `every` the uncapped
    zones (`zones_to_describe`). The next run's cap counts back from `today` (default `end`);
    with `hold_progression` (safety) it is the longest run itself, no 10% more."""
    start = end - timedelta(days=6)
    days = [r for r in runs if start <= r.date <= end]
    before = [r for r in runs if start - timedelta(days=7) <= r.date < start]
    km, previous_km = sum(r.km for r in days), sum(r.km for r in before)
    notes = []
    found = spikes(runs, start, end)
    if found:
        notes.append(
            f"{LOAD_RULE}: a run more than about {SPIKE_RATIO - 1:.0%} longer than the longest run "
            f"of the previous {SPIKE_LOOKBACK_DAYS} days raised the injury rate"
        )
    zone_minutes = None
    if shown.method in HR_METHODS:
        zone_minutes = {z.name: 0.0 for z in every} | {NO_HR: 0.0}
        for run in days:
            zone = zones.zone_for(every, run.avg_hr) if run.avg_hr is not None else None
            zone_minutes[zone.name if zone else NO_HR] += run.minutes
        notes.append(
            "convention: each run's minutes count in the zone of its average heart rate; "
            "intervals inside a run are not split out"
        )
        hidden = {z.name for z in every} - {z.name for z in shown.zones}
        held = sum(zone_minutes[name] for name in hidden)
        if held:
            caps = [n for n in shown.notes if n.startswith((safety.BP, safety.PARQ_THRESHOLDS))]
            notes.append(
                f"{held:g} min in zones held back ({', '.join(sorted(hidden))}): " + "; ".join(caps)
            )
        peak = max((r.max_hr for r in days if r.max_hr is not None), default=None)
        if peak is not None and shown.hr_max is not None and peak > shown.hr_max:
            notes.append(
                f"{zones.HRMAX_RULE}: a logged peak of {peak} bpm is above HRmax {shown.hr_max}; "
                f"if it came from a genuine all-out effort, store hr_max {peak} with "
                "`coach profile set` (the zones then use it)"
            )
    elif shown.method == "rpe":
        notes.append("no time per zone: the zones are RPE only, so judge intensity by RPE")
    else:
        notes += shown.notes  # no zones at all (training on hold, or the cardiac team's zones)
    today = today or end
    cap_base = longest(runs, today - timedelta(days=SPIKE_LOOKBACK_DAYS - 1), today)
    ratio = 1.0 if hold_progression else SPIKE_RATIO
    if hold_progression and cap_base is not None and shown.method != "no_training":
        notes.append(
            "progression is on hold (coach safety): the next long run stays at or below the "
            f"longest run of the last {SPIKE_LOOKBACK_DAYS} days"
        )
    return {
        "week": {"start": start, "end": end},
        "runs": len(days),
        "km": km,
        "minutes": sum(r.minutes for r in days),
        "longest_km": longest(days, start, end),
        "previous_week": {"km": previous_km, "runs": len(before)},
        "change_pct": (km - previous_km) / previous_km * 100 if previous_km else None,
        "spikes": found,
        # The next run's cap under the rule: 10% over the longest run of the last 30 days.
        # None while training is on hold: no next run to cap.
        "long_run_cap_km": cap_base * ratio
        if cap_base is not None and shown.method != "no_training"
        else None,
        "zone_method": shown.method,
        "zone_minutes": zone_minutes,
        "notes": notes,
    }


def taper(race: date, today: date, runs: list[Run]) -> dict:
    days = (race - today).days
    if days < 0:
        raise ValueError(f"the race date {race} is before today ({today})")
    starts_on = race - timedelta(weeks=TAPER_WEEKS)
    earliest = race - timedelta(weeks=TAPER_MAX_WEEKS)
    result = {
        "race_date": race,
        "in_window": race - today <= timedelta(weeks=TAPER_MAX_WEEKS),
        "weeks": TAPER_WEEKS,
        "max_weeks": TAPER_MAX_WEEKS,
        "starts_on": starts_on,
        "earliest_start": earliest,
        "distance_cut": TAPER_CUT,
        "keep": ["the intensity of key sessions", "the number of runs per week"],
        "rule": TAPER_RULE,
    }
    if not result["in_window"]:
        result["note"] = (
            f"{TAPER_RULE}: the race is {days} days away; the taper starts about {TAPER_WEEKS} "
            f"weeks before it ({starts_on}), {TAPER_MAX_WEEKS} at most ({earliest}). Train as "
            "planned until then"
        )
        return result
    # The weekly distance the taper cuts from: the 7 days before it starts (or up to today).
    ref_end = min(today, starts_on - timedelta(days=1))
    reference = sum(r.km for r in runs if ref_end - timedelta(days=6) <= r.date <= ref_end)
    result["reference_week"] = {"start": ref_end - timedelta(days=6), "end": ref_end}
    result["reference_week_km"] = reference
    # Where the progressive cut ends: the reference week less 60% to less 41%.
    result["taper_week_km"] = (
        (reference * (1 - TAPER_CUT[1]), reference * (1 - TAPER_CUT[0])) if reference else None
    )
    return result
