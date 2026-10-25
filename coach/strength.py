"""Estimated 1RM, weekly hard sets per muscle, and next-session progression for one lift.

Functions take any objects with the set attributes they read (`exercise`, `date`, `set_type`,
`weight_kg`, `reps`, `rir`, `rpe`), so they work on `coach.sessions.model.ExerciseSet` and on
simple test doubles alike.
"""

from __future__ import annotations

import re
from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from functools import cache
from pathlib import Path
from typing import Any

import yaml

from coach.safety import Pause, SafetyFlags
from coach.text import fold

MUSCLE_MAP_PATH = Path(__file__).with_name("muscle_map.yaml")

DOUBLE_PROGRESSION = 'strength-hypertrophy.md: "Double progression"'
STALLS = 'strength-hypertrophy.md: "When progress stalls"'
TARGET_RIR = 'strength-hypertrophy.md: "Target reps in reserve"'
SHORT_BREAKS = 'strength-hypertrophy.md: "Short breaks cost little"'
DELOADS = 'strength-hypertrophy.md: "Deloads"'

# convention: Epley's formula; no knowledge file names an e1RM formula. Reps in reserve are added
# to the reps done, so a set of 8 at 2 RIR counts as 10 reps to failure.
EPLEY_DIVISOR = 30
# strength-hypertrophy.md: "Weekly sets per muscle (dose-response)": move each major muscle toward
# roughly 10 or more hard weekly sets (a reference point, not a hard minimum).
WEEKLY_SETS_REFERENCE = 10
# strength-hypertrophy.md: "Target reps in reserve": warm-ups are not working sets, and a set
# ended with 5+ RIR is probably too easy for hypertrophy.
WARMUP = "warmup"
TOO_EASY_RIR = 5
# strength-hypertrophy.md: "Starting point for novices" and "Double progression": 8-12 reps. This
# is only the default: "Double progression" says to pick a range (for example 8-12), "Load range
# for maximal strength" asks for heavier main-lift work in 3-8 reps, and "Load range for
# hypertrophy" allows about 6-30 (default 6-15). `coach strength progress --rep-range` sets it
# per lift.
REP_RANGE = (8, 12)
# strength-hypertrophy.md: "Double progression": the smallest practical increment within about
# 2-10%, smaller for upper-body and isolation lifts, larger for big lower-body lifts.
# convention: 2.5% upper body and isolation, 5% big lower-body lifts, rounded to 0.5 kg.
INCREMENT_UPPER, INCREMENT_LOWER = 0.025, 0.05
LOAD_STEP_KG = 0.5
# strength-hypertrophy.md: "When progress stalls": no increase for about 3 consecutive sessions.
STALL_SESSIONS = 3
# strength-hypertrophy.md: "Short breaks cost little": under about 2 weeks off, restart at about
# 90%; after longer breaks start 10-20% below previous working loads.
# convention: a break is more than 7 days since the lift was last trained; after 2 weeks the
# coach uses 15% below, the midpoint of 10-20%.
BREAK_DAYS = 7
SHORT_BREAK_DAYS = 14
RESTART_SHORT, RESTART_LONG = 0.90, 0.85
# strength-hypertrophy.md: "Deloads": two or more of these signs persisting for 1-2 weeks; cut
# volume by about 30-50% (a coaching convention in the rule), keep loads, stop 3+ reps short of
# failure; with signs of overreaching add 1-3 rest days.
DELOAD_SIGNS = {"performance_stall", "joint_aches", "poor_sleep", "low_motivation"}
OVERREACHING_SIGNS = {"drop_despite_rest", "low_mood"}
DELOAD_MIN_SIGNS = 2
DELOAD_VOLUME_CUT = (0.3, 0.5)
DELOAD_STOP_RIR = 3
OVERREACHING_REST_DAYS = (1, 3)
# strength-hypertrophy.md: "Calibrating clients to RIR" uses the RIR-based RPE scale, on which
# RPE 10 is 0 reps in reserve: RIR = 10 - RPE.
RPE_SCALE_MAX = 10


