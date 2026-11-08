"""The client's profile: data/profile.yaml.

A profile may be partial (/setup saves as it goes). Calculators call `profile.require(field)` and
raise `ProfileIncomplete` naming the missing field; skills ask for it instead of guessing.

`medications` and `conditions` hold free strings, but only the tokens below trigger anything in
the calculators. /setup maps the client's answers onto these tokens; any other string is kept for
the record and ignored by the code.
"""

from __future__ import annotations

import math
import re
from dataclasses import asdict, dataclass, field, fields
from datetime import date
from pathlib import Path

import yaml

from coach.regioncode import NO_REGION, real_region

# Equations and calorie floors in the knowledge files are defined for female and male only
# (nutrition.md: "Default RMR equation: Mifflin-St Jeor"; "Low- and very-low-calorie diets need
# clinical supervision"), so the profile stores exactly that.
SEXES = ("female", "male")
GOALS = ("fat_loss", "maintenance", "muscle_gain", "recomposition")
# convention: no rule defines the three levels, so /setup uses months of consistent training (about
# 2 or more sessions a week, the twice-weekly programme of the novice rule). novice: under 12
# months; intermediate: 12 months or more and still adding load or reps most months; advanced: 12
# months or more and progress has slowed to a plateau. The 12 months come from the rules' own
# populations: strength-hypertrophy.md "Novice strength gains and plateau" (fast gains in the
# first year, slowing after 6-12 months) and "Trained lifters: 12-20 weekly sets" (applies to at
# least 1 year of training, for a lifter who has plateaued). Only `novice` changes what /plan
# loads ("Starting point for novices"); advanced adds the 12-20 weekly sets rule.
EXPERIENCE = ("novice", "intermediate", "advanced")
# nutrition.md: "Daily protein target for endurance runners": runners get their own protein rule,
# and runners who also lift follow the lifter rule. Unset means lifting (the coach's default).
SPORTS = ("lifting", "running", "both")
# nutrition.md: "Activity multipliers (PAL)": desk work with little exercise; desk work with about
# 1 h of training most days; physically active job or daily exercise plus high daily movement.
ACTIVITY_LEVELS = ("desk", "desk_training", "active")
# The languages the skills, the deferral line and the PDF labels exist in.
LANGUAGES = ("es", "en")
# convention: input check, not coaching: emergency numbers are 2 to 6 digits (112, 911, 000).
EMERGENCY_NUMBER = re.compile(r"^\d{2,6}$")
NO_NUMBER = "none"  # the client declined or has no number: `coach safety` prints none of its own

# Plausibility limits for typed-in heart rates (convention: input validation, not coaching).
HR_REST_RANGE = (30, 120)
HR_MAX_RANGE = (100, 230)

# Tokens the calculators read.
BETA_BLOCKER = "beta_blocker"  # cardio-health.md: "Beta-blockers: no formula-based HR zones"
# GLP-1 agonist or tirzepatide; nutrition.md: "GLP-1 users: protein, training and red flags"
GLP1 = "glp1"
# cardio-health.md: "Blood pressure medicines and exercise": any blood-pressure medicine; the coach
# never changes it, and it counts as known hypertension for the BP bands.
BP_MEDICATION = "bp_medication"
MEDICATION_TOKENS = (BETA_BLOCKER, GLP1, BP_MEDICATION)
PREGNANT = "pregnant"
PLANNING_PREGNANCY = "planning_pregnancy"
HYPERTENSION = "hypertension"  # read by skills (recovery-habits.md BP bands), not calculators
HEART_DISEASE = "heart_disease"
# nutrition.md: "Resistance training during any diet, especially for older adults": obesity with
# a weight-related health problem is the only case where an older adult gets a deficit.
WEIGHT_RELATED_CONDITION = "weight_related_condition"
CONDITION_TOKENS = (
    PREGNANT,
    PLANNING_PREGNANCY,
    HYPERTENSION,
    HEART_DISEASE,
    WEIGHT_RELATED_CONDITION,
)

