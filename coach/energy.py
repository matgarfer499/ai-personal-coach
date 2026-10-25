"""Resting and total energy expenditure, and the daily calorie target.

Every result is a starting estimate (MSJ is about ±10% for most people) to be corrected from the
client's weight trend after 2-4 weeks (`trend.recalibrate_tdee`).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from coach.profile import GLP1, GOALS, WEIGHT_RELATED_CONDITION, Profile, ProfileIncomplete
from coach.safety import GLP1_RULE, SafetyFlags, calorie_block_reason

# nutrition.md: "Default RMR equation: Mifflin-St Jeor" (sex-specific form, [S819])
MSJ_WEIGHT, MSJ_HEIGHT, MSJ_AGE = 10.0, 6.25, 5.0
MSJ_SEX_CONSTANT = {"male": 5.0, "female": -161.0}

# nutrition.md: "Activity multipliers (PAL)": desk 1.4-1.5, desk + about 1 h training most days
# 1.6-1.75, physically active 1.7-1.9.
PAL_BANDS = {"desk": (1.4, 1.5), "desk_training": (1.6, 1.75), "active": (1.7, 1.9)}
# nutrition.md: "Activity multipliers (PAL)": never 1.2 for ambulatory adults (1.4 is the
# guideline's floor), not above about 2.0 for recreational gym-goers.
PAL_MIN, PAL_MAX = 1.4, 2.0

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
PAL_RULE = 'nutrition.md: "Activity multipliers (PAL)"'


def rmr_mifflin(profile: Profile, today: date | None = None) -> float:
    sex = profile.require("sex")
    return (
        MSJ_WEIGHT * profile.require("weight_kg")
        + MSJ_HEIGHT * profile.require("height_cm")
        - MSJ_AGE * profile.age(today)
        + MSJ_SEX_CONSTANT[sex]
    )


def pal(profile: Profile) -> float:
    """Midpoint of the client's activity band (convention: band midpoint as the point estimate)."""
    low, high = PAL_BANDS[profile.require("activity_level")]
    return (low + high) / 2


def tdee(profile: Profile, multiplier: float | None = None, today: date | None = None) -> float:
    if multiplier is None:
        multiplier = pal(profile)
    elif multiplier < PAL_MIN:
        raise ValueError(
            f"PAL {multiplier} is too low: never 1.2 for ambulatory adults, use at least "
            f"{PAL_MIN} ({PAL_RULE})"
        )
    elif multiplier > PAL_MAX:
        raise ValueError(
            f"PAL {multiplier} is too high: not above about {PAL_MAX} for recreational "
            f"gym-goers ({PAL_RULE})"
        )
    return rmr_mifflin(profile, today) * multiplier


@dataclass
class Target:
    kcal: int
    maintenance: float
    deficit: int  # kcal below maintenance; negative for a surplus
    clamped: bool = False
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


def calorie_target(
    profile: Profile,
    flags: SafetyFlags,
    goal: str | None = None,
    today: date | None = None,
    tdee_kcal: float | None = None,
    current_kcal: float | None = None,
    recalibrated: bool = False,
) -> Target:
    """Daily calorie target.

    `tdee_kcal` replaces the estimate (an explicit PAL, or the trend's recalibrated TDEE).
    `current_kcal` is what the client eats now; with `hold_deficit` the target never goes below it.
    `recalibrated` marks `tdee_kcal` as the trend's TDEE: then a cut from `current_kcal` is
    limited to one step.
    """
    if flags.no_calorie_targets:
        raise ValueError(calorie_block_reason(flags))
    goal = goal or profile.require("goal")
    if goal not in GOALS:
        raise ValueError(f"goal must be one of {', '.join(GOALS)}, not {goal!r}")
    maintenance = tdee_kcal if tdee_kcal is not None else tdee(profile, today=today)
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
        # A surplus aims at weight gain, which is a weight target: blocked by the same flags.
        if not (flags.prescriber_owns_weight or flags.no_weight_targets):
            adjustment = maintenance * SURPLUS_FRACTION
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
        deficit=round(maintenance) - kcal,
        clamped=clamped,
        notes=notes,
    )


def floor_note(sex: str) -> str:
    return (
        f"{FLOOR_RULE}: raised to the {FLOOR_KCAL[sex]:,} kcal floor; going lower needs "
        "clinical supervision"
    )
