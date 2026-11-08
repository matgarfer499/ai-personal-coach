"""Daily protein, fat, carbohydrate and fibre targets for a calorie target."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date

from coach import safety
from coach.energy import FLOOR_KCAL, OBESITY_BMI, OLDER_ADULT_AGE, floor_note
from coach.profile import GLP1, Profile

# nutrition.md: "EU label rules and tolerances": 4 kcal/g protein and carbohydrate, 9 fat.
KCAL_PER_G = {"protein": 4, "carbs": 4, "fat": 9}

# Protein in g/kg/day.
# nutrition.md: "Daily protein target for people who lift": default 1.6 (range 1.4-2.2).
PROTEIN_DEFAULT = 1.6
PROTEIN_RANGE = (1.4, 2.2)
# convention: where a rule gives a range with no default, the coach uses its midpoint.
# nutrition.md: "Protein during fat loss": 1.6-2.2 for ordinary lifters; the coach's default band
# of 1.8-2.2 is the rule's own labelled convention.
PROTEIN_DEFICIT = (1.8, 2.2)
PROTEIN_DEFICIT_RANGE = (1.6, 2.2)
# nutrition.md: "Older adults: protein targets": 1.2-1.6 for older adults who lift.
PROTEIN_OLDER = (1.2, 1.6)
# nutrition.md: "GLP-1 users: protein, training and red flags": 1.2-1.6.
PROTEIN_GLP1 = (1.2, 1.6)
# convention: "Protein during fat loss" says to use fat-free mass or goal weight for clients with
# more body fat, and "Daily protein target for people who lift" says so for obesity. The coach
# knows neither, so it caps the weight protein is based on at the weight for a reference BMI for
# the client's height: BMI 25 in a deficit, BMI 30 (energy.OBESITY_BMI) otherwise. A cap, not a
# switch, so protein never jumps at a BMI boundary. For an overweight beginner in a deficit it
# lands near "about 1.6-2.0 g/kg" of body weight, the rule's own figure for them.
REFERENCE_BMI = 25.0

# nutrition.md: "Minimum dietary fat": at least about 20% of energy and 0.5 g/kg; default 20-35%.
# convention: the coach starts at 25%, the lower half of the default range.
FAT_FRACTION = 0.25
FAT_MIN_FRACTION = 0.20
FAT_MIN_G_PER_KG = 0.5
# nutrition.md: "Dietary fibre": at least 25 g/day.
FIBRE_MIN_G = 25


@dataclass
class Macros:
    kcal: float  # the calorie target used (raised to the floor if needed)
    protein_g: float
    fat_g: float
    fat_min_g: float  # "Minimum dietary fat": a menu below this is too low in fat
    carbs_g: float
    fibre_g: float  # a floor: at least this much
    protein_g_per_kg: float  # the rule's dose, per kg of the weight the protein is based on
    protein_g_per_kg_body: float = 0.0  # the same protein per kg of body weight
    protein_min_g: float = 0.0  # the rule's range in grams: a menu passes from the low end
    protein_max_g: float = 0.0
    notes: list[str] = field(default_factory=list)


def _midpoint(band: tuple[float, float]) -> float:
    return (band[0] + band[1]) / 2


def protein_band(
    profile: Profile, in_deficit: bool, today: date | None = None
) -> tuple[float, tuple[float, float], str]:
    """The dose in g/kg, the rule's range and the rule's heading."""
    if profile.has_medication(GLP1):
        return _midpoint(PROTEIN_GLP1), PROTEIN_GLP1, "GLP-1 users: protein, training and red flags"
    if profile.age(today) >= OLDER_ADULT_AGE:
        return _midpoint(PROTEIN_OLDER), PROTEIN_OLDER, "Older adults: protein targets"
    if in_deficit:
        return _midpoint(PROTEIN_DEFICIT), PROTEIN_DEFICIT_RANGE, "Protein during fat loss"
    return PROTEIN_DEFAULT, PROTEIN_RANGE, "Daily protein target for people who lift"


def macro_targets(
    profile: Profile,
    kcal: float,
    in_deficit: bool = False,
    today: date | None = None,
) -> Macros:
    """Macros for `kcal`. The calorie floor and the no-deficit flags apply here too, so a kcal
    figure typed in by hand cannot get round them."""
    weight = profile.require("weight_kg")
    sex = profile.require("sex")
    notes = []
    if kcal < FLOOR_KCAL[sex]:
        kcal = FLOOR_KCAL[sex]
        notes.append(floor_note(sex))
    flags = safety.flags(profile, today)
    if flags.no_calorie_targets:
        raise ValueError(safety.calorie_block_reason(flags))
    if in_deficit and (flags.no_deficit or flags.prescriber_owns_weight):
        in_deficit = False
        notes += flags.reasons
    per_kg, band, rule = protein_band(profile, in_deficit, today)
    notes.append(f'nutrition.md: "{rule}": {per_kg:g} g/kg/day')
    cap_bmi = REFERENCE_BMI if in_deficit else OBESITY_BMI
    protein_weight = min(weight, cap_bmi * (profile.require("height_cm") / 100) ** 2)
    protein_g = per_kg * protein_weight
    if protein_weight < weight:
        notes.append(
            f"convention: protein from {protein_weight:.0f} kg, the weight at BMI "
            f"{cap_bmi:g} for this height, instead of body weight: "
            f"{protein_g / weight:.2f} g per kg of body weight"
        )
    fat_min_g = max(kcal * FAT_MIN_FRACTION / KCAL_PER_G["fat"], FAT_MIN_G_PER_KG * weight)
    fat_g = max(kcal * FAT_FRACTION / KCAL_PER_G["fat"], fat_min_g)
    carbs_kcal = kcal - protein_g * KCAL_PER_G["protein"] - fat_g * KCAL_PER_G["fat"]
    if carbs_kcal < 0:
        notes.append("protein and fat minimums already exceed the calorie target; carbs set to 0")
        carbs_kcal = 0.0
    return Macros(
        kcal=kcal,
        protein_g=protein_g,
        fat_g=fat_g,
        fat_min_g=fat_min_g,
        carbs_g=carbs_kcal / KCAL_PER_G["carbs"],
        fibre_g=FIBRE_MIN_G,
        protein_g_per_kg=per_kg,
        protein_g_per_kg_body=protein_g / weight,
        protein_min_g=band[0] * protein_weight,
        protein_max_g=band[1] * protein_weight,
        notes=notes,
    )
