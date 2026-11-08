"""Command line for the coach skills: every number a skill quotes comes from here.

    uv run python -m coach [--data-dir DIR] [--today YYYY-MM-DD] <command> ... [--json]

Commands print JSON (indented unless --json asks for one compact line). A missing profile field
exits with code 2 and {"error": "profile_incomplete", "field": "<name>"} so the skill can ask
for it; invalid input exits 2 with {"error": "invalid", "message": ...}.
"""

from __future__ import annotations

import argparse
import dataclasses
import hashlib
import json
import math
import os
import re
import sys
import types
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from statistics import fmean, median
from typing import Any, NoReturn

import yaml

from coach import (
    catalogue,
    energy,
    export,
    foods,
    knowledge,
    macros,
    mealplan,
    off,
    recipes,
    regions,
    runs,
    safety,
    strength,
    tastes,
    trend,
    zones,
)
from coach.checkins import Checkin, append_checkin, read_checkins, weigh_ins, weight_jump
from coach.profile import (
    BP_MEDICATION,
    CLEARANCE_ANSWERS,
    CONDITION_TOKENS,
    GOALS,
    HEART_DISEASE,
    MEDICATION_TOKENS,
    NO_NUMBER,
    PARQ_ANSWERS,
    SCREENING_KEYS,
    Profile,
    ProfileIncomplete,
    load_profile,
    save_profile,
)
from coach.regioncode import NO_REGION, real_region
from coach.sessions.importers import base as importers  # the package registers importers
from coach.sessions.model import ExerciseSet
from coach.sessions.store import append, read_sets
from coach.text import fold, fold_words

# convention: generic-name endings of common blood-pressure medicines (ACE inhibitors -pril, ARBs
# -sartan, dihydropyridine calcium channel blockers -dipine), the classes cardio-health.md "Blood
# pressure medicines and exercise" names; a hit only suggests the bp_medication token.
BP_DRUG_ENDINGS = ("pril", "sartan", "dipine")
# convention: 2 decimals in CLI output, so skills can quote numbers verbatim to a client.
OUTPUT_DECIMALS = 2
# convention: `strength progress` with no exercise covers lifts trained in the last 4 weeks.
PROGRESS_LOOKBACK_DAYS = 28
# convention: /menu accepts a day up to 5% over the calorie target, never under it.
MENU_KCAL_MARGIN = 0.05
DEFAULT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def _jsonable(value: Any) -> Any:
    if dataclasses.is_dataclass(value):
        return _jsonable(dataclasses.asdict(value))
    if isinstance(value, dict):
        return {k: _jsonable(v) for k, v in value.items()}
    if isinstance(value, list | tuple):
        return [_jsonable(v) for v in value]
    if isinstance(value, date):
        return value.isoformat()
    if isinstance(value, float):
        return round(value, OUTPUT_DECIMALS)
    return value


def cmd_energy(profile: Profile, args: argparse.Namespace) -> dict:
    flags = safety.flags(profile, args.today)
    rmr = energy.rmr_mifflin(profile, args.today)
    estimated = energy.tdee(profile, args.pal, args.today, flags.no_training)
    target = energy.calorie_target(
        profile,
        flags,
        goal=args.goal,
        today=args.today,
        tdee_kcal=args.tdee if args.tdee is not None else estimated,
        current_kcal=args.current_kcal,
        recalibrated=args.tdee is not None,
        estimate_chosen=args.pal is not None or args.tdee is not None,
    )
    return {
        "rmr": rmr,
        "rmr_range": energy.rmr_range(profile, args.today),
        "tdee": estimated,
        "tdee_range": energy.tdee_range(profile, args.today, flags.no_training, args.pal),
        "target": target,
    }


def cmd_macros(profile: Profile, args: argparse.Namespace) -> dict:
    notes = []
    if args.kcal is None:
        target = cmd_energy(profile, args)["target"]
        kcal, in_deficit = target.kcal, target.deficit > 0
    else:
        # A stored target from before a flag fired (or before a birthday) must not keep a deficit
        # or a surplus that the safety rules now forbid.
        kcal, in_deficit = args.kcal, args.in_deficit
        flags = safety.flags(profile, args.today)
        allowed = cmd_energy(profile, args)["target"].kcal
        if kcal < allowed and energy.deficit_blockers(profile, flags, args.today):
            kcal, in_deficit = allowed, False
            notes.append(f"raised to {allowed:,} kcal: the safety rules forbid a deficit")
        elif kcal > allowed and energy.surplus_blocked(flags):
            kcal = allowed
            notes.append(f"lowered to {allowed:,} kcal: the safety rules forbid a surplus")
    result = macros.macro_targets(profile, kcal, in_deficit=in_deficit, today=args.today)
    result.notes += notes
    return {"in_deficit": in_deficit} | dataclasses.asdict(result)


def cmd_trend(profile: Profile, args: argparse.Namespace) -> dict:
    today = args.today or date.today()
    checkins = [c for c in read_checkins(args.data_dir / "checkins.csv") if c.date <= today]
    result = trend.weight_trend(weigh_ins(checkins), safety.flags(profile, args.today))
    recalibrated = None
    if result.status == "ok" and result.can_recalibrate:
        intakes = [
            c.intake_kcal
            for c in checkins
            if c.intake_kcal is not None and result.start <= c.date <= result.end
        ]
        if intakes:
            recalibrated = trend.recalibrate_tdee(result, fmean(intakes), args.energy_density)
    return dataclasses.asdict(result) | {"recalibrated_tdee": recalibrated}


def _heart_rates(profile: Profile, args: argparse.Namespace) -> tuple[int | None, int | None]:
    """(resting, max): the --hr-rest/--hr-max flags, else the profile's stored values."""
    rest = getattr(args, "hr_rest", None)
    peak = getattr(args, "hr_max", None)
    return (
        profile.hr_rest if rest is None else rest,
        profile.hr_max if peak is None else peak,
    )


def cmd_zones(profile: Profile, args: argparse.Namespace) -> zones.Zones:
    hr_rest, hr_max = _heart_rates(profile, args)
    return zones.hr_zones(profile, safety.flags(profile, args.today), hr_rest, hr_max, args.today)


def cmd_safety(profile: Profile, args: argparse.Namespace) -> safety.SafetyFlags:
    return safety.flags(profile, args.today)


def cmd_strength(profile: Profile, args: argparse.Namespace) -> dict:
    if args.strength_cmd == "e1rm":
        return {"e1rm": strength.e1rm(args.weight, args.reps, args.rir)}
    if args.strength_cmd == "deload":
        signs = {s.strip() for s in args.signs.split(",") if s.strip()}
        return {"deload": strength.deload(signs)}
    if args.strength_cmd == "alias":
        return _strength_alias(args)
    if args.strength_cmd == "plan-sets":
        return _plan_sets(args.data_dir / args.file, args.data_dir)
    today = args.today or date.today()
    logged = [s for s in read_sets(args.data_dir / "sessions.csv") if s.date <= today]
    muscle_map = strength.muscle_map_for(args.data_dir)
    if args.strength_cmd == "sets":
        # Default: the 7 days ending on the last logged session, the latest week with data.
        end = args.week_ending or max((s.date for s in logged), default=today)
        start = end - timedelta(days=6)
        week = [s for s in logged if start <= s.date <= end]
        return {
            "week": {"start": start, "end": end},
            "sets": strength.weekly_hard_sets(week, muscle_map),
            "unmapped": strength.unmapped_exercises(week, muscle_map),
            "reference_sets_per_week": strength.WEEKLY_SETS_REFERENCE,
        }
    if args.exercise:
        wanted = args.exercise.strip().lower()
        names = sorted({s.exercise for s in logged if s.exercise.lower() == wanted})
    else:
        recent = today - timedelta(days=PROGRESS_LOOKBACK_DAYS)
        names = sorted({s.exercise for s in logged if s.date > recent})
    flags = safety.flags(profile, args.today)
    ranges = [strength.parse_rep_range(text) for text in args.rep_range]
    lifts = {
        name: strength.progression(
            [s for s in logged if s.exercise == name],
            today=today,
            rep_range=strength.rep_range_for(name, ranges, muscle_map=muscle_map),
            muscle_map=muscle_map,
            flags=flags,
            stall_after=strength.pause_end(name, profile.injuries, muscle_map),
        )
        for name in names
    }
    # `*` gives a range to every lift, so none of them is on the default.
    star = any(n == strength.STAR for n, _ in ranges)
    recent_cutoff = today - timedelta(days=PROGRESS_LOOKBACK_DAYS)
    given = {
        name: star or any(strength.rep_range_matches(name, n, muscle_map) for n, _ in ranges)
        for name in names
    }
    notes = {}
    for name in names:
        reps = [
            s.reps
            for s in logged
            if s.exercise == name and strength.hard_set(s) and s.date > recent_cutoff
        ]
        if not given[name] and reps:
            mid = median(reps)
            low, high = strength.REP_RANGE
            if not low <= mid <= high:
                notes[name] = (
                    f"logged reps (median {mid:g}) are outside the default {low}-{high}: ask "
                    "the client's usual range and pass it with --rep-range"
                )
    # Every logged lift, not just the ones shown: --exercise and the lookback only filter output.
    every = {s.exercise for s in logged}
    unmatched = strength.unmatched_rep_ranges(ranges, every, muscle_map)
    # Names that match only lifts last logged before the lookback window. --exercise bypasses
    # the window, so there is nothing outside it to report.
    outside = [] if args.exercise else strength.unmatched_rep_ranges(ranges, set(names), muscle_map)
    return {
        "lifts": lifts,
        "rep_range_source": {n: "given" if given[n] else "default" for n in names},
        "rep_range_notes": notes,
        "unmatched_rep_ranges": unmatched,
        "rep_ranges_outside_lookback": [n for n in outside if n not in unmatched],
    }