def e1rm(weight: float, reps: int, rir: float = 0) -> float:
    if reps < 1:
        raise ValueError("e1rm needs at least 1 rep")
    if rir < 0:
        raise ValueError("reps in reserve cannot be negative")
    total = reps + rir
    if total == 1:
        return float(weight)
    return weight * (1 + total / EPLEY_DIVISOR)


def effective_rir(s: Any) -> float | None:
    if s.rir is not None:
        return s.rir
    if s.rpe is not None:
        return RPE_SCALE_MAX - s.rpe
    return None


def is_working(s: Any) -> bool:
    return s.set_type != WARMUP and s.reps is not None and s.reps > 0


def hard_set(s: Any) -> bool:
    rir = effective_rir(s)
    # convention: a working set with no RIR or RPE logged counts as hard (logs often omit it).
    return is_working(s) and (rir is None or rir < TOO_EASY_RIR)


@cache
def load_muscle_map(path: Path = MUSCLE_MAP_PATH) -> dict[str, dict]:
    return yaml.safe_load(Path(path).read_text(encoding="utf-8"))


def _base_name(exercise: str) -> str:
    return fold(re.sub(r"\s*\([^)]*\)\s*$", "", exercise))


def lookup(exercise: str, muscle_map: dict[str, dict]) -> dict | None:
    """Map entry for a logged name: case, accents and a trailing "(Equipment)" do not matter."""
    names = {fold(exercise), _base_name(exercise)}
    for key, entry in muscle_map.items():
        if fold(key) in names or names & {fold(a) for a in entry.get("aliases", [])}:
            return entry
    return None


def weekly_hard_sets(sets: list[Any], muscle_map: dict[str, dict]) -> dict[str, float]:
    """Fractional hard sets per muscle. Pass one week of sets."""
    totals: dict[str, float] = defaultdict(float)
    for s in sets:
        entry = lookup(s.exercise, muscle_map)
        if entry is None or not hard_set(s):
            continue
        for muscle, credit in entry["muscles"].items():
            if credit:
                totals[muscle] += credit
    return dict(totals)


def unmapped_exercises(sets: list[Any], muscle_map: dict[str, dict]) -> list[str]:
    return sorted({s.exercise for s in sets if lookup(s.exercise, muscle_map) is None})


@dataclass
class Suggestion:
    # no_data | no_training | paused | restart | hold | too_easy | increase_load | stalled |
    # add_reps
    action: str
    load_kg: float | None = None
    rep_range: tuple[int, int] = REP_RANGE
    reasons: list[str] = field(default_factory=list)


def _round_load(kg: float) -> float:
    return round(kg / LOAD_STEP_KG) * LOAD_STEP_KG


def _best_performance(session: list[Any]) -> float:
    """Best e1RM in a session; for bodyweight sets (no load logged), best reps to failure."""
    if all(s.weight_kg is None for s in session):
        return max(s.reps + (effective_rir(s) or 0) for s in session)
    return max(e1rm(s.weight_kg or 0.0, s.reps, effective_rir(s) or 0) for s in session)


def progression(
    history: list[Any],
    today: date | None = None,
    rep_range: tuple[int, int] = REP_RANGE,
    muscle_map: dict[str, dict] | None = None,
    flags: SafetyFlags | None = None,
    stall_after: date | None = None,
) -> Suggestion:
    """Next-session suggestion for one exercise from its logged sets.

    With `flags.no_training` nothing is prescribed. An exercise in `flags.paused_exercises` (an
    active injury) never progresses: with no professional yet it gets no load at all, otherwise
    at most its last load, or the lower restart load after a break. With
    `flags.hold_progression` the load stays where it was (a restart after a break may still
    lower it). Sessions on or before `stall_after` (the end of an injury pause) never count
    towards a stall.
    """
    if flags and flags.no_training:
        return Suggestion("no_training", None, rep_range, list(flags.reasons))
    suggestion = _progression(history, today, rep_range, muscle_map, stall_after)
    paused = flags.paused_exercises if flags else {}
    mapped = muscle_map or load_muscle_map()
    pause = find_pause(history[0].exercise, paused, mapped) if history else None
    if pause and suggestion.action != "no_data":
        if not pause.assessed:
            load = None
        elif suggestion.action == "restart":
            load = suggestion.load_kg
        else:
            load = _held_load(history)
        return Suggestion("paused", load, rep_range, list(pause.reasons))
    if flags and flags.hold_progression and suggestion.action not in ("no_data", "restart"):
        return Suggestion(
            "hold",
            _held_load(history),
            rep_range,
            ["same load and reps as last session until a clinician reviews", *flags.reasons],
        )
    return suggestion


