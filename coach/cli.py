"""Command line for the coach skills: every number a skill quotes comes from here.

    uv run python -m coach [--data-dir DIR] [--today YYYY-MM-DD] <command> ... [--json]

Commands print JSON (indented unless --json asks for one compact line). A missing profile field
exits with code 2 and {"error": "profile_incomplete", "field": "<name>"} so the skill can ask
for it; invalid input exits 2 with {"error": "invalid", "message": ...}.
"""

from __future__ import annotations

import argparse
import dataclasses
import json
import os
import re
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path
from statistics import fmean
from typing import Any, NoReturn

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
    safety,
    strength,
    tastes,
    trend,
    zones,
)
from coach.checkins import Checkin, append_checkin, read_checkins, weigh_ins
from coach.profile import (
    CONDITION_TOKENS,
    GOALS,
    MEDICATION_TOKENS,
    PARQ_ANSWERS,
    SCREENING_KEYS,
    Profile,
    ProfileIncomplete,
    load_profile,
    save_profile,
)
from coach.sessions.importers import base as importers  # the package registers importers
from coach.sessions.model import ExerciseSet
from coach.sessions.store import append, read_sets
from coach.text import fold

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
    estimated = energy.tdee(profile, args.pal, args.today)
    target = energy.calorie_target(
        profile,
        flags,
        goal=args.goal,
        today=args.today,
        tdee_kcal=args.tdee if args.tdee is not None else estimated,
        current_kcal=args.current_kcal,
        recalibrated=args.tdee is not None,
    )
    return {"rmr": rmr, "tdee": estimated, "target": target}


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
        elif kcal > allowed and (flags.no_weight_targets or flags.prescriber_owns_weight):
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


def cmd_zones(profile: Profile, args: argparse.Namespace) -> zones.Zones:
    return zones.hr_zones(
        profile, safety.flags(profile, args.today), args.hr_rest, args.hr_max, args.today
    )


def cmd_safety(profile: Profile, args: argparse.Namespace) -> safety.SafetyFlags:
    return safety.flags(profile, args.today)


def cmd_strength(profile: Profile, args: argparse.Namespace) -> dict:
    if args.strength_cmd == "e1rm":
        return {"e1rm": strength.e1rm(args.weight, args.reps, args.rir)}
    if args.strength_cmd == "deload":
        signs = {s.strip() for s in args.signs.split(",") if s.strip()}
        return {"deload": strength.deload(signs)}
    today = args.today or date.today()
    logged = [s for s in read_sets(args.data_dir / "sessions.csv") if s.date <= today]
    muscle_map = strength.load_muscle_map()
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
    return {
        name: strength.progression(
            [s for s in logged if s.exercise == name],
            today=today,
            rep_range=strength.rep_range_for(name, ranges),
            muscle_map=muscle_map,
            flags=flags,
            stall_after=strength.pause_end(name, profile.injuries, muscle_map),
        )
        for name in names
    }


def _leftover_warning(leftovers: list[ExerciseSet]) -> str:
    counts = Counter((s.exercise, s.date.isoformat()) for s in leftovers)
    which = ", ".join(f"{name} {day} x{n}" for (name, day), n in sorted(counts.items()))
    return (
        f"{len(leftovers)} sets with no reps, weight, duration or distance (template leftovers) "
        f"were not stored: {which}"
    )


def cmd_import(profile: Profile, args: argparse.Namespace) -> dict:
    importer = importers.get(args.importer) if args.importer else importers.detect(args.path)
    read = importer.read(args.path)
    # Empty rows are what an app leaves when a routine template's sets are never filled in. They
    # carry nothing any calculator reads (no reps, so not a working set), so storing them would
    # only inflate `added`; they are skipped and reported instead.
    leftovers = [s for s in read if s.is_empty]
    sets = [s for s in read if not s.is_empty]
    store = args.data_dir / "sessions.csv"
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
    return {
        "importer": importer.name,
        "read": len(read),
        "added": result.added,
        "duplicates": result.duplicates,
        "skipped_empty": len(leftovers),
        "first_day": days[0] if days else None,
        "last_day": days[-1] if days else None,
        "warnings": warnings,
    }