def _plan_sets(path: Path, data_dir: Path) -> dict:
    """Weekly hard sets per muscle for a planned week (each listed session happens once)."""
    try:
        plan = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as err:
        raise ValueError(f"{path} is not valid YAML: {err}") from err
    sessions = plan.get("sessions") if isinstance(plan, dict) else None
    if not isinstance(sessions, list) or not all(isinstance(x, dict) for x in sessions):
        raise ValueError("the plan needs `sessions:`, a list of {name, exercises}")
    planned = []
    for session in sessions:
        exercises = session.get("exercises") or []
        if not isinstance(exercises, list):
            raise ValueError(f"`exercises:` must be a list, not {exercises!r}")
        for item in exercises:
            sets = item.get("sets") if isinstance(item, dict) else None
            if (
                not isinstance(sets, int)
                or isinstance(sets, bool)
                or sets < 1
                or not item.get("exercise")
            ):
                raise ValueError(
                    f"each planned exercise needs `exercise` and whole `sets`: {item!r}"
                )
            planned += [
                types.SimpleNamespace(
                    exercise=str(item["exercise"]), set_type="normal", reps=1, rir=None, rpe=None
                )
            ] * sets
    if not planned:
        raise ValueError("the plan lists no sessions with exercises")
    muscle_map = strength.muscle_map_for(data_dir)
    totals = strength.weekly_hard_sets(planned, muscle_map)
    return {
        "sets": totals,
        # Every muscle the map credits, so one the plan never trains is listed too.
        "below_reference": sorted(
            m
            for m in {m for entry in muscle_map.values() for m in entry["muscles"]}
            if totals.get(m, 0) < strength.WEEKLY_SETS_REFERENCE
        ),
        "unmapped": strength.unmapped_exercises(planned, muscle_map),
        "reference_sets_per_week": strength.WEEKLY_SETS_REFERENCE,
    }


def _leftover_warning(leftovers: list[ExerciseSet]) -> str:
    counts = Counter((s.exercise, s.date.isoformat()) for s in leftovers)
    which = ", ".join(f"{name} {day} x{n}" for (name, day), n in sorted(counts.items()))
    return (
        f"{len(leftovers)} sets with no reps, weight, duration or distance (template leftovers) "
        f"were not stored: {which}"
    )


def _import_runs(importer: importers.Importer, args: argparse.Namespace) -> dict:
    """A run importer (`target = "runs"`): its runs go to data/runs.csv."""
    read = importer.read(args.path)
    today = args.today or date.today()
    kept = [r for r in read if r.date <= today]
    result = runs.append_runs(kept, args.data_dir / "runs.csv")
    days = sorted(r.date for r in kept)
    future = len(read) - len(kept)
    return {
        "importer": importer.name,
        "store": "runs.csv",
        "read": len(read),
        "added": result.added,
        "duplicates": result.duplicates,
        "skipped_future": future,
        "first_day": days[0] if days else None,
        "last_day": days[-1] if days else None,
        "warnings": [f"{future} runs dated after today ({today}) were not stored"]
        if future
        else [],
    }


def _strength_alias(args: argparse.Namespace) -> dict:
    aliases = strength.personal_aliases(args.data_dir)
    if args.alias_cmd == "add":
        muscle_map = strength.load_muscle_map()
        entry = strength.lookup(args.exercise, muscle_map)
        if entry is None:
            raise ValueError(
                f"{args.exercise!r} is not in the muscle map: give a lift it knows, e.g. "
                + ", ".join(list(muscle_map)[:6])
            )
        name = args.name.strip()
        if not name:
            raise ValueError("give the name as the client logs it")
        key = next(k for k, v in muscle_map.items() if v is entry)
        # A name the map already gives to another lift keeps that lift: the alias would be dead
        # (that lift comes first in the map) or take every set logged under it (it comes later).
        rest = strength.with_aliases({k: v for k, v in aliases.items() if k != name})
        other = next(
            (
                k
                for k, e in rest.items()
                if k != key and fold(name) in {fold(n) for n in (k, *e.get("aliases", []))}
            ),
            None,
        )
        if other is not None:
            raise ValueError(f"{name!r} already names {other!r} in the muscle map")
        aliases[name] = key
        path = args.data_dir / strength.PERSONAL_ALIASES
        path.write_text(yaml.safe_dump(aliases, allow_unicode=True), encoding="utf-8")
    return {"aliases": aliases}


def cmd_import(profile: Profile, args: argparse.Namespace) -> dict:
    importer = importers.get(args.importer) if args.importer else importers.detect(args.path)
    if getattr(importer, "target", "sessions") == "runs":
        return _import_runs(importer, args)
    read = importer.read(args.path)
    # Empty rows are what an app leaves when a routine template's sets are never filled in. They
    # carry nothing any calculator reads (no reps, so not a working set), so storing them would
    # only inflate `added`; they are skipped and reported instead.
    leftovers = [s for s in read if s.is_empty]
    today = args.today or date.today()
    future = [s for s in read if not s.is_empty and s.date > today]
    sets = [s for s in read if not s.is_empty and s.date <= today]
    store = args.data_dir / "sessions.csv"
    muscle_map = strength.muscle_map_for(args.data_dir)  # before storing: a bad file stops here
    # The same workout imported through two importers is stored twice (the key includes the
    # source) and would double-count weekly sets, so say so.
    other_starts = {s.start_time for s in read_sets(store) if s.source != importer.name}
    clashes = sorted({s.start_time for s in sets} & other_starts)
    result = append(sets, store)
    days = sorted({s.date for s in sets})
    warnings = [
        f"{start.isoformat()} is already logged from another source; it may now be counted twice"
        for start in clashes
    ]
    if leftovers:
        warnings.append(_leftover_warning(leftovers))
    if future:
        warnings.append(f"{len(future)} sets dated after today ({today}) were not stored")
    if result.conflicts:
        warnings.append(
            f"{result.conflicts} sets match stored ones but differ in load or reps (an edited "
            "or re-exported log, or another unit): kept the stored rows"
        )
    return {
        "importer": importer.name,
        "read": len(read),
        "added": result.added,
        "duplicates": result.duplicates,
        "conflicts": result.conflicts,
        "skipped_future": len(future),
        "skipped_empty": len(leftovers),
        # Names the muscle map does not know: their sets count towards no muscle until mapped.
        "unmapped": strength.unmapped_exercises(sets, muscle_map),
        "first_day": days[0] if days else None,
        "last_day": days[-1] if days else None,
        "warnings": warnings,
    }


def cmd_runs(profile: Profile, args: argparse.Namespace) -> dict:
    path = args.data_dir / "runs.csv"
    today = args.today or date.today()
    logged = [r for r in runs.read_runs(path) if r.date <= today]
    if args.runs_cmd == "taper":
        flags = safety.flags(profile, args.today)
        if flags.no_training:
            stops = safety.stop_reasons(flags)
            raise ValueError("no taper while training is on hold: " + "; ".join(stops))
        if safety.running_unassessed(profile):
            paused = safety.running_paused(profile)
            raise ValueError("no taper while running is paused: " + "; ".join(paused))
        return runs.taper(args.race_date, today, logged)
    if args.runs_cmd == "add":
        when = args.date or today
        if when > today:
            raise ValueError(f"{when} is after today ({today}); log a run on the day or after it")
        run = runs.Run(
            when, args.km, args.minutes, args.avg_hr, args.max_hr, args.rpe, args.notes.strip()
        )
        result = runs.append_runs([run], path)
        return {
            "run": run,
            "added": result.added,
            "duplicates": result.duplicates,
            "paused": safety.running_paused(profile),
            "warnings": ["the same run (date, km, minutes) is already stored; not added again"]
            if result.duplicates
            else [],
        }
    # Default: the 7 days ending on the last logged run, the latest week with data.
    end = args.week_ending or max((r.date for r in logged), default=today)
    flags = safety.flags(profile, args.today)
    hr_rest, hr_max = _heart_rates(profile, args)
    shown = zones.hr_zones(profile, flags, hr_rest, hr_max, args.today)
    every = runs.zones_to_describe(profile, flags, hr_rest, hr_max, args.today)
    paused = safety.running_paused(profile)
    # Unassessed: no next run at all. Managed by a professional: no progression, the cap stays
    # at the longest run and the professional's limits decide the rest (as for a paused lift).
    hold = flags.hold_progression or bool(paused)
    week = runs.week(logged, end, shown, every, today, hold, safety.running_unassessed(profile))
    return week | {"paused": paused}


def menu_check(totals: dict, targets: dict, share: float = 1.0) -> dict:
    """'ok', 'under' or 'over' per target: kcal within [target, target + MENU_KCAL_MARGIN], protein
    at least the low end of its range, fibre at least its target, fat at least its minimum.
    Carbohydrate fills the rest.

    'missing' when an item lacks the value: always for kcal; for a floor only while the known
    total is below it (the true total can only be higher).

    With a free meal in the day (`share` below 1, see `mealplan.Day.share`) the planned meals
    must reach `share` of every target and kcal may not pass the full target: the free meal adds
    to what is planned, so there is no margin."""
    missing = totals.get("missing") or {}
    kcal = totals["kcal"]
    kcal_max = targets["kcal"] * (1 + MENU_KCAL_MARGIN) if share == 1 else targets["kcal"]
    if "kcal" in missing:
        kcal_status = "missing"
    elif kcal < targets["kcal"] * share:
        kcal_status = "under"
    elif kcal > kcal_max:
        kcal_status = "over"
    else:
        kcal_status = "ok"
    # Protein passes from the low end of the rule's range (macros `protein_min_g`) up to its top
    # (`protein_max_g`, the same rule's range); a free meal only adds, so the full top applies.
    protein = "protein_min_g" if "protein_min_g" in targets else "protein_g"
    floors = {"protein_g": protein, "fat_g": "fat_min_g", "fibre_g": "fibre_g"}
    status = {"kcal": kcal_status} | {
        key: "ok"
        if totals[key] >= targets[target] * share
        else "missing"
        if key in missing
        else "under"
        for key, target in floors.items()
    }
    if "protein_max_g" in targets and totals["protein_g"] > targets["protein_max_g"]:
        status["protein_g"] = "over"
    return status


# nutrition.md: "Dietary fibre": at least 400 g/day of vegetables and fruit.
VEG_FRUIT_MIN_G = 400
VEG_FRUIT_NOTE = (
    "veg_fruit_g counts vegetables and fruit from the food tables only: products count 0, and "
    "potatoes and other starchy roots are left out (a convention)"
)


