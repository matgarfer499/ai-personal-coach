"""Resting and total energy expenditure, and the daily calorie target.

Every result is a starting estimate (MSJ is about ±10% for most people) to be corrected from the
client's weight trend after 2-4 weeks (`trend.recalibrate_tdee`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from coach.profile import (
    GLP1,
    GOALS,
    PAL_RULE,
    WEIGHT_RELATED_CONDITION,
    Profile,
    ProfileIncomplete,
    check_pal,
)
from coach.safety import GLP1_RULE, SafetyFlags, calorie_block_reason
from coach.safety import flags as safety_flags

# nutrition.md: "Default RMR equation: Mifflin-St Jeor" (sex-specific form, [S819])
MSJ_WEIGHT, MSJ_HEIGHT, MSJ_AGE = 10.0, 6.25, 5.0
MSJ_SEX_CONSTANT = {"male": 5.0, "female": -161.0}

# nutrition.md: "Activity multipliers (PAL)": desk 1.4-1.5, desk + about 1 h training most days
# 1.6-1.75, physically active 1.7-1.9.
PAL_BANDS = {"desk": (1.4, 1.5), "desk_training": (1.6, 1.75), "active": (1.7, 1.9)}
# PAL_MIN, PAL_MAX and check_pal (profile.py): nutrition.md "Activity multipliers (PAL)" limits.

# nutrition.md: "Deficit size for weight loss (overweight and obesity)" (500-750 kcal) and
# "Deficit size when keeping or building muscle" (at or below about 500): every coach client
# lifts, so the coach uses 500.
DEFICIT_KCAL = 500
# nutrition.md: "Surplus size for muscle gain": 5-20% above maintenance; start at the lower end.
SURPLUS_FRACTION = 0.05
# nutrition.md: "Recalibrate TDEE from the weight trend": adjust intake in steps of about
# 100-200 kcal/d. Only cuts are stepped (judgment call: eating more is the cautious direction).
RECALIBRATE_STEP_KCAL = 200
# nutrition.md: "Low- and very-low-calorie diets need clinical supervision"
FLOOR_KCAL = {"female": 1200, "male": 1500}
# nutrition.md: "GLP-1 users: protein, training and red flags": the advisory's micronutrient
# flag (a separate threshold from the general floor above).
GLP1_LOW_INTAKE_KCAL = {"female": 1200, "male": 1800}
# nutrition.md: "Resistance training during any diet, especially for older adults": about 65+.
OLDER_ADULT_AGE = 65
# nutrition.md: "Overweight and obesity: equation choice" treats obesity as BMI 30 or more.
OBESITY_BMI = 30.0

FLOOR_RULE = 'nutrition.md: "Low- and very-low-calorie diets need clinical supervision"'
OLDER_RULE = 'nutrition.md: "Resistance training during any diet, especially for older adults"'
RECALIBRATE_RULE = 'nutrition.md: "Recalibrate TDEE from the weight trend"'


def rmr_mifflin(profile: Profile, today: date | None = None) -> float:
    sex = profile.require("sex")
    return (
        MSJ_WEIGHT * profile.require("weight_kg")
        + MSJ_HEIGHT * profile.require("height_cm")
        - MSJ_AGE * profile.age(today)
        + MSJ_SEX_CONSTANT[sex]
    )


# nutrition.md: "Default RMR equation: Mifflin-St Jeor": a starting guess with about ±10% error.
MSJ_ERROR = 0.10


def rmr_range(profile: Profile, today: date | None = None) -> tuple[float, float]:
    rmr = rmr_mifflin(profile, today)
    return rmr * (1 - MSJ_ERROR), rmr * (1 + MSJ_ERROR)


def tdee_range(
    profile: Profile,
    today: date | None = None,
    no_training: bool = False,
    multiplier: float | None = None,
) -> tuple[float, float]:
    """The RMR range times the PAL `tdee` used: a chosen multiplier (`--pal` or the stored
    `pal_override`) or the client's band (nutrition.md "Activity multipliers (PAL)")."""
    low, high = rmr_range(profile, today)
    if multiplier is None and pal_override_applies(profile, no_training):
        multiplier = profile.pal_override
    if multiplier is not None:
        return low * multiplier, high * multiplier
    band = PAL_BANDS[_level(profile, training=not no_training)]
    return low * band[0], high * band[1]