# Screening outcomes (answers are stored as outcomes, never as question text).
SCREENING_KEYS = {
    "scoff_yes_count": int,  # clear yes answers to the five SCOFF-style questions, 0 to 5
    "scoff_positive": bool,  # a warning sign, positive whatever the count
    "parq_any_yes": bool,  # any YES on the PAR-Q+ 7 questions
    "parq_followup_yes": bool,  # any YES on the follow-up questions
    # recovery-habits.md: "PAR-Q+ specific thresholds": a qualified exercise professional or
    # clinician has reviewed vigorous or maximal work for this client.
    "vigorous_reviewed": bool,
    "cardiac_symptoms": bool,  # any symptom from "Cardiac warning symptoms: stop and refer"
    # recovery-habits.md: "ACSM 2015 screening algorithm" (the default entry screen): planned,
    # structured exercise of 30+ min at moderate intensity, 3+ days a week, for the last 3 months.
    "regular_exercise": bool,
    "known_disease": list,  # DISEASE_TOKENS diagnosed by a doctor; an empty list is none
    "symptoms": list,  # SYMPTOM_TOKENS reported at screening; an empty list is none
    "medically_cleared": bool,  # a clinician cleared exercise (`coach clearance add`)
    # recovery-habits.md: "Cardiac warning symptoms: stop and refer": training resumes only once a
    # clinician clears it; `coach clearance add` records who, when and what they said.
    "cleared_on": date,
    "cleared_by": str,
    "clearance_note": str,
    "symptoms_on": date,  # the latest day a warning symptom was reported
    "menstrual": str,  # one of MENSTRUAL_STATES
    "bp_systolic": int,  # latest seated resting reading, mmHg
    "bp_diastolic": int,
}
# The PAR-Q+ answers a vigorous-work review covers; changing one drops `vigorous_reviewed`.
PARQ_ANSWERS = ("parq_any_yes", "parq_followup_yes")
# The answers a medical clearance covers; changing one drops the clearance record.
CLEARANCE_ANSWERS = ("known_disease", "symptoms", "cardiac_symptoms")
# The clearance record: written only by `coach clearance add`, never by `profile set`.
CLEARANCE_RECORD = ("medically_cleared", "cleared_on", "cleared_by", "clearance_note")
# recovery-habits.md: "ACSM 2015 screening algorithm": the diseases that change the cell.
# Hypertension is not one of them (ACSM 2015 dropped risk-factor counting).
DISEASE_TOKENS = ("cardiovascular", "metabolic", "renal")
# recovery-habits.md: "Cardiac warning symptoms: stop and refer": the symptom tokens /setup and
# /checkin record, from the rule's list.
SYMPTOM_TOKENS = (
    "chest_pain",
    "neck_jaw_arm_pain",
    "breathless",
    "dizzy",
    "faint",
    "palpitations",
    "ankle_swelling",
    "calf_pain",
    "unusual_fatigue",
)
SCREENING_TOKENS = {"known_disease": DISEASE_TOKENS, "symptoms": SYMPTOM_TOKENS}
MENSTRUAL_STATES = ("normal", "irregular_new", "absent", "not_applicable")
# nutrition.md: "Eating-disorder screening: brief questions as a prompt": the five SCOFF questions.
SCOFF_ITEMS = 5

# Injuries: one record per injured area. While `active`, the logged exercises listed under
# `exercises` keep their load in `strength progress` (coach/safety.py says why).
INJURY_STATUSES = ("active", "cleared")
INJURY_KEYS = {
    "area": str,  # in the client's words, e.g. "right shoulder"
    "status": str,  # one of INJURY_STATUSES
    "since": date,
    "professional": str,  # who assessed it and manages it, e.g. "physiotherapist"
    "cleared_on": date,  # the date the professional cleared it; required once cleared
    "exercises": list,  # logged exercise names whose loads are paused while active
}

ENUMS = {
    "sex": SEXES,
    "goal": GOALS,
    "experience": EXPERIENCE,
    "sport": SPORTS,
    "activity_level": ACTIVITY_LEVELS,
    "language": LANGUAGES,
}


# Field types for a hand-edited profile.yaml (bool is excluded where a number is expected,
# because YAML's `true` would otherwise pass as 1).
# nutrition.md: "Activity multipliers (PAL)": never 1.2 for ambulatory adults (1.4 is the
# guideline's floor), not above about 2.0 for recreational gym-goers.
PAL_MIN, PAL_MAX = 1.4, 2.0
PAL_RULE = 'nutrition.md: "Activity multipliers (PAL)"'