def _menu_day(totals: foods.MenuTotals, targets: dict, share: float = 1.0) -> dict:
    check = menu_check(dataclasses.asdict(totals), targets, share)
    warnings = []
    floor = VEG_FRUIT_MIN_G * share  # a free meal carries its share, as in menu_check
    if totals.veg_fruit_g < floor:
        # With a free meal the planned meals carry their share of the day's 400 g.
        of_day = f" of the {VEG_FRUIT_MIN_G} g a day" if share < 1 else " a day"
        warnings.append(
            f"{round(totals.veg_fruit_g, OUTPUT_DECIMALS):g} g of vegetables and fruit, under the "
            f'{round(floor, OUTPUT_DECIMALS):g} g{of_day} of nutrition.md "Dietary fibre" for '
            "the planned meals"
        )
    return {
        "totals": totals,
        "targets": targets,
        "check": check,
        # Protein over the rule's top is a warning, not a fail: the range is a target, not a limit.
        "ok": not totals.unknown
        and all(v == "ok" or (k, v) == ("protein_g", "over") for k, v in check.items()),
        "warnings": warnings,
        "veg_fruit_note": VEG_FRUIT_NOTE,
    }


def _free_meal(day: mealplan.Day, totals: foods.MenuTotals, targets: dict) -> dict:
    """What the free meal has left to reach the day's targets (never below 0): the targets minus
    the planned meals, using the values the planned items have."""
    left = {
        "kcal": targets["kcal"] - totals.kcal,
        "protein_g": targets.get("protein_min_g", targets["protein_g"]) - totals.protein_g,
        "fat_g": targets["fat_min_g"] - totals.fat_g,
        "fibre_g": targets["fibre_g"] - totals.fibre_g,
    }
    return {
        "meals": day.free_meals,
        "planned_meals": len(day.meals) - len(day.free_meals),
        "share": day.share,
        "budget": {key: max(round(value, 2), 0) for key, value in left.items()},
        "note": "kcal still to reach the target, and protein, fat (minimum) and fibre still to "
        "reach theirs; the day passes only when the planned meals carry their share of each "
        "target (see check)",
    }


def _region_for(profile: Profile, args: argparse.Namespace) -> str | None:
    """`--region` over the profile's; an empty `--region` is an error, as in `profile set`."""
    given = getattr(args, "region", None)
    if given is not None and not given.strip():
        raise ValueError("--region needs a value: a region code, or none for no region")
    return given or profile.region


def _menu_table(profile: Profile, args: argparse.Namespace) -> list[foods.Food]:
    return regions.menu_table(_region_for(profile, args), data_dir=args.data_dir)


def cmd_menu(profile: Profile, args: argparse.Namespace) -> foods.MenuTotals | dict:
    items = [foods.parse_item(item) for item in args.item]
    totals = foods.menu_totals(items, _menu_table(profile, args))
    if not args.targets:
        return totals
    return _menu_day(totals, cmd_macros(profile, args))


def _in_data_dir(args: argparse.Namespace, path: Path) -> Path:
    """A relative path names a file in the data dir."""
    return path if path.is_absolute() else args.data_dir / path


def _shown(args: argparse.Namespace, path: Path) -> str:
    """The path as the JSON output shows it: relative to the data dir when inside it."""
    return (
        path.relative_to(args.data_dir).as_posix()
        if path.is_relative_to(args.data_dir)
        else str(path)
    )


def _meals(day: mealplan.Day) -> list[dict]:
    return [
        {"meal": m.name, "tupper": m.tupper, "free": m.free, "dishes": [d.name for d in m.dishes]}
        for m in day.meals
    ]


def cmd_mealplan(profile: Profile, args: argparse.Namespace) -> dict:
    if args.mealplan_cmd == "list":
        return {
            "menus": [
                {
                    "file": path.relative_to(args.data_dir).as_posix(),
                    "start": date.fromisoformat(path.stem),
                    "days": len(mealplan.load_draft(path)[1]),
                }
                for path in mealplan.saved(args.data_dir)
            ]
        }
    if args.mealplan_cmd == "export":
        return _export_menu(profile, args)
    document, days = mealplan.load_draft(_in_data_dir(args, args.file))
    if any(day.free_meals for day in days) and safety.eating_disorder_positive(profile):
        raise ValueError(
            f"{mealplan.FREE_MEAL_RULE}: no free meal after a positive eating-disorder "
            "screen; plan every meal and suggest a GP or eating-disorder professional"
        )
    table = _menu_table(profile, args)
    targets = cmd_macros(profile, args)
    client_tastes = tastes.load_tastes(args.data_dir / "tastes.yaml")
    taste_flags = mealplan.taste_flags(days, client_tastes, table)
    blocking = [f for f in taste_flags if f["blocking"]]
    cooking_minutes = client_tastes.cooking_minutes
    today = args.today or date.today()
    checked = []
    timed: set[str] = set()  # a batch is cooked once: its time is checked on its first day
    for day in days:
        totals = foods.menu_totals(day.items, table)
        checked.append(_menu_day(totals, targets, day.share))
        if day.free_meals:
            checked[-1]["free_meal"] = _free_meal(day, totals, targets)
        if day.date < today:
            checked[-1]["warnings"].append(f"dated before today ({today})")
        for dish in (d for m in day.meals for d in m.dishes if not d.eat_out):
            if fold(dish.name) in timed:
                continue
            timed.add(fold(dish.name))
            if cooking_minutes and dish.minutes and dish.minutes > cooking_minutes:
                checked[-1]["warnings"].append(
                    f"{dish.name} takes {dish.minutes} min, over the client's cooking_minutes "
                    f"({cooking_minutes})"
                )
    repeats = mealplan.repeats(days)
    ok = not repeats and not blocking and all(c["ok"] for c in checked)
    result = {
        "ok": ok,
        "repeats": repeats,
        "taste_flags": taste_flags,
        "warnings": [
            f"{d.date}: {w}" for d, c in zip(days, checked, strict=True) for w in c["warnings"]
        ],
        "veg_fruit_note": VEG_FRUIT_NOTE,
        "targets": targets,
        "days": [
            {"date": day.date, "dishes": day.dishes, "meals": _meals(day)}
            | {k: c[k] for k in ("totals", "check", "ok", "free_meal", "warnings") if k in c}
            | {"taste_flags": [f for f in taste_flags if f["date"] == day.date]}
            for day, c in zip(days, checked, strict=True)
        ],
    }
    if args.mealplan_cmd == "check":
        return result
    if not ok:
        failing = [str(d.date) for d, c in zip(days, checked, strict=True) if not c["ok"]]
        reasons = [f"days not ok: {', '.join(failing)}"] if failing else []
        reasons += [f"{r['dish']} repeats on {', '.join(map(str, r['dates']))}" for r in repeats]
        reasons += [
            f"{f['kind']} {f['entry']!r} matches {f['text']!r} in {f['dish']!r} ({f['date']})"
            for f in blocking
        ]
        raise ValueError("not saved; " + "; ".join(reasons))
    for entry, c, day in zip(document["days"], checked, days, strict=True):
        entry.update(_jsonable({k: c[k] for k in ("totals", "check", "ok", "free_meal") if k in c}))
        flags = [f for f in taste_flags if f["date"] == day.date]
        if flags:
            entry["taste_flags"] = _jsonable(flags)
    document = {"saved_on": args.today or date.today(), "targets": _jsonable(targets)} | document
    return result | {"saved": mealplan.save(document, args.data_dir, args.replace)}


def _saved_menu(args: argparse.Namespace) -> Path:
    """The menu named on the command line, or the newest saved one."""
    if args.menu is not None:
        return _in_data_dir(args, args.menu)
    menus = mealplan.saved(args.data_dir)
    if not menus:
        raise ValueError("no saved menu yet: save one with `coach mealplan save`")
    return menus[-1]


def _export_menu(profile: Profile, args: argparse.Namespace) -> dict:
    path = _saved_menu(args)
    document, days = mealplan.load_draft(path)
    table = _menu_table(profile, args)
    pantry = tastes.load_tastes(args.data_dir / "tastes.yaml").pantry or []
    listed = mealplan.shopping(days, table, profile.language, pantry)
    out = _in_data_dir(args, args.out) if args.out else path.with_suffix(".pdf")
    export.write(out, document, days, table, listed, profile.language, qr=not args.no_qr)
    return {
        "pdf": _shown(args, out),
        "menu": _shown(args, path),
        "days": len(days),
        "qr": not args.no_qr,
    }


def cmd_shopping(profile: Profile, args: argparse.Namespace) -> dict:
    path = _saved_menu(args)
    _, days = mealplan.load_draft(path)
    pantry = tastes.load_tastes(args.data_dir / "tastes.yaml").pantry or []
    listed = mealplan.shopping(days, _menu_table(profile, args), profile.language, pantry)
    return {
        "menu": _shown(args, path),
        "days": len(days),
        **listed,
        "note": "amounts are for the form each name gives (raw, cooked, drained); a batch is "
        "bought once at its servings, `left_over` of them are for other days or the freezer; "
        "`units` is about how many of `unit_name` (the source's portion size) the grams make, in "
        "whole units rounded up",
    }


PROFILE_REQUIRED = [
    "sex",
    "birth_date",
    "height_cm",
    "weight_kg",
    "goal",
    "experience",
    "activity_level",
    "language",
    "region",
    "emergency_number",
]
_PROFILE_TYPES = {
    "birth_date": date.fromisoformat,
    "height_cm": float,
    "weight_kg": float,
    "pal_override": float,
    "research_reminder_months": int,
    "hr_max": int,
    "hr_rest": int,
}


# convention: input parsing, not coaching: a medications or conditions answer meaning "none"
# (es and en) is stored as an empty list.
NONE_WORDS = ("none", "no", "nothing", "ninguno", "ninguna", "nada")


def _missing(profile: Profile, name: str) -> bool:
    if name == "emergency_number":  # the region's number counts (coach safety prints it)
        return profile.emergency_number is None and regions.emergency_number(profile.region) is None
    return getattr(profile, name) is None


def _list_answer(raw: str) -> list[str]:
    items = [item.strip() for item in raw.split(",") if item.strip()]
    return [] if len(items) == 1 and fold(items[0]) in NONE_WORDS else items