def menu_check(totals: dict, targets: dict, share: float = 1.0) -> dict:
    """'ok', 'under' or 'over' per target: kcal within [target, target + MENU_KCAL_MARGIN], protein
    and fibre at least their targets, fat at least its minimum. Carbohydrate fills the rest.

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
    floors = {"protein_g": "protein_g", "fat_g": "fat_min_g", "fibre_g": "fibre_g"}
    return {"kcal": kcal_status} | {
        key: "ok"
        if totals[key] >= targets[target] * share
        else "missing"
        if key in missing
        else "under"
        for key, target in floors.items()
    }


def _menu_day(totals: foods.MenuTotals, targets: dict, share: float = 1.0) -> dict:
    check = menu_check(dataclasses.asdict(totals), targets, share)
    return {
        "totals": totals,
        "targets": targets,
        "check": check,
        "ok": not totals.unknown and set(check.values()) == {"ok"},
    }


def _free_meal(day: mealplan.Day, totals: foods.MenuTotals, targets: dict) -> dict:
    """What the free meal has left to reach the day's targets (never below 0): the targets minus
    the planned meals, using the values the planned items have."""
    left = {
        "kcal": targets["kcal"] - totals.kcal,
        "protein_g": targets["protein_g"] - totals.protein_g,
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


def _menu_table(profile: Profile, args: argparse.Namespace) -> list[foods.Food]:
    return regions.menu_table(
        getattr(args, "region", None) or profile.region, data_dir=args.data_dir
    )


def cmd_menu(profile: Profile, args: argparse.Namespace) -> foods.MenuTotals | dict:
    items = [foods.parse_item(item) for item in args.item]
    totals = foods.menu_totals(items, _menu_table(profile, args))
    if not args.targets:
        return totals
    return _menu_day(totals, cmd_macros(profile, args))


def _in_data_dir(args: argparse.Namespace, path: Path) -> Path:
    """A relative path names a file in the data dir."""
    return path if path.is_absolute() else args.data_dir / path


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
    taste_flags = mealplan.taste_flags(
        days, tastes.load_tastes(args.data_dir / "tastes.yaml"), table
    )
    blocking = [f for f in taste_flags if f["blocking"]]
    checked = []
    for day in days:
        totals = foods.menu_totals(day.items, table)
        checked.append(_menu_day(totals, targets, day.share))
        if day.free_meals:
            checked[-1]["free_meal"] = _free_meal(day, totals, targets)
    repeats = mealplan.repeats(days)
    ok = not repeats and not blocking and all(c["ok"] for c in checked)
    result = {
        "ok": ok,
        "repeats": repeats,
        "taste_flags": taste_flags,
        "targets": targets,
        "days": [
            {"date": day.date, "dishes": day.dishes, "meals": _meals(day)}
            | {k: c[k] for k in ("totals", "check", "ok", "free_meal") if k in c}
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
        "pdf": out.relative_to(args.data_dir).as_posix()
        if out.is_relative_to(args.data_dir)
        else str(out),
        "menu": path.relative_to(args.data_dir).as_posix()
        if path.is_relative_to(args.data_dir)
        else str(path),
        "days": len(days),
        "qr": not args.no_qr,
    }


def cmd_shopping(profile: Profile, args: argparse.Namespace) -> dict:
    path = _saved_menu(args)
    _, days = mealplan.load_draft(path)
    pantry = tastes.load_tastes(args.data_dir / "tastes.yaml").pantry or []
    listed = mealplan.shopping(days, _menu_table(profile, args), profile.language, pantry)
    return {
        "menu": path.relative_to(args.data_dir).as_posix()
        if path.is_relative_to(args.data_dir)
        else str(path),
        "days": len(days),
        **listed,
        "note": "amounts are for the form each name gives (raw, cooked, drained); a batch is "
        "bought once at its servings, `left_over` of them are for other days or the freezer",
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
]
_PROFILE_TYPES = {
    "birth_date": date.fromisoformat,
    "height_cm": float,
    "weight_kg": float,
    "research_reminder_months": int,
}


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
        if kind is int:
            if not raw.isdigit():
                raise ValueError(f"{field} must be a whole number, not {raw!r}")
            return int(raw)
        return raw
    if field == "injuries":
        raise ValueError("injuries are set with `coach injury add` and `coach injury clear`")
    if field == "region":
        if raw.lower() == "none":
            return None  # no region: the base food table only
        if not (regions.ROOT / "regions" / raw / "region.yaml").exists():
            raise ValueError(
                f"there is no region {raw!r} yet (no regions/{raw}/region.yaml): leave the region "
                "unset, which uses the base food table, or add one as docs/adding-a-region.md says"
            )
    if field in ("medications", "conditions"):
        return [item.strip() for item in raw.split(",") if item.strip()]
    if field not in Profile.__dataclass_fields__:
        raise ValueError(f"unknown profile field {field!r}")
    try:
        return _PROFILE_TYPES.get(field, str)(raw)
    except ValueError:
        raise ValueError(f"{field}: {raw!r} is not valid") from None


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
        else:
            setattr(profile, args.field, value)
        save_profile(profile, args.data_dir / "profile.yaml")  # validates enums and screening
    return {
        "data_dir": str(args.data_dir.resolve()),  # skills read and write files here by path
        "profile": profile,
        "missing": [f for f in PROFILE_REQUIRED if getattr(profile, f) is None],
        "unrecognised": {
            "medications": [m for m in profile.medications if m not in MEDICATION_TOKENS],
            "conditions": [c for c in profile.conditions if c not in CONDITION_TOKENS],
        },
    }


def _find_injury(profile: Profile, area: str) -> dict | None:
    return next((i for i in profile.injuries if fold(i["area"]) == fold(area)), None)


def cmd_injury(profile: Profile, args: argparse.Namespace) -> dict:
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
    muscle_map = strength.load_muscle_map()
    listed = [e for i in profile.active_injuries() for e in i.get("exercises", [])]
    unmatched = [
        e for e in listed if not any(strength.named_in(x, [e], muscle_map) for x in logged)
    ]
    return {"injuries": profile.injuries, "unmatched": unmatched}


def cmd_tastes(profile: Profile, args: argparse.Namespace) -> dict:
    path = args.data_dir / "tastes.yaml"
    current = tastes.load_tastes(path)
    if args.tastes_cmd == "set":
        setattr(current, args.field, tastes.parse_value(args.field, args.value))
        tastes.save_tastes(current, path)  # validates
    elif args.tastes_cmd == "rate":
        when = args.today or date.today()
        current.rate(tastes.Rating(args.dish.strip(), args.rating, when, args.source, args.note))
        tastes.save_tastes(current, path)
        # a dish the client likes joins the recipe library (data/recipes/)
        saved = (
            recipes.save(args.data_dir, args.dish, args.source.strip(), when)
            if args.rating in recipes.SAVED_RATINGS
            else None
        )
        return _tastes_view(current) | {"recipe_saved": saved}
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


def cmd_checkin(profile: Profile, args: argparse.Namespace) -> Checkin:
    flags = safety.flags(profile, args.today)
    refused = ["weight"] if flags.no_weight_targets and args.weight is not None else []
    if safety.eating_disorder_positive(profile) or flags.no_calorie_targets:
        # Judgment call: after a positive screen or under 18, waist and calorie logs are body and
        # intake tracking too (pregnancy refuses weigh-ins only).
        refused += [name for name in ("waist", "intake") if getattr(args, name) is not None]
    if refused:
        reason = safety.weight_block_reason(flags)
        raise ValueError(f"{reason}; {', '.join(refused)} not recorded")
    checkin = Checkin(
        date=args.date or args.today or date.today(),
        weight_kg=args.weight,
        waist_cm=args.waist,
        intake_kcal=args.intake,
        sleep_hours=args.sleep,
        notes=args.notes,
    )
    append_checkin(checkin, args.data_dir / "checkins.csv")
    return checkin


def cmd_foods(profile: Profile, args: argparse.Namespace) -> dict:
    region = args.region or profile.region

    words = [fold(w) for w in args.words if w.strip()]
    if not words:
        raise ValueError("foods search needs at least one word")

    def hit(*names: str) -> bool:
        # Each search word must start a word of the names ("pollo" finds "pechuga de pollo",
        # not "repollo").
        found = re.findall(r"\w+", fold(" ".join(names)))
        return all(any(f.startswith(w) for f in found) for w in words)

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


def cmd_products(profile: Profile, args: argparse.Namespace) -> dict:
    if args.products_cmd == "list":
        return {"products": [_catalogue_entry(p) for p in catalogue.load(args.data_dir)]}
    if args.products_cmd == "search":
        hits = off.search(args.words, args.brand, args.limit, profile.language or "es")
        return {"source": catalogue.SOURCE, "hits": hits}
    found = off.product(args.barcode)
    if found is None:
        raise ValueError(f"{args.barcode} is not in Open Food Facts; check the barcode on the pack")
    name = " ".join((args.name or found["name"] or "").split())
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
    if any(p.barcode == args.barcode for p in products) and not args.replace:
        raise ValueError(f"{args.barcode} is already in the catalogue: add --replace to refresh it")
    others = [p for p in products if p.barcode != args.barcode]
    table = regions.menu_table(profile.region) + [p.as_food() for p in others]
    if foods.find(name, table) is not None:
        raise ValueError(f"{name!r} is already a food or product name: choose one with --name")
    product = catalogue.CatalogueProduct(
        barcode=args.barcode,
        product_name=name,
        brand=found["brand"] or "",
        chain=" ".join(args.chain.split()),
        per=per,
        **found["values"],
        allergens=tuple(found["allergens"]),
        url=found["url"],
        fetched_on=args.today or date.today(),
    )
    catalogue.save([*others, product], args.data_dir)
    warnings = []
    if None not in (product.kcal, product.protein_g, product.carbs_g, product.fat_g):
        gap = foods.energy_exception(product.to_row())
        if gap:
            warnings.append(f"label kcal is {gap}; check the pack")
    return {"added": product, "missing": product.missing(), "warnings": warnings}


def cmd_knowledge(profile: Profile, args: argparse.Namespace) -> dict | str:
    if args.knowledge_cmd == "section":
        return knowledge.section(args.file, args.heading)
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
    zones_cmd.add_argument("--hr-rest", type=int, default=None)
    zones_cmd.add_argument("--hr-max", type=int, default=None)
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

    import_cmd = add("import", cmd_import, "import a workout export into data/sessions.csv")
    import_cmd.add_argument("path", type=Path)
    import_cmd.add_argument("--importer", default=None, help="default: detect from the header")

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
        "products", cmd_products, "Open Food Facts products in data/catalogue.csv (unverified)"
    )
    products_sub = products_cmd.add_subparsers(dest="products_cmd", required=True)
    off_search = products_sub.add_parser("search", parents=[json_flag], help="WORD [WORD...]")
    off_search.add_argument("words", nargs="+")
    off_search.add_argument("--brand", default=None, help='e.g. "Hacendado"')
    off_search.add_argument("--limit", type=int, default=off.SEARCH_LIMIT)
    off_add = products_sub.add_parser("add", parents=[json_flag], help="BARCODE --chain CHAIN")
    off_add.add_argument("barcode")
    off_add.add_argument("--chain", required=True, help="the supermarket the client buys it at")
    off_add.add_argument("--name", default=None, help="default: the Open Food Facts name")
    off_add.add_argument("--per", default=None, choices=sorted(off.UNITS.values()))
    off_add.add_argument(
        "--confirm-per",
        action="store_true",
        help="keep --per although the pack unit says otherwise (after reading the label)",
    )
    off_add.add_argument("--replace", action="store_true", help="refresh a product already added")
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
    tastes_set.add_argument("field", help=", ".join(tastes.ASKED))
    tastes_set.add_argument("value", help="lists comma-separated; none for an empty answer")
    rate_cmd = tastes_sub.add_parser("rate", parents=[json_flag], help="DISH RATING")
    rate_cmd.add_argument("dish")
    rate_cmd.add_argument("rating", choices=tastes.RATINGS)
    rate_cmd.add_argument("--source", default="", help="the recipe or video link")
    rate_cmd.add_argument("--note", default="")

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

    knowledge_cmd = add("knowledge", cmd_knowledge, "knowledge staleness and sections")
    knowledge_sub = knowledge_cmd.add_subparsers(dest="knowledge_cmd", required=True)
    stale_cmd = knowledge_sub.add_parser("stale", parents=[json_flag])
    stale_cmd.add_argument("--months", type=int, default=None)
    section_cmd = knowledge_sub.add_parser("section", parents=[json_flag])
    section_cmd.add_argument("file")
    section_cmd.add_argument("heading")
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