def band_midpoint(level: str) -> float:
    """Convention: the band midpoint as the point estimate."""
    low, high = PAL_BANDS[level]
    return (low + high) / 2


# nutrition.md: "Activity multipliers (PAL)" desk band, which applies once exercise has stopped
# (no_training). convention: its midpoint is the pal_override the `active` note suggests.
DESK_PAL = band_midpoint("desk")


def pal_override_applies(profile: Profile, no_training: bool) -> bool:
    """A stored choice counts only under no_training and only for `active` (the note's case)."""
    return bool(no_training and profile.pal_override and profile.activity_level == "active")


def pal(profile: Profile, training: bool = True) -> float:
    """Midpoint of the client's activity band (convention: band midpoint as the point estimate).

    Without training (`no_training` flag) desk_training drops to the desk band: desk work with
    little exercise (PAL_RULE). `active` stays: it may come from the job.
    """
    return band_midpoint(_level(profile, training))


def _level(profile: Profile, training: bool = True) -> str:
    level = profile.require("activity_level")
    return "desk" if not training and level == "desk_training" else level


def tdee(
    profile: Profile,
    multiplier: float | None = None,
    today: date | None = None,
    no_training: bool | None = None,
) -> float:
    """`no_training`: the safety flag; callers holding the flags pass it, else it is computed."""
    if multiplier is None:
        if no_training is None:
            no_training = safety_flags(profile, today).no_training
        if pal_override_applies(profile, no_training):
            multiplier = profile.pal_override
        else:
            multiplier = pal(profile, training=not no_training)
    check_pal(multiplier)
    return rmr_mifflin(profile, today) * multiplier


@dataclass
class Target:
    kcal: int
    maintenance: float
    deficit: int  # kcal below maintenance (0 for a surplus)
    clamped: bool = False
    surplus: int = 0  # kcal above maintenance
    notes: list[str] = field(default_factory=list)


def deficit_blockers(profile: Profile, flags: SafetyFlags, today: date | None) -> list[str]:
    """Reasons that forbid a deficit (empty list: a deficit is allowed)."""
    if not flags.screened:
        raise ProfileIncomplete("screening.scoff_yes_count")
    if flags.no_deficit or flags.prescriber_owns_weight:
        return list(flags.reasons)
    if profile.age(today) >= OLDER_ADULT_AGE and not (
        profile.bmi() >= OBESITY_BMI and profile.has_condition(WEIGHT_RELATED_CONDITION)
    ):
        return [
            f"{OLDER_RULE}: no deficit for adults about {OLDER_ADULT_AGE}+ unless they have "
            "obesity with a weight-related health problem"
        ]
    return []


def surplus_blocked(flags: SafetyFlags) -> bool:
    """A surplus aims at weight gain, a weight target: blocked by the same flags; a training stop
    holds maintenance too (safety.NO_TRAINING_NO_DEFICIT)."""
    return flags.prescriber_owns_weight or flags.no_weight_targets or flags.no_training