def _parse_profile_value(field: str, raw: str) -> Any:
    if field.startswith("screening."):
        key = field.removeprefix("screening.")
        if key not in SCREENING_KEYS:
            raise ValueError(f"unknown screening key {key!r}: {', '.join(SCREENING_KEYS)}")
        if raw.lower() == "none":
            return None  # clears the answer, e.g. an outdated BP reading
        kind = SCREENING_KEYS[key]
        if kind is bool:
            if raw.lower() not in ("true", "false"):
                raise ValueError(f"{field} must be true or false, not {raw!r}")
            return raw.lower() == "true"
        if kind is list:
            # "none" clears the answer (above); "no" and the other none-words are the answer none.
            return _list_answer(raw)
        if kind is int:
            if not raw.isdigit():
                raise ValueError(f"{field} must be a whole number, not {raw!r}")
            return int(raw)
        return raw
    if field in ("pal_override", "hr_max", "hr_rest", "sport") and raw.lower() == "none":
        return None
    if field == "injuries":
        raise ValueError("injuries are set with `coach injury add` and `coach injury clear`")
    if field == "emergency_number" and raw.strip().lower() == NO_NUMBER:
        return NO_NUMBER  # declined or not available: counts as set, safety prints none
    if field == "region":
        if not raw.strip():
            raise ValueError("region needs a value: a region code, or none for no region")
        code = real_region(raw)
        if code is None:
            return NO_REGION  # chosen: no region for this country, the base food table only
        raw = code
        if not (regions.ROOT / "regions" / raw / "region.yaml").exists():
            raise ValueError(
                f"there is no region {raw!r} yet (no regions/{raw}/region.yaml): set the region "
                "to none, which uses the base food table, or add one as docs/adding-a-region.md "
                "says"
            )
    if field in ("medications", "conditions"):
        return _list_answer(raw)
    if field in CONDITION_TOKENS:
        raise ValueError(
            f"{field!r} is not a profile field: store it as a condition, e.g. "
            f"`coach profile set conditions {field}` (give every condition, comma-separated)"
        )
    if field not in Profile.__dataclass_fields__:
        raise ValueError(f"unknown profile field {field!r}")
    try:
        return _PROFILE_TYPES.get(field, str)(raw)
    except ValueError:
        raise ValueError(f"{field}: {raw!r} is not valid") from None


def _pal_override_warnings(profile: Profile, args: argparse.Namespace) -> list[str]:
    if profile.pal_override is None:
        return []
    if profile.activity_level != "active":
        return ["pal_override has no effect: it applies only to the 'active' activity level"]
    if not safety.flags(profile, args.today).no_training:
        return ["pal_override is inactive until a training hold applies"]
    return []


def cmd_profile(profile: Profile, args: argparse.Namespace) -> dict:
    if args.profile_cmd == "set":
        value = _parse_profile_value(args.field, args.value)
        if args.field.startswith("screening."):
            key = args.field.removeprefix("screening.")
            old = profile.screening.pop(key, None)
            if value is not None:
                profile.screening[key] = value
            if key in PARQ_ANSWERS and value != old:
                # A vigorous-work review covered the old answers, not the new ones.
                profile.screening.pop("vigorous_reviewed", None)
            if key in CLEARANCE_ANSWERS and value != old:
                # A medical clearance covered the old diagnoses and symptoms, not the new ones.
                profile.screening.pop("medically_cleared", None)
        else:
            setattr(profile, args.field, value)
        save_profile(profile, args.data_dir / "profile.yaml")  # validates enums and screening
    warnings = (
        _pal_override_warnings(profile, args)
        if getattr(args, "field", None) == "pal_override"
        else []
    )
    disease = profile.screening.get("known_disease")
    if (
        profile.has_condition(HEART_DISEASE)
        and disease is not None
        and "cardiovascular" not in disease
    ):
        warnings.append(
            "conditions lists heart_disease but screening.known_disease has no cardiovascular: "
            "if a doctor diagnosed it, add cardiovascular"
        )
    return ({"warnings": warnings} if warnings else {}) | {
        "data_dir": str(args.data_dir.resolve()),  # skills read and write files here by path
        "profile": profile,
        "missing": [f for f in PROFILE_REQUIRED if _missing(profile, f)],
        "unrecognised": {
            "medications": [m for m in profile.medications if m not in MEDICATION_TOKENS],
            "conditions": [c for c in profile.conditions if c not in CONDITION_TOKENS],
        },
        "unrecognised_note": "recorded as given; no calculation depends on these items",
        "suggested_tokens": {
            m: BP_MEDICATION for m in profile.medications if fold(m).endswith(BP_DRUG_ENDINGS)
        }
        if not profile.has_medication(BP_MEDICATION)
        else {},
    }


def _find_injury(profile: Profile, area: str) -> dict | None:
    return next((i for i in profile.injuries if fold(i["area"]) == fold(area)), None)


def cmd_injury(profile: Profile, args: argparse.Namespace) -> dict:
    # An injury is a safety record: a broken alias file never stops it from being saved; it only
    # falls back to the built-in names for the `unmatched` hint.
    warnings = []
    try:
        muscle_map = strength.muscle_map_for(args.data_dir)
    except ValueError as err:
        muscle_map = strength.load_muscle_map()
        warnings.append(f"{err}; matched against the built-in exercise names only")
    if args.injury_cmd == "add":
        injury = _find_injury(profile, args.area)
        if injury is not None and injury["status"] == "cleared":
            # A new episode in a cleared area: nobody has assessed it yet, so only the lifts it
            # affected carry over.
            fresh = {"area": injury["area"], "exercises": injury.get("exercises", [])}
            profile.injuries[profile.injuries.index(injury)] = injury = fresh
        if injury is None:
            injury = {"area": args.area.strip()}
            profile.injuries.append(injury)
        injury["status"] = "active"
        if args.since:
            injury["since"] = args.since
        if args.professional:
            injury["professional"] = args.professional.strip()
        if args.exercises is not None:
            injury["exercises"] = [e.strip() for e in args.exercises.split(",") if e.strip()]
        save_profile(profile, args.data_dir / "profile.yaml")
    elif args.injury_cmd == "clear":
        injury = _find_injury(profile, args.area)
        if injury is None:
            raise ValueError(f"no injury recorded for {args.area!r}")
        injury["status"] = "cleared"
        injury["cleared_on"] = args.on or args.today or date.today()
        save_profile(profile, args.data_dir / "profile.yaml")
    # Listed names that match no logged lift pause nothing: the skill asks for the logged name.
    logged = {s.exercise for s in read_sets(args.data_dir / "sessions.csv")}
    listed = [e for i in profile.active_injuries() for e in i.get("exercises", [])]
    unmatched = [
        e
        for e in listed
        if fold(e) not in safety.RUN_NAMES
        and not any(strength.named_in(x, [e], muscle_map) for x in logged)
    ]
    return {"injuries": profile.injuries, "unmatched": unmatched} | (
        {"warnings": warnings} if warnings else {}
    )


def cmd_tastes(profile: Profile, args: argparse.Namespace) -> dict:
    path = args.data_dir / "tastes.yaml"
    current = tastes.load_tastes(path)
    if args.tastes_cmd == "set":
        setattr(current, args.field, tastes.parse_value(args.field, args.value))
        tastes.save_tastes(current, path)  # validates
    elif args.tastes_cmd == "rate":
        today = args.today or date.today()
        when = args.date or today
        if when > today:
            raise ValueError(f"{when} is after today ({today}); rate a dish already eaten")
        known = (
            any(fold(r.dish) == fold(args.dish) for r in current.ratings)
            or recipes.find_in_menus(args.data_dir, args.dish)
            or any(
                fold(r["dish"]) == fold(args.dish) for r in recipes.load_all(args.data_dir, current)
            )
        )
        if not known and not args.source.strip():
            raise ValueError(
                f"{args.dish!r} is in no saved menu and not in the recipe library: check the "
                "name, or give its recipe link with --source"
            )
        scheduled = recipes.menu_dates(args.data_dir, args.dish)
        rated_before = any(fold(r.dish) == fold(args.dish) for r in current.ratings)
        if scheduled and all(d > when for d in scheduled) and not rated_before:
            raise ValueError(
                f"{args.dish!r} is first scheduled for {scheduled[0]}, after {when}: rate it once "
                "it has been eaten (or give --date for the day it was)"
            )
        rating = tastes.Rating(args.dish.strip(), args.rating, when, args.source, args.note)
        current.rate(rating)
        tastes.save_tastes(current, path)
        # a dish the client likes joins the recipe library (data/recipes/)
        saved = (
            recipes.save(args.data_dir, args.dish, args.source.strip(), today)
            if args.rating in recipes.SAVED_RATINGS
            else None
        )
        return {"rating": rating, "recipe_saved": saved}
    return _tastes_view(current)


def _tastes_view(current: tastes.Tastes) -> dict:
    return {
        "tastes": current,
        "missing": current.missing(),
        "favoured": current.dishes("loved", "liked"),
        "disliked": current.dishes("disliked"),
        "excluded": current.dishes("never_again"),
    }


def cmd_recipes(profile: Profile, args: argparse.Namespace) -> dict:
    current = tastes.load_tastes(args.data_dir / "tastes.yaml")
    if args.recipes_cmd == "save":
        saved = recipes.save(
            args.data_dir, args.dish, args.source.strip(), args.today or date.today()
        )
        if saved is None:
            raise ValueError(
                f"{args.dish!r} is not in a saved menu: give its recipe link with --source"
            )
        return {"saved": saved}
    library = recipes.load_all(args.data_dir, current)
    if args.recipes_cmd == "show":
        return {"recipe": recipes.get(library, args.dish)}
    if args.recipes_cmd == "remove":
        return {"removed": recipes.remove(args.data_dir, library, args.dish)}
    if args.recipes_cmd == "search":
        library = recipes.search(library, args.words)
    return {
        "recipes": [
            {k: r.get(k) for k in ("dish", "rating", "source", "servings", "file")}
            | {"has_steps": bool(r.get("steps"))}
            for r in library
        ]
    }