def check_pal(value: float, label: str = "PAL") -> None:
    """The one range check for a PAL (an explicit --pal and the stored pal_override)."""
    if value < PAL_MIN:
        raise ValueError(
            f"{label} {value} is too low: never 1.2 for ambulatory adults, use at least "
            f"{PAL_MIN} ({PAL_RULE})"
        )
    if value > PAL_MAX:
        raise ValueError(
            f"{label} {value} is too high: not above about {PAL_MAX} for recreational "
            f"gym-goers ({PAL_RULE})"
        )


NUMBERS = ("height_cm", "weight_kg", "pal_override", "race_km")
TYPES = {
    "birth_date": date,
    "race_date": date,
    "research_reminder_months": int,
    "hr_max": int,
    "hr_rest": int,
    "language": str,
    "region": str,
    "medications": list,
    "conditions": list,
    "screening": dict,
    "injuries": list,
}


class ProfileIncomplete(Exception):
    def __init__(self, field: str):
        self.field = field
        super().__init__(f"profile is missing '{field}'")


@dataclass
class Profile:
    sex: str | None = None
    birth_date: date | None = None
    height_cm: float | None = None
    weight_kg: float | None = None
    goal: str | None = None
    experience: str | None = None
    sport: str | None = None  # one of SPORTS; unset behaves as lifting
    activity_level: str | None = None
    # The client's chosen PAL while no_training is set (ignored otherwise); see energy.tdee.
    pal_override: float | None = None
    # cardio-health.md: "HRmax: formulas and setting the anchor": an observed all-out peak and a
    # measured morning resting HR, used by `coach zones` instead of the formula.
    hr_max: int | None = None
    hr_rest: int | None = None
    # A goal race (cardio-health.md: "Taper before a goal race"): `coach runs taper` and
    # `coach runs plan` read it.
    race_date: date | None = None
    race_km: float | None = None
    language: str | None = None
    region: str | None = None
    emergency_number: str | None = None  # the client's own; else their region's (coach safety)
    medications: list[str] = field(default_factory=list)
    conditions: list[str] = field(default_factory=list)
    screening: dict = field(default_factory=dict)
    injuries: list[dict] = field(default_factory=list)
    # convention: chosen when the coach was designed (2026-10-24): remind after 6 months.
    research_reminder_months: int = 6

    def require(self, name: str):
        value = getattr(self, name)
        if value is None:
            raise ProfileIncomplete(name)
        return value

    def has_medication(self, token: str) -> bool:
        return token in self.medications

    def has_condition(self, token: str) -> bool:
        return token in self.conditions

    def active_injuries(self) -> list[dict]:
        return [i for i in self.injuries if i["status"] == "active"]

    def age(self, today: date | None = None) -> int:
        born = self.require("birth_date")
        today = today or date.today()
        return today.year - born.year - ((today.month, today.day) < (born.month, born.day))

    def bmi(self) -> float:
        height_m = self.require("height_cm") / 100
        return self.require("weight_kg") / height_m**2