def named_in(exercise: str, names: list[str], muscle_map: dict[str, dict] | None = None) -> bool:
    """Whether a logged name is one of `names`; case, accents and "(Equipment)" do not matter.

    With a muscle map, two names for the same mapped lift (an alias such as "press banca" for
    "Bench Press (Barbell)") also match.
    """
    wanted = {fold(n) for n in names} | {_base_name(n) for n in names}
    if {fold(exercise), _base_name(exercise)} & wanted:
        return True
    if muscle_map is None:
        return False
    entry = lookup(exercise, muscle_map)
    return entry is not None and any(lookup(n, muscle_map) is entry for n in names)


REP_RANGE_FORMAT = "EXERCISE=LOW-HIGH"
_REP_RANGE = re.compile(r"^(.*)=\s*(\d+)\s*-\s*(\d+)\s*$")


def parse_rep_range(text: str) -> tuple[str, tuple[int, int]]:
    """ "EXERCISE=LOW-HIGH" as (exercise, (low, high)). Raises ValueError on a bad range."""
    match = _REP_RANGE.match(text)
    if not match:
        raise ValueError(f"rep range {text!r} must look like {REP_RANGE_FORMAT}, e.g. squat=6-8")
    name, low, high = match.group(1).strip(), int(match.group(2)), int(match.group(3))
    if not name:
        raise ValueError(f"rep range {text!r} names no exercise ({REP_RANGE_FORMAT})")
    if low < 1:
        raise ValueError(f"rep range {text!r}: the low end must be at least 1")
    if low >= high:
        raise ValueError(f"rep range {text!r}: the low end must be lower than the high end")
    return name, (low, high)


def rep_range_for(
    exercise: str, ranges: list[tuple[str, tuple[int, int]]], default: tuple[int, int] = REP_RANGE
) -> tuple[int, int]:
    """The range given for a logged lift (the last one wins), else the rule's default."""
    matching = [rep_range for name, rep_range in ranges if named_in(exercise, [name])]
    return matching[-1] if matching else default


def find_pause(
    exercise: str, paused: dict[str, Pause], muscle_map: dict[str, dict] | None = None
) -> Pause | None:
    """The injury pause for a logged lift; several matching entries merge (unassessed wins)."""
    matches = [p for name, p in paused.items() if named_in(exercise, [name], muscle_map)]
    if not matches:
        return None
    reasons = [r for p in matches for r in p.reasons]
    return Pause(list(dict.fromkeys(reasons)), assessed=all(p.assessed for p in matches))


def pause_end(
    exercise: str, injuries: list[dict], muscle_map: dict[str, dict] | None = None
) -> date | None:
    """The latest date an injury that paused this exercise was cleared, if any."""
    ends = [
        i["cleared_on"]
        for i in injuries
        if i["status"] == "cleared" and named_in(exercise, i.get("exercises", []), muscle_map)
    ]
    return max(ends, default=None)


def _held_load(history: list[Any]) -> float | None:
    """Top working load of the last session."""
    working = [s for s in history if is_working(s)]
    last_day = max(s.date for s in working)
    loads = [s.weight_kg for s in working if s.date == last_day and s.weight_kg is not None]
    return max(loads) if loads else None