def cmd_checkin(profile: Profile, args: argparse.Namespace) -> dict:
    said = [s.strip() for s in (args.symptoms or "").split(",") if s.strip()]
    unknown = [s for s in said if safety.symptom_token(s) is None]
    symptoms = list(dict.fromkeys(safety.symptom_token(s) for s in said if s not in unknown))
    if unknown:
        raise ValueError(f"unknown symptom {', '.join(unknown)}; use {', '.join(safety.SYMPTOMS)}")
    if symptoms:
        # recovery-habits.md: "Cardiac warning symptoms: stop and refer": any one of them. Saved
        # first, so a refused or invalid field cannot drop the stop.
        profile.screening["cardiac_symptoms"] = True
        profile.screening.pop("medically_cleared", None)  # it predates these symptoms
        save_profile(profile, args.data_dir / "profile.yaml")
    flags = safety.flags(profile, args.today)
    refused = ["weight"] if flags.no_weight_targets and args.weight is not None else []
    if safety.eating_disorder_positive(profile) or flags.no_calorie_targets:
        # Judgment call: after a positive screen or under 18, waist and calorie logs are body and
        # intake tracking too (pregnancy refuses weigh-ins only).
        refused += [name for name in ("waist", "intake") if getattr(args, name) is not None]
    if refused:
        reason = safety.weight_block_reason(flags)
        raise ValueError(f"{reason}; {', '.join(refused)} not recorded")
    today = args.today or date.today()
    when = args.date or today
    if when > today:
        recorded = " (the symptoms recorded: run `coach safety`)" if symptoms else ""
        raise ValueError(
            f"{when} is after today ({today}); a check-in is for today or a past day{recorded}"
        )
    checkin = Checkin(
        date=when,
        weight_kg=args.weight,
        waist_cm=args.waist,
        intake_kcal=args.intake,
        sleep_hours=args.sleep,
        notes="; ".join(
            filter(None, [args.notes, symptoms and "symptoms: " + ", ".join(symptoms)])
        ),
    )
    given = [k for k, v in vars(checkin).items() if k != "date" and v not in (None, "")]
    # Rows dated after today (stored before they were refused) are not weigh-ins to compare with.
    past = [c for c in read_checkins(args.data_dir / "checkins.csv") if c.date <= today]
    jump = weight_jump(checkin, past)
    stored = append_checkin(checkin, args.data_dir / "checkins.csv")
    possible = [w for w in safety.red_flag_words(args.notes or "") if w not in symptoms]
    out = dataclasses.asdict(stored) | {
        "warnings": [jump] if jump else [],
        "given": given,
        "symptoms": symptoms,
        "possible_red_flags": possible,
        "possible_injury": safety.injury_words(args.notes or ""),
    }
    if possible:
        # The words never set a flag: the skill asks once, and this records a yes.
        out["confirm_with"] = f"coach checkin add --date {when} --symptoms {','.join(possible)}"
    if symptoms:
        out["deferral_line"], out["emergency_line"] = flags.deferral_line, flags.emergency_line
    return out


def cmd_foods(profile: Profile, args: argparse.Namespace) -> dict:
    region = _region_for(profile, args)

    words = fold_words(*args.words)
    if not words:
        raise ValueError("foods search needs at least one word")

    def hit(*names: str) -> bool:
        # Each search word must start a word of the names ("pollo" finds "pechuga de pollo",
        # not "repollo").
        found = fold_words(*names)
        return all(any(f.startswith(w) for f in found) for w in words)

    region = real_region(region)
    products = regions.load_products(region) if region else []
    return {
        "foods": [
            {"name_en": f.name_en, "name_es": f.name_es}
            | {attr: getattr(f, attr) for attr in foods.NUMBERS}
            | {"missing": f.missing()}
            for f in foods.load_foods(region)
            if hit(f.name_en, f.name_es)
        ],
        "products": [
            {"product_name": p.product_name, "chain": p.chain, "per": p.per}
            | {attr: getattr(p, attr) for attr in foods.NUMBERS}
            | {"missing": [attr for attr in foods.NUMBERS if getattr(p, attr) is None]}
            for p in products
            if hit(p.product_name, p.chain, p.brand)
        ]
        + [
            _catalogue_entry(p)
            for p in catalogue.load(args.data_dir)
            if hit(p.product_name, p.chain, p.brand, p.barcode)
        ],
    }


def _catalogue_entry(p: catalogue.CatalogueProduct) -> dict:
    return (
        {"product_name": p.product_name, "brand": p.brand, "chain": p.chain, "per": p.per}
        | {attr: getattr(p, attr) for attr in foods.NUMBERS}
        | {"missing": p.missing(), "barcode": p.barcode, "allergens": list(p.allergens)}
        | {"source": p.source, "url": p.url}
    )


PER_NAMES = {"100 g": "grams", "100 ml": "millilitres"}


# convention: 8 hex digits (32 bits) tell apart the lossy slugs of one client's few products.
LABEL_KEY_HASH_CHARS = 8
LABEL_ONLY = ("kcal", "protein", "carbs", "fat", "fibre", "allergens", "label_barcode")


# convention: kcal per 100 g is below 900, so a typed 1 or 2 digit prefix, one separator and
# exactly 3 digits (1.674, 12.500) is a kJ value or a thousands grouping, not kcal. A leading 0
# (0,125) is a plain decimal.
KCAL_THOUSANDS = re.compile(r"[1-9][0-9]?[.,][0-9]{3}", re.ASCII)
# Allergen entries are read by structure. Per item (a comma inside parentheses stays in its
# item): an exact none phrase means none; an unknown marker adds `unknown`; a free-from or
# negation claim is refused; text with a recognised allergen word is a declared allergen, stored
# as typed; anything else is stored as typed and adds `unknown` too. Words match whole (never
# "none" inside "piñones").
# The 14 EU allergens in Spanish and English with common synonyms, accent-folded.
ALLERGEN_WORDS = (
    *"""gluten trigo cebada centeno avena espelta kamut wheat barley rye oats
    crustaceos crustaceo gambas gamba langostino langostinos camarones cangrejo crustaceans
    shrimp prawns huevo huevos egg eggs pescado pescados fish
    cacahuete cacahuetes cacahuate cacahuates mani peanut peanuts
    soja soya soy soybeans leche lactosa lacteos milk lactose dairy
    almendra almendras avellana avellanas nuez nueces anacardo anacardos pistacho pistachos
    pinon pinones macadamia pecana pecanas nuts nut almonds hazelnuts walnuts cashews
    pistachios apio celery mostaza mustard sesamo sesame sulfito sulfitos sulphites sulfites
    altramuz altramuces lupin lupino moluscos molusco molluscs mollusks""".split(),
    "frutos de cascara", "frutos secos", "dioxido de azufre", "sulphur dioxide",
)  # fmt: skip
ALLERGEN_VOCAB = re.compile(
    r"(?<!\w)(?:" + "|".join(sorted(ALLERGEN_WORDS, key=len, reverse=True)) + r")(?!\w)"
)
ALLERGEN_UNKNOWN = re.compile(
    r"(?<!\w)(?:unknown|desconoc\w*|desconoz\w*|illegible|ilegible|no legible|not readable"
    r"|no indicado"
    r"|no consta|not sure|n/a|n\.a\.|nd|no data|no info|no informacion|sin informacion"
    r"|no lo se|no se|ns/nc)(?!\w)|\?"
)
ALLERGEN_NONE = {
    "none", "ninguno", "ninguna", "ningun alergeno", "sin alergenos", "sin alergeno",
    "no alergenos", "no contiene", "no contiene alergenos", "no allergens", "nothing", "nada",
}  # fmt: skip
ALLERGEN_NEGATION = re.compile(
    r"(?<!\w)(?:no|sin|without|not|exento|exenta|exentos|exentas|free|libre|libres|doesn|don"
    r"|nunca|ningun\w*|none|nothing|nada)(?!\w)"
)
ALLERGEN_FILLER = re.compile(
    r"(?<!\w)(?:s[ií]|lleva|tiene|contiene|if|it|has|contains)(?!\w)", re.I
)
UNRECOGNISED_WARNING = (
    "unrecognised allergen text: do not use for anyone with an allergy or intolerance until checked"
)


def _split_items(text: str) -> list[str]:
    """Split on commas and semicolons outside parentheses."""
    items, depth, current = [], 0, ""
    for char in text:
        depth += (char in "([") - (char in ")]")
        if char in ",;" and depth <= 0:
            items.append(current)
            current = ""
        else:
            current += char
    return [c for piece in [*items, current] if (c := off._text(piece))]


def _without_markers(piece: str) -> str:
    """The piece minus its unknown markers and filler words, in the client's own spelling."""
    keep, folded = [], ""
    for char in piece:  # fold char by char so folded offsets map back to the original
        part = fold(char) if char.strip() else " "
        folded += part
        keep += [char] * len(part)
    drop = {i for m in ALLERGEN_UNKNOWN.finditer(folded) for i in range(m.start(), m.end())}
    rest = "".join(c if i not in drop else " " for i, c in enumerate(keep))
    rest = re.sub(r"[(\[]\s*[)\]]", " ", ALLERGEN_FILLER.sub(" ", rest))
    return " ".join(rest.strip(" ,.:;-/").split())


def _label_allergens(text: str) -> tuple[list[str], bool]:
    """(allergens, unrecognised): `none` is [], `unknown` leads the list; unrecognised is True
    when some text was kept that is not a known allergen."""
    if not (pieces := _split_items(text)):
        raise ValueError("--allergens is empty: list them, or say none or unknown")
    unknown = none = unrecognised = False
    declared: dict[str, str] = {}  # folded -> first spelling, in first-seen order
    for piece in pieces:
        if fold(piece) in ALLERGEN_NONE:
            none = True
            continue
        marked = bool(ALLERGEN_UNKNOWN.search(fold(piece)))
        if marked:
            unknown = True
            piece = _without_markers(piece)
            if not piece:
                continue
        folded = fold(piece)
        if ALLERGEN_NEGATION.search(folded):
            raise ValueError(
                f"--allergens {piece!r} is a free-from claim: write only the allergens the pack "
                "declares, or exactly none (it declares none) or unknown (it cannot be read)"
            )
        if ALLERGEN_VOCAB.search(folded):
            declared.setdefault(folded, piece)
        elif not marked:  # text left beside a marker is not stored as an allergen
            unknown = unrecognised = True
            declared.setdefault(folded, piece)
    if none and (declared or unknown):
        raise ValueError(f"--allergens {text!r}: none cannot be combined with other allergens")
    return (["unknown", *declared.values()] if unknown else list(declared.values())), unrecognised