def calorie_target(
    profile: Profile,
    flags: SafetyFlags,
    goal: str | None = None,
    today: date | None = None,
    tdee_kcal: float | None = None,
    current_kcal: float | None = None,
    recalibrated: bool = False,
    estimate_chosen: bool = False,
) -> Target:
    """Daily calorie target.

    `tdee_kcal` replaces the estimate (the CLI's estimate, with or without an explicit PAL or a
    stored `pal_override`, or the trend's recalibrated TDEE); `None` means the default `tdee`.
    `current_kcal` is what the client eats now; with `hold_deficit` the target never goes below it.
    `recalibrated` marks `tdee_kcal` as the trend's TDEE: then a cut from `current_kcal` is
    limited to one step. `estimate_chosen` covers `--pal` and `--tdee` only (the client picked the
    estimate, so the `active` no_training note is skipped); a stored `pal_override` that applies
    also silences that note but is always announced by a note of its own.
    """
    if flags.no_calorie_targets:
        raise ValueError(calorie_block_reason(flags))
    goal = goal or profile.require("goal")
    if goal not in GOALS:
        raise ValueError(f"goal must be one of {', '.join(GOALS)}, not {goal!r}")
    maintenance = (
        tdee_kcal
        if tdee_kcal is not None
        else tdee(profile, today=today, no_training=flags.no_training)
    )
    if recalibrated:
        notes = [f"{RECALIBRATE_RULE}: maintenance from the weight trend; re-check in 2-4 weeks"]
    elif flags.no_weight_targets:  # no weigh-ins, so no trend to recalibrate from
        notes = [f"{RECALIBRATE_RULE}: starting estimate from an equation"]
    else:
        notes = [f"{RECALIBRATE_RULE}: starting estimate, recalibrate after 2-4 weeks of weigh-ins"]
    adjustment = 0.0

    if goal == "fat_loss":
        blockers = deficit_blockers(profile, flags, today)
        if blockers:
            notes += blockers
        elif flags.hold_deficit:
            # nutrition.md: "Menstrual dysfunction: stop and refer": stop increasing the deficit,
            # so never start one and never go below current intake.
            if current_kcal is not None:
                adjustment = min(0.0, current_kcal - maintenance)
            else:
                notes.append("current intake unknown: holding at maintenance")
        else:
            adjustment = -DEFICIT_KCAL
    elif goal == "muscle_gain":
        if not surplus_blocked(flags):
            adjustment = maintenance * SURPLUS_FRACTION
    stored = pal_override_applies(profile, flags.no_training) and not estimate_chosen
    if stored:
        notes.append(
            f"using stored pal_override {profile.pal_override:g} (set while training was on "
            "hold): if the hold is over or your activity changed, run "
            "`coach profile set pal_override none`"
        )
    elif (
        flags.no_training
        and not estimate_chosen
        and profile.activity_level == "active"
        and not profile.pal_override
    ):
        notes.append(
            f"{PAL_RULE}: activity level 'active' is kept while training is on hold: if it comes "
            "from the job, no change is needed; if it comes from exercise (stopped while "
            f"training is on hold), set it with `coach profile set pal_override {DESK_PAL:g}`; "
            "the coach cannot model a mix of both yet, so make no change"
        )
    notes += [r for r in flags.reasons if r not in notes]

    kcal = round(maintenance + adjustment)
    sex = profile.require("sex")
    if recalibrated and current_kcal is not None and kcal < current_kcal - RECALIBRATE_STEP_KCAL:
        full = max(kcal, FLOOR_KCAL[sex])
        notes.append(
            f"{RECALIBRATE_RULE}: one step of {RECALIBRATE_STEP_KCAL} kcal down from the current "
            f"{round(current_kcal)} kcal; the full target is {full:,} kcal"
        )
        kcal = round(current_kcal) - RECALIBRATE_STEP_KCAL
    clamped = kcal < FLOOR_KCAL[sex]
    if clamped:
        kcal = FLOOR_KCAL[sex]
        notes.append(floor_note(sex))
    if profile.has_medication(GLP1) and kcal < GLP1_LOW_INTAKE_KCAL[sex]:
        notes.append(
            f"{GLP1_RULE}: below {GLP1_LOW_INTAKE_KCAL[sex]:,} kcal, favour nutrient-dense "
            "foods and discuss supplements and monitoring with the prescriber"
        )
    return Target(
        kcal=kcal,
        maintenance=maintenance,
        deficit=max(0, round(maintenance) - kcal),
        surplus=max(0, kcal - round(maintenance)),
        clamped=clamped,
        notes=notes,
    )


def floor_note(sex: str) -> str:
    return (
        f"{FLOOR_RULE}: raised to the {FLOOR_KCAL[sex]:,} kcal floor; going lower needs "
        "clinical supervision"
    )