def _validate(data: dict) -> None:
    known = {f.name for f in fields(Profile)}
    unknown = sorted(set(data) - known)
    if unknown:
        raise ValueError(f"unknown profile keys: {', '.join(unknown)}")
    for name in NUMBERS:
        value = data.get(name)
        bad = isinstance(value, bool) or not isinstance(value, int | float)
        if value is not None and (bad or not math.isfinite(value)):
            raise ValueError(f"{name} must be a number, not {value!r}")
    pal = data.get("pal_override")
    if pal is not None:
        check_pal(pal, "pal_override")
    for name, kind in TYPES.items():
        value = data.get(name)
        if value is not None and (isinstance(value, bool) or not isinstance(value, kind)):
            hint = "a date YYYY-MM-DD, unquoted" if kind is date else kind.__name__
            raise ValueError(f"{name} must be {hint}, not {value!r}")
    if data.get("race_km") is not None and not data["race_km"] > 0:
        raise ValueError(f"race_km must be above 0, not {data['race_km']!r}")
    for name, limits in (("hr_max", HR_MAX_RANGE), ("hr_rest", HR_REST_RANGE)):
        value = data.get(name)
        if value is not None and not limits[0] <= value <= limits[1]:
            raise ValueError(f"{name} {value} bpm is outside {limits[0]}-{limits[1]}")
    if data.get("hr_rest") is not None and data.get("hr_max") is not None:
        if data["hr_rest"] >= data["hr_max"]:
            raise ValueError(f"hr_rest {data['hr_rest']} must be below hr_max {data['hr_max']}")
    for name, allowed in ENUMS.items():
        if data.get(name) is not None and data[name] not in allowed:
            raise ValueError(f"{name} must be one of {', '.join(allowed)}, not {data[name]!r}")
    screening = data.get("screening") or {}
    for key, value in screening.items():
        if key not in SCREENING_KEYS:
            raise ValueError(f"unknown screening key: {key}")
        expected = SCREENING_KEYS[key]
        if not isinstance(value, expected) or (expected is int and isinstance(value, bool)):
            raise ValueError(f"screening.{key} must be {expected.__name__}")
        bad = [v for v in value if v not in SCREENING_TOKENS[key]] if expected is list else []
        if bad:
            raise ValueError(
                f"screening.{key}: unknown {', '.join(map(str, bad))}; use "
                f"{', '.join(SCREENING_TOKENS[key])} (no for none)"
            )
    if not 0 <= screening.get("scoff_yes_count", 0) <= SCOFF_ITEMS:
        raise ValueError(f"screening.scoff_yes_count must be 0 to {SCOFF_ITEMS}")
    if screening.get("menstrual", "normal") not in MENSTRUAL_STATES:
        raise ValueError(f"screening.menstrual must be one of {', '.join(MENSTRUAL_STATES)}")
    for injury in data.get("injuries") or []:
        _validate_injury(injury)
    if isinstance(data.get("region"), str):
        real_region(data["region"])  # raises for a path
    number = data.get("emergency_number")
    declined = number == NO_NUMBER
    if (
        number is not None
        and not declined
        and not (isinstance(number, str) and EMERGENCY_NUMBER.match(number))
    ):
        raise ValueError(f"emergency_number must be 2 to 6 digits or none, not {number!r}")


def _validate_injury(injury: object) -> None:
    if not isinstance(injury, dict):
        raise ValueError("each injury must hold field: value lines")
    unknown = sorted(set(injury) - set(INJURY_KEYS))
    if unknown:
        raise ValueError(f"unknown injury keys: {', '.join(unknown)}")
    for key, kind in INJURY_KEYS.items():
        value = injury.get(key)
        if value is not None and not isinstance(value, kind):
            hint = "a date YYYY-MM-DD, unquoted" if kind is date else kind.__name__
            raise ValueError(f"injury {key} must be {hint}, not {value!r}")
    if not (injury.get("area") or "").strip():
        raise ValueError("each injury needs an area")
    if injury.get("status") not in INJURY_STATUSES:
        raise ValueError(f"injury status must be one of {', '.join(INJURY_STATUSES)}")
    if injury["status"] == "cleared" and injury.get("cleared_on") is None:
        raise ValueError("a cleared injury needs cleared_on")
    since, cleared_on = injury.get("since"), injury.get("cleared_on")
    if since and cleared_on and cleared_on < since:
        raise ValueError("an injury's cleared_on cannot be before its since date")
    if not all(isinstance(e, str) for e in injury.get("exercises", [])):
        raise ValueError("injury exercises must be exercise names")


def load_profile(path: Path) -> Profile:
    path = Path(path)
    if not path.exists():
        return Profile()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as err:
        raise ValueError(f"{path.name} is not valid YAML: {err}") from None
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must hold field: value lines")
    # An empty `medications:` or `exercises:` line in a hand-edited file means an empty list.
    for name in ("medications", "conditions", "injuries", "screening"):
        if name in data and data[name] is None:
            del data[name]
    for injury in data.get("injuries") or []:
        if isinstance(injury, dict) and injury.get("exercises", []) is None:
            del injury["exercises"]
    if isinstance(data.get("region"), str):
        # A hand-edited `None` or `NONE` means no region; an empty string means unset.
        data["region"] = real_region(data["region"]) or (
            NO_REGION if data["region"].strip() else None
        )
        if data["region"] is None:
            del data["region"]
    number = data.get("emergency_number")
    if isinstance(number, str) and number.strip().lower() == NO_NUMBER:
        data["emergency_number"] = NO_NUMBER
    _validate(data)
    return Profile(**data)


def save_profile(profile: Profile, path: Path) -> None:
    data = {k: v for k, v in asdict(profile).items() if v not in (None, [], {})}
    _validate(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