def _label_product(args: argparse.Namespace) -> dict:
    """Values the client read off the pack: no network, same limits as Open Food Facts values."""
    required = ("name", "per", "kcal", "protein", "carbs", "fat", "allergens")
    if missing := [f"--{f}" for f in required if getattr(args, f) is None]:
        raise ValueError(f"--label also needs {', '.join(missing)}")
    values = {}
    for column, flag, raw in (
        ("kcal", "kcal", args.kcal),
        ("protein_g", "protein", args.protein),
        ("carbs_g", "carbs", args.carbs),
        ("fat_g", "fat", args.fat),
        ("fibre_g", "fibre", args.fibre),
    ):
        if raw is None:
            values[column] = None
            continue
        limit = off.MAX_KCAL_PER_100G if column == "kcal" else off.MAX_G_PER_100G
        text = raw.strip()
        if column == "kcal" and KCAL_THOUSANDS.fullmatch(text):
            raise ValueError(f"--kcal {raw!r} looks like kJ or a thousands number: type kcal")
        # ASCII digits, at most one "." or "," ("9,5", ",5", "5.", grams "9.500"); no "1_0", "1e1".
        # Limits are below 1000, so one separator is always a decimal point.
        strict = re.fullmatch(r"(?=.*[0-9])[0-9]*(?:[.,][0-9]*)?", text, re.ASCII)
        number = off._number(text.replace(",", ".") if strict else None, limit)
        if number is None:
            raise ValueError(f"--{flag} {raw!r} must be a number from 0 to {limit:g}")
        values[column] = number
    if args.label_barcode is not None and not off.BARCODE.fullmatch(args.label_barcode):
        raise ValueError(f"a barcode is 8 to 14 digits, not {args.label_barcode!r}")
    name = off._text(args.name)
    if not name:
        raise ValueError("--name is empty")
    # The slug is lossy (cuts, drops non-Latin text): then the key also carries a hash of the
    # folded name, so different names stay different keys.
    stem = recipes.slug(name)
    if fold(name) != stem.replace("-", " "):  # plain only when the name is exactly its slug
        stem += "-" + hashlib.sha1(fold(name).encode()).hexdigest()[:LABEL_KEY_HASH_CHARS]
    allergens, unrecognised = _label_allergens(args.allergens)
    return {
        # the slug keeps path and CSV structure out of the key
        "barcode": args.label_barcode or f"label-{stem}",
        "name": name,
        "brand": None,
        "per": args.per,
        "values": values,
        "allergens": allergens,
        "unrecognised": unrecognised,
        "url": "",
    }


def cmd_products(profile: Profile, args: argparse.Namespace) -> dict:
    if args.products_cmd == "list":
        return {"products": [_catalogue_entry(p) for p in catalogue.load(args.data_dir)]}
    if args.products_cmd == "search":
        hits = off.search(args.words, args.brand, args.limit, profile.language or "es")
        return {"source": catalogue.SOURCE, "hits": hits}
    if not args.label:
        stray = [
            "--" + f.replace("label_", "").replace("_", "-")
            for f in LABEL_ONLY
            if getattr(args, f) is not None
        ]
        if stray:
            raise ValueError(f"{', '.join(stray)} only work with --label")
    if args.label:
        if args.confirm_per:
            raise ValueError("--confirm-per does nothing with --label (there is no pack unit)")
        if args.barcode:
            raise ValueError("with --label, give the barcode as --barcode, not as an argument")
        found = _label_product(args)
    else:
        if not args.barcode:
            raise ValueError("give a BARCODE, or --label to type the values from the pack")
        found = off.product(args.barcode)
        if found is None:
            raise ValueError(
                f"{args.barcode} is not in Open Food Facts; check the barcode on the pack"
            )
        found["barcode"] = args.barcode
    barcode = found["barcode"]
    name = " ".join(((found["name"] if args.label else args.name or found["name"]) or "").split())
    if not name:
        raise ValueError(f"Open Food Facts has no name for {args.barcode}: give one with --name")
    per = args.per or found["per"]
    if args.per and found["per"] and args.per != found["per"] and not args.confirm_per:
        raise ValueError(
            f"Open Food Facts says {args.barcode} is sold in {PER_NAMES[found['per']]}, so its "
            f'values are per {found["per"]}, not per {args.per}: use --per "{found["per"]}", '
            f"or read the label and add --confirm-per to keep per {args.per}"
        )
    if per is None:
        raise ValueError(
            f"Open Food Facts does not say whether {args.barcode} is sold by weight or volume: "
            'give --per "100 g" or --per "100 ml"'
        )
    products = catalogue.load(args.data_dir)
    stored = next((p for p in products if p.barcode == barcode), None)
    if stored and not args.label and stored.source == catalogue.LABEL_SOURCE:
        raise ValueError(
            f"{barcode} is a hand-entered label row: "
            "correct it by giving every label value again: "
            f"--label --barcode {barcode} --replace --name ... (all values)"
        )
    if stored and args.label and stored.source != catalogue.LABEL_SOURCE:
        raise ValueError(
            f"{barcode} is an {stored.source} row: label values never overwrite it; "
            "use a different --barcode, or omit --barcode, for a separate product"
        )
    # Only a generated key can be a lossy collision; an explicit barcode may rename its product.
    if (
        stored
        and args.label
        and not args.label_barcode
        and (fold(stored.product_name) != fold(name))
    ):
        raise ValueError(
            f"{barcode} is already in the catalogue as a DIFFERENT product "
            f"({stored.product_name!r}, not {name!r}): pass --barcode with the pack's barcode, "
            "or --name with a more specific name"
        )
    if stored and not args.replace:
        raise ValueError(f"{barcode} is already in the catalogue: add --replace to refresh it")
    others = [p for p in products if p.barcode != barcode]
    table = regions.menu_table(profile.region) + [p.as_food() for p in others]
    if foods.find(name, table) is not None:
        raise ValueError(f"{name!r} is already a food or product name: choose one with --name")
    product = catalogue.CatalogueProduct(
        barcode=barcode,
        product_name=name,
        brand=found["brand"] or "",
        chain=" ".join(args.chain.split()),
        per=per,
        **found["values"],
        allergens=tuple(found["allergens"]),
        url=found["url"],
        fetched_on=args.today or date.today(),
        source=catalogue.LABEL_SOURCE if args.label else catalogue.SOURCE,
    )
    gap = None
    if args.label and None not in (product.kcal, product.protein_g, product.carbs_g, product.fat_g):
        kind, reason = foods.energy_check(product.to_row(), typed=True) or ("", "")
        computed = foods.label_energy(product.to_row())
        if kind == foods.GAP and abs(product.kcal - computed) / computed > LABEL_REFUSE_GAP:
            gap = reason
    if gap and not args.confirm_kcal:
        raise ValueError(
            f"label kcal is {gap}: more than {LABEL_REFUSE_GAP:.0%} off, so probably a typo or "
            "the wrong column (per serving, kJ). Read the label again; if it really says so, add "
            "--confirm-kcal"
        )
    catalogue.save([*others, product], args.data_dir)
    warnings = []
    if args.label and found["unrecognised"]:
        warnings.append(UNRECOGNISED_WARNING)
    elif args.label and "unknown" in product.allergens:
        warnings.append("allergens unknown: do not use for anyone with an allergy or intolerance")
    if None not in (product.kcal, product.protein_g, product.carbs_g, product.fat_g):
        kind, reason = foods.energy_check(product.to_row(), typed=args.label) or ("", "")
        again = (
            ": read the label again, fix it with --replace" if args.label else "; check the pack"
        )
        lead = "label kcal is" if args.label else "kcal is"
        if kind == foods.NO_MACROS:
            warnings.append(f"{lead} stated but no energy-yielding macros are listed{again}")
        elif kind == foods.GAP:
            warnings.append(f"{lead} {reason}{again}")
    return {"added": product, "missing": product.missing(), "warnings": warnings}


# convention: a typed label kcal more than 50% away from its 4/4/9 value is refused unless
# confirmed: nutrition.md "EU label rules and tolerances" allows about 20%, so a gap this size is a
# typo, a per-serving column or kJ, not a tolerance. Between 10% and 50% it is a warning.
LABEL_REFUSE_GAP = 0.5


# The header lines /plan writes at the top of data/plan.md (.claude/skills/plan/SKILL.md step 6).
PLAN_DATE_KEYS = ("Date", "Fecha")


def _same_number(text: str, value: float) -> bool:
    try:
        return float(text) == value
    except ValueError:
        return False