def _progression(
    history: list[Any],
    today: date | None,
    rep_range: tuple[int, int],
    muscle_map: dict[str, dict] | None,
    stall_after: date | None = None,
) -> Suggestion:
    if len({s.exercise for s in history}) > 1:
        raise ValueError("progression takes the history of one exercise")
    by_day: dict[date, list[Any]] = defaultdict(list)
    for s in history:
        if is_working(s):
            by_day[s.date].append(s)
    if not by_day:
        return Suggestion("no_data", rep_range=rep_range)
    days = sorted(by_day)
    sessions = [by_day[d] for d in days]
    last = sessions[-1]
    loads = [s.weight_kg for s in last if s.weight_kg is not None]
    top_load = max(loads) if loads else None
    bodyweight = top_load is None
    today = today or date.today()

    gap = (today - days[-1]).days
    if gap > BREAK_DAYS:
        factor = RESTART_SHORT if gap < SHORT_BREAK_DAYS else RESTART_LONG
        return Suggestion(
            "restart",
            None if bodyweight else _round_load(top_load * factor),
            rep_range,
            [f"{SHORT_BREAKS}: {gap} days off, restart at {factor:.0%} of the last working load"],
        )

    entry = lookup(history[0].exercise, muscle_map or load_muscle_map()) or {}
    step = INCREMENT_LOWER if entry.get("lower_body") else INCREMENT_UPPER
    if bodyweight:
        heavier = None
    else:
        # Never round a jump back to the same load (small loads): at least one 0.5 kg step.
        heavier = max(_round_load(top_load * (1 + step)), top_load + LOAD_STEP_KG)
    rirs = [effective_rir(s) for s in last]
    if all(r is not None and r >= TOO_EASY_RIR for r in rirs):
        return Suggestion("too_easy", heavier, rep_range, [f"{TARGET_RIR}: sets ended with 5+ RIR"])
    if all(s.reps > rep_range[1] for s in last):
        how = (
            "add load (a belt or vest) or move to a harder variation"
            if bodyweight
            else f"add {step:.1%} or the smallest practical jump"
        )
        return Suggestion(
            "increase_load",
            heavier,
            rep_range,
            [f"{DOUBLE_PROGRESSION}: every work set beat {rep_range[1]} reps, {how}"],
        )
    # Sessions inside a finished injury pause were held on purpose, so they are not a stall.
    countable = [by_day[d] for d in days if stall_after is None or d > stall_after]
    if len(countable) > STALL_SESSIONS:
        before = _best_performance(countable[-STALL_SESSIONS - 1])
        if max(_best_performance(s) for s in countable[-STALL_SESSIONS:]) <= before:
            return Suggestion(
                "stalled",
                top_load,
                rep_range,
                [
                    f"{STALLS}: no gain in load or reps for {STALL_SESSIONS} sessions; check "
                    "effort and weekly sets (10+), then add 10-20% more sets for this muscle"
                ],
            )
    return Suggestion(
        "add_reps",
        top_load,
        rep_range,
        [f"{DOUBLE_PROGRESSION}: same load, add reps until every set beats {rep_range[1]}"],
    )


@dataclass
class Deload:
    volume_cut: tuple[float, float]
    stop_rir: int
    extra_rest_days: tuple[int, int]
    reasons: list[str]


def deload(signs: set[str]) -> Deload | None:
    unknown = signs - DELOAD_SIGNS - OVERREACHING_SIGNS
    if unknown:
        raise ValueError(f"unknown deload signs: {', '.join(sorted(unknown))}")
    core = signs & DELOAD_SIGNS
    if "drop_despite_rest" in signs:
        core = core | {"performance_stall"}
    overreaching = "drop_despite_rest" in signs and bool(signs & {"poor_sleep", "low_mood"})
    if len(core) < DELOAD_MIN_SIGNS and not overreaching:
        return None
    return Deload(
        volume_cut=DELOAD_VOLUME_CUT,
        stop_rir=DELOAD_STOP_RIR,
        extra_rest_days=OVERREACHING_REST_DAYS if overreaching else (0, 0),
        reasons=[f"{DELOADS}: {len(core)} signs together; one lighter week, keep the loads"],
    )