def cmd_plan(profile: Profile, args: argparse.Namespace) -> dict:
    path = args.data_dir / "plan.md"
    if not path.exists():
        raise ValueError(f"no plan at {path}: /plan writes it")
    flags = safety.flags(profile, args.today)
    stale = (
        "the plan is stale: safety now stops training ("
        + "; ".join(safety.stop_reasons(flags))
        + "); run /plan again once a clinician clears it"
        if flags.no_training
        else None
    )
    if args.plan_cmd == "export":
        if stale:
            raise ValueError(stale)
        out = _in_data_dir(args, args.out)
        text = path.read_text(encoding="utf-8")
        exercises = export.write_plan(out, text, profile.language, qr=not args.no_qr)
        return {
            "pdf": _shown(args, out),
            "exercises": exercises,
            # Session parts that name no lift: they are in the PDF's text but get no video link.
            "unread": export.plan_unread(text),
            "qr": not args.no_qr,
        }
    text = path.read_text(encoding="utf-8")
    head = text.splitlines()[:3]
    fields = dict(line.split(":", 1) for line in head if ":" in line)
    fields = {k.strip(): v.strip() for k, v in fields.items()}
    problems = [stale] if stale else []
    unread = export.plan_unread(text)
    if unread:
        problems.append(
            "training bullets the export cannot read as lifts (write `Name load`, `Name 3x8` "
            "or `Name, 3 sets of 8-12`): " + "; ".join(unread)
        )
    week_file = args.data_dir / "plan-week.yaml"
    if week_file.exists():
        try:
            week = yaml.safe_load(week_file.read_text(encoding="utf-8")) or {}
        except yaml.YAMLError:
            week = None
        planned = week.get("sessions") if isinstance(week, dict) else None
        sessions = export.plan_sessions(text)
        if not isinstance(planned, list):
            problems.append(
                "plan-week.yaml needs `sessions:`, a list of {name, exercises}: rewrite it, then "
                "rerun `coach strength plan-sets`"
            )
        elif sessions != len(planned):
            problems.append(
                f"plan.md lists {sessions} sessions with lifts but plan-week.yaml has "
                f"{len(planned)}: write the same week in both, then rerun "
                "`coach strength plan-sets`"
            )
    if not any(k in fields for k in PLAN_DATE_KEYS):
        problems.append("line 1 must be `Date: YYYY-MM-DD` (es: `Fecha:`)")
    problems += [
        f"missing header line `{key}:` in the first three lines"
        for key in ("target_kcal", "in_deficit")
        if key not in fields
    ]
    notes = []
    args.kcal, args.in_deficit = None, False
    fresh = cmd_macros(profile, args)
    if "target_kcal" in fields and "in_deficit" in fields:
        try:
            kcal = float(fields["target_kcal"])
            if not math.isfinite(kcal):
                raise ValueError
        except ValueError:
            kcal = None
            problems.append(f"target_kcal must be a number, not {fields['target_kcal']!r}")
        if fields["in_deficit"].lower() not in ("true", "false"):
            problems.append(f"in_deficit must be true or false, not {fields['in_deficit']!r}")
        elif kcal is not None:
            # The stored target as /menu will use it: the safety rules raise or lower it here.
            args.kcal, args.in_deficit = kcal, fields["in_deficit"].lower() == "true"
            used = cmd_macros(profile, args)
            if not _same_number(fields["target_kcal"], used["kcal"]) or (
                used["in_deficit"] != args.in_deficit
            ):
                problems.append(
                    f"the safety rules change this target: `coach macros --kcal` gives "
                    f"{used['kcal']:g} kcal, in_deficit {str(used['in_deficit']).lower()}"
                )
            elif not _same_number(fields["target_kcal"], fresh["kcal"]):
                # A target agreed at /review (--tdee, --current-kcal) or kept from the last plan.
                notes.append(
                    f"target_kcal differs from a fresh estimate ({fresh['kcal']:g} kcal): fine "
                    "when it was agreed at /review or kept from the previous plan"
                )
    return {
        "ok": not problems,
        "problems": problems,
        "unread": unread,
        "notes": notes,
        "fresh_estimate": {"target_kcal": fresh["kcal"], "in_deficit": fresh["in_deficit"]},
    }


def cmd_knowledge(profile: Profile, args: argparse.Namespace) -> dict | str:
    if args.knowledge_cmd == "section":
        return knowledge.section(args.file, args.heading)
    if args.knowledge_cmd == "audit":
        return knowledge.audit(args.file, args.heading)
    months = args.months or profile.research_reminder_months
    stale = knowledge.stale_files(months, args.today or date.today())
    return {"months": months, "stale": [{"file": f, "checked": d} for f, d in stale]}


class UsageError(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    """Bad arguments raise instead of printing usage, so a skill always gets JSON back."""

    def error(self, message: str) -> NoReturn:
        raise UsageError(f"{self.prog}: {message}")


def build_parser() -> argparse.ArgumentParser:
    parser = _Parser(prog="coach", description=__doc__.splitlines()[0])
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=Path(os.environ.get("COACH_DATA_DIR", DEFAULT_DATA_DIR)),
        help="default: $COACH_DATA_DIR, else data/",
    )
    parser.add_argument("--today", type=date.fromisoformat, default=None, help="for tests")
    json_flag = argparse.ArgumentParser(add_help=False)
    json_flag.add_argument("--json", action="store_true", help="one compact JSON line")
    # Also after the subcommand (`coach menu ... --today D`); it overrides the global one.
    json_flag.add_argument(
        "--today", type=date.fromisoformat, default=argparse.SUPPRESS, help=argparse.SUPPRESS
    )
    sub = parser.add_subparsers(dest="command", required=True)

    def add(name: str, func, help_text: str) -> argparse.ArgumentParser:
        command = sub.add_parser(name, parents=[json_flag], help=help_text)
        command.set_defaults(func=func)
        return command

    energy_cmd = add("energy", cmd_energy, "RMR, TDEE and the daily calorie target")
    macros_cmd = add("macros", cmd_macros, "protein, fat, carbs and fibre for the target")
    for command in (energy_cmd, macros_cmd):
        command.add_argument("--goal", default=None, choices=GOALS)
        command.add_argument("--pal", type=float, default=None, help="explicit activity factor")
        command.add_argument("--tdee", type=float, default=None, help="recalibrated TDEE")
        command.add_argument(
            "--current-kcal",
            type=float,
            default=None,
            help="current intake (holds a deficit; with --tdee, cuts one step at a time)",
        )
    macros_cmd.add_argument("--kcal", type=float, default=None)
    macros_cmd.add_argument("--in-deficit", action="store_true")

    trend_cmd = add("trend", cmd_trend, "weight trend from data/checkins.csv")
    trend_cmd.add_argument("--energy-density", type=float, default=trend.ENERGY_DENSITY_KCAL_PER_KG)
    zones_cmd = add("zones", cmd_zones, "heart-rate and RPE zones")
    zones_cmd.add_argument("--hr-rest", type=int, default=None, help="default: profile hr_rest")
    zones_cmd.add_argument("--hr-max", type=int, default=None, help="default: profile hr_max")
    add("safety", cmd_safety, "screening flags and the rules behind them")

    strength_cmd = add("strength", cmd_strength, "e1RM, weekly sets, progression, deload")
    strength_sub = strength_cmd.add_subparsers(dest="strength_cmd", required=True)
    e1rm_cmd = strength_sub.add_parser("e1rm", parents=[json_flag])
    e1rm_cmd.add_argument("--weight", type=float, required=True)
    e1rm_cmd.add_argument("--reps", type=int, required=True)
    e1rm_cmd.add_argument("--rir", type=float, default=0)
    deload_cmd = strength_sub.add_parser("deload", parents=[json_flag])
    deload_cmd.add_argument(
        "--signs",
        required=True,
        help=", ".join(sorted(strength.DELOAD_SIGNS | strength.OVERREACHING_SIGNS)),
    )
    plan_sets_cmd = strength_sub.add_parser(
        "plan-sets", parents=[json_flag], help="weekly hard sets of a planned week (YAML)"
    )
    plan_sets_cmd.add_argument("file", type=Path, help="relative to the data dir")
    alias_cmd = strength_sub.add_parser(
        "alias", parents=[json_flag], help="the client's own exercise names (muscle_aliases.yaml)"
    )
    alias_sub = alias_cmd.add_subparsers(dest="alias_cmd", required=True)
    alias_add = alias_sub.add_parser("add", parents=[json_flag], help="NAME EXERCISE")
    alias_add.add_argument("name", help="the name as the client logs it")
    alias_add.add_argument("exercise", help="a lift the muscle map knows, e.g. bent over row")
    alias_sub.add_parser("list", parents=[json_flag])
    sets_cmd = strength_sub.add_parser("sets", parents=[json_flag], help="weekly hard sets")
    sets_cmd.add_argument("--week-ending", type=date.fromisoformat, default=None)
    progress_cmd = strength_sub.add_parser("progress", parents=[json_flag], help="next session")
    progress_cmd.add_argument("--exercise", default=None, help="default: lifts of the last 4 weeks")
    progress_cmd.add_argument(
        "--rep-range",
        action="append",
        default=[],
        metavar=strength.REP_RANGE_FORMAT,
        help="rep range for one lift, e.g. squat=6-8; repeat per lift; a lift with no logged "
        f"sets is ignored; default {strength.REP_RANGE[0]}-{strength.REP_RANGE[1]}",
    )

    import_cmd = add(
        "import", cmd_import, "import a workout export into data/sessions.csv (runs: runs.csv)"
    )
    import_cmd.add_argument("path", type=Path)
    import_cmd.add_argument("--importer", default=None, help="default: detect from the header")

    runs_cmd = add("runs", cmd_runs, "log runs in data/runs.csv, weekly km and zones, taper")
    runs_sub = runs_cmd.add_subparsers(dest="runs_cmd", required=True)
    runs_add = runs_sub.add_parser("add", parents=[json_flag], help="one run")
    runs_add.add_argument("--date", type=date.fromisoformat, default=None, help="default: today")
    runs_add.add_argument("--km", type=float, required=True)
    runs_add.add_argument("--minutes", type=float, required=True)
    runs_add.add_argument("--avg-hr", type=int, default=None)
    runs_add.add_argument("--max-hr", type=int, default=None)
    runs_add.add_argument("--rpe", type=int, default=None, help="Borg 6-20, as in coach zones")
    runs_add.add_argument("--notes", default="")
    runs_week = runs_sub.add_parser("week", parents=[json_flag], help="weekly km, spikes, zones")
    runs_week.add_argument(
        "--week-ending", type=date.fromisoformat, default=None, help="default: last logged run"
    )
    runs_taper = runs_sub.add_parser("taper", parents=[json_flag], help="taper before a race")
    runs_taper.add_argument("--race-date", type=date.fromisoformat, required=True)

    menu_cmd = add("menu", cmd_menu, "macro totals for foods and grams")
    menu_cmd.add_argument("--item", action="append", required=True, help='"NAME=GRAMS", repeat')
    menu_cmd.add_argument("--region", default=None, help="default: the profile's region")
    menu_cmd.add_argument(
        "--targets", action="store_true", help="check the totals against `coach macros`"
    )
    menu_cmd.add_argument("--kcal", type=float, default=None, help="stored calorie target")
    menu_cmd.add_argument(
        "--in-deficit", action="store_true", help="the stored target is a deficit"
    )
    menu_cmd.add_argument(
        "--current-kcal", type=float, default=None, help="current intake (holds a deficit)"
    )
    menu_cmd.set_defaults(goal=None, pal=None, tdee=None)

    mealplan_cmd = add("mealplan", cmd_mealplan, "check, save or list multi-day menus")
    mealplan_sub = mealplan_cmd.add_subparsers(dest="mealplan_cmd", required=True)
    for name, help_text in (("check", "check every day"), ("save", "check, then save")):
        plan_cmd = mealplan_sub.add_parser(name, parents=[json_flag], help=help_text)
        plan_cmd.add_argument("file", type=Path, help="the draft; relative to the data dir")
        plan_cmd.add_argument("--kcal", type=float, default=None, help="stored calorie target")
        plan_cmd.add_argument(
            "--in-deficit", action="store_true", help="the stored target is a deficit"
        )
        plan_cmd.add_argument(
            "--current-kcal", type=float, default=None, help="current intake (holds a deficit)"
        )
        plan_cmd.set_defaults(goal=None, pal=None, tdee=None)
    mealplan_sub.choices["save"].add_argument(
        "--replace", action="store_true", help="overwrite a menu saved for the same first date"
    )
    mealplan_sub.add_parser("list", parents=[json_flag])
    export_cmd = mealplan_sub.add_parser(
        "export", parents=[json_flag], help="a saved menu as a PDF (needs the pdf extra)"
    )
    export_cmd.add_argument(
        "menu", type=Path, nargs="?", default=None, help="default: the newest in data/menus/"
    )
    export_cmd.add_argument("--out", type=Path, default=None, help="default: next to the menu")
    export_cmd.add_argument("--no-qr", action="store_true", help="no QR code per recipe link")

    shopping_cmd = add("shopping", cmd_shopping, "shopping list from a saved menu")
    shopping_cmd.add_argument(
        "menu", type=Path, nargs="?", default=None, help="default: the newest in data/menus/"
    )

    foods_cmd = add("foods", cmd_foods, "search the food tables and regional products")
    foods_sub = foods_cmd.add_subparsers(dest="foods_cmd", required=True)
    search_cmd = foods_sub.add_parser("search", parents=[json_flag], help="WORD [WORD...]")
    search_cmd.add_argument("words", nargs="+")
    search_cmd.add_argument("--region", default=None, help="default: the profile's region")

    products_cmd = add(
        "products",
        cmd_products,
        "products in data/catalogue.csv: Open Food Facts (unverified) or values from the label",
    )
    products_sub = products_cmd.add_subparsers(dest="products_cmd", required=True)
    off_search = products_sub.add_parser("search", parents=[json_flag], help="WORD [WORD...]")
    off_search.add_argument("words", nargs="+")
    off_search.add_argument("--brand", default=None, help='e.g. "Hacendado"')
    off_search.add_argument("--limit", type=int, default=off.SEARCH_LIMIT)
    off_add = products_sub.add_parser(
        "add", parents=[json_flag], help="BARCODE --chain CHAIN, or --label with the pack's values"
    )
    off_add.add_argument("barcode", nargs="?", default=None)
    off_add.add_argument("--chain", required=True, help="the supermarket the client buys it at")
    off_add.add_argument("--name", default=None, help="default: the Open Food Facts name")
    off_add.add_argument("--per", default=None, choices=sorted(off.UNITS.values()))
    off_add.add_argument(
        "--confirm-per",
        action="store_true",
        help="keep --per although the pack unit says otherwise (after reading the label)",
    )
    off_add.add_argument(
        "--confirm-kcal",
        action="store_true",
        help="keep a label kcal far from its macros (after reading the label again)",
    )
    off_add.add_argument("--replace", action="store_true", help="refresh a product already added")
    off_add.add_argument(
        "--label", action="store_true", help="type the values from the pack: no Open Food Facts"
    )
    for flag in ("kcal", "protein", "carbs", "fat", "fibre"):
        off_add.add_argument(f"--{flag}", default=None, help="--label: per 100 g or 100 ml")
    off_add.add_argument("--barcode", dest="label_barcode", default=None, help="--label only")
    off_add.add_argument(
        "--allergens", default=None, help='--label (required): "soja, leche", none, or unknown'
    )
    products_sub.add_parser("list", parents=[json_flag])

    profile_cmd = add("profile", cmd_profile, "show or set data/profile.yaml fields")
    profile_sub = profile_cmd.add_subparsers(dest="profile_cmd", required=True)
    profile_sub.add_parser("show", parents=[json_flag])
    set_cmd = profile_sub.add_parser("set", parents=[json_flag], help="FIELD VALUE")
    set_cmd.add_argument("field", help="a profile field, or screening.<key>")
    set_cmd.add_argument(
        "value", help="lists comma-separated; dates YYYY-MM-DD; true/false; none clears screening"
    )

    injury_cmd = add("injury", cmd_injury, "record, clear or list injuries in the profile")
    injury_sub = injury_cmd.add_subparsers(dest="injury_cmd", required=True)
    injury_add = injury_sub.add_parser("add", parents=[json_flag], help="AREA: active injury")
    injury_add.add_argument("area", help="in the client's words; the same area updates it")
    injury_add.add_argument("--since", type=date.fromisoformat, default=None)
    injury_add.add_argument("--professional", default=None, help="who assessed and manages it")
    injury_add.add_argument(
        "--exercises", default=None, help="logged exercise names whose loads pause, comma-separated"
    )
    injury_clear = injury_sub.add_parser("clear", parents=[json_flag], help="AREA: cleared")
    injury_clear.add_argument("area")
    injury_clear.add_argument("--on", type=date.fromisoformat, default=None, help="default: today")
    injury_sub.add_parser("list", parents=[json_flag])

    tastes_cmd = add("tastes", cmd_tastes, "show, set or rate data/tastes.yaml (food preferences)")
    tastes_sub = tastes_cmd.add_subparsers(dest="tastes_cmd", required=True)
    tastes_sub.add_parser("show", parents=[json_flag])
    tastes_set = tastes_sub.add_parser("set", parents=[json_flag], help="FIELD VALUE")
    tastes_set.add_argument("field", help=", ".join(tastes.SETTABLE))
    tastes_set.add_argument("value", help="lists comma-separated; none for an empty answer")
    rate_cmd = tastes_sub.add_parser("rate", parents=[json_flag], help="DISH RATING")
    rate_cmd.add_argument("dish")
    rate_cmd.add_argument("rating", choices=tastes.RATINGS)
    rate_cmd.add_argument("--source", default="", help="the recipe or video link")
    rate_cmd.add_argument("--note", default="")
    rate_cmd.add_argument(
        "--date", type=date.fromisoformat, default=None, help="when it was eaten; default: today"
    )

    recipes_cmd = add("recipes", cmd_recipes, "the recipe library in data/recipes/ (rated dishes)")
    recipes_sub = recipes_cmd.add_subparsers(dest="recipes_cmd", required=True)
    recipes_sub.add_parser("list", parents=[json_flag])
    recipes_search = recipes_sub.add_parser("search", parents=[json_flag], help="WORD [WORD...]")
    recipes_search.add_argument("words", nargs="+")
    recipes_show = recipes_sub.add_parser("show", parents=[json_flag], help="DISH")
    recipes_show.add_argument("dish")
    recipes_save = recipes_sub.add_parser("save", parents=[json_flag], help="DISH: from a menu")
    recipes_save.add_argument("dish")
    recipes_save.add_argument("--source", default="", help="the recipe or video link")
    recipes_remove = recipes_sub.add_parser("remove", parents=[json_flag], help="DISH")
    recipes_remove.add_argument("dish")

    checkin_cmd = add("checkin", cmd_checkin, "record a daily check-in in data/checkins.csv")
    checkin_sub = checkin_cmd.add_subparsers(dest="checkin_cmd", required=True)
    add_cmd = checkin_sub.add_parser("add", parents=[json_flag])
    add_cmd.add_argument("--date", type=date.fromisoformat, default=None)
    add_cmd.add_argument("--weight", type=float, default=None)
    add_cmd.add_argument("--waist", type=float, default=None)
    add_cmd.add_argument("--intake", type=float, default=None, help="logged kcal for the day")
    add_cmd.add_argument("--sleep", type=float, default=None, help="hours")
    add_cmd.add_argument("--notes", default="")
    add_cmd.add_argument(
        "--symptoms", default="", help=f"comma-separated: {', '.join(safety.SYMPTOMS)}"
    )

    plan_cmd = add("plan", cmd_plan, "check data/plan.md's header, or export it as a PDF")
    plan_sub = plan_cmd.add_subparsers(dest="plan_cmd", required=True)
    check_plan = plan_sub.add_parser("check", parents=[json_flag])
    check_plan.add_argument("--goal", default=None, choices=GOALS)
    check_plan.add_argument("--pal", type=float, default=None, help="as given to /plan")
    check_plan.add_argument("--tdee", type=float, default=None, help="as given to /plan")
    check_plan.add_argument("--current-kcal", type=float, default=None, help="as given to /plan")
    export_plan = plan_sub.add_parser(
        "export", parents=[json_flag], help="data/plan.md as a PDF (needs the pdf extra)"
    )
    export_plan.add_argument(
        "--out", type=Path, default=Path("plan.pdf"), help="default: plan.pdf in the data dir"
    )
    export_plan.add_argument("--no-qr", action="store_true", help="no QR code per video link")
    knowledge_cmd = add("knowledge", cmd_knowledge, "knowledge staleness and sections")
    knowledge_sub = knowledge_cmd.add_subparsers(dest="knowledge_cmd", required=True)
    stale_cmd = knowledge_sub.add_parser("stale", parents=[json_flag])
    stale_cmd.add_argument("--months", type=int, default=None)
    section_cmd = knowledge_sub.add_parser("section", parents=[json_flag])
    section_cmd.add_argument("file")
    section_cmd.add_argument("heading")
    audit_cmd = knowledge_sub.add_parser(
        "audit", parents=[json_flag], help="FILE HEADING: rule, grade, each source's Supports"
    )
    audit_cmd.add_argument("file")
    audit_cmd.add_argument("heading")
    return parser


def _print(payload: Any, compact: bool) -> None:
    if isinstance(payload, str):
        print(payload, end="")
    else:
        print(json.dumps(_jsonable(payload), ensure_ascii=False, indent=None if compact else 2))


def main(argv: list[str] | None = None) -> int:
    try:
        args = build_parser().parse_args(argv)
    except UsageError as err:
        _print({"error": "invalid", "message": str(err)}, compact=True)
        return 2
    compact = getattr(args, "json", False)
    try:
        profile = load_profile(args.data_dir / "profile.yaml")
        _print(args.func(profile, args), compact)
    except ProfileIncomplete as err:
        _print({"error": "profile_incomplete", "field": err.field}, compact)
        return 2
    except (ValueError, OSError, knowledge.SectionNotFound) as err:
        _print({"error": "invalid", "message": str(err)}, compact)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
