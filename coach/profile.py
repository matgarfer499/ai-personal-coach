"""The client's profile: data/profile.yaml.

A profile may be partial (/setup saves as it goes). Calculators call `profile.require(field)` and
raise `ProfileIncomplete` naming the missing field; skills ask for it instead of guessing.

`medications` and `conditions` hold free strings, but only the tokens below trigger anything in
the calculators. /setup maps the client's answers onto these tokens; any other string is kept for
the record and ignored by the code.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field, fields
from datetime import date
from pathlib import Path

import yaml

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
# nutrition.md: "Activity multipliers (PAL)": desk work with little exercise; desk work with about
# 1 h of training most days; physically active job or daily exercise plus high daily movement.
ACTIVITY_LEVELS = ("desk", "desk_training", "active")
# The languages the skills, the deferral line and the PDF labels exist in.
LANGUAGES = ("es", "en")
# convention: input check, not coaching: emergency numbers are 2 to 6 digits (112, 911, 000).
EMERGENCY_NUMBER = re.compile(r"^\d{2,6}$")

# Tokens the calculators read.
BETA_BLOCKER = "beta_blocker"  # cardio-health.md: "Beta-blockers: no formula-based HR zones"
GLP1 = "glp1"  # GLP-1 agonist or tirzepatide; nutrition.md: "GLP-1 users: protein, training..."
MEDICATION_TOKENS = (BETA_BLOCKER, GLP1)
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
    "menstrual": str,  # one of MENSTRUAL_STATES
    "bp_systolic": int,  # latest seated resting reading, mmHg
    "bp_diastolic": int,
}
# The PAR-Q+ answers a vigorous-work review covers; changing one drops `vigorous_reviewed`.
PARQ_ANSWERS = ("parq_any_yes", "parq_followup_yes")
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
    "activity_level": ACTIVITY_LEVELS,
    "language": LANGUAGES,
}


# Field types for a hand-edited profile.yaml (bool is excluded where a number is expected,
# because YAML's `true` would otherwise pass as 1).
NUMBERS = ("height_cm", "weight_kg")
TYPES = {
    "birth_date": date,
    "research_reminder_months": int,
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
    activity_level: str | None = None
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
        if value is not None and (isinstance(value, bool) or not isinstance(value, int | float)):
            raise ValueError(f"{name} must be a number, not {value!r}")
    for name, kind in TYPES.items():
        value = data.get(name)
        if value is not None and (isinstance(value, bool) or not isinstance(value, kind)):
            hint = "a date YYYY-MM-DD, unquoted" if kind is date else kind.__name__
            raise ValueError(f"{name} must be {hint}, not {value!r}")
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
    if not 0 <= screening.get("scoff_yes_count", 0) <= SCOFF_ITEMS:
        raise ValueError(f"screening.scoff_yes_count must be 0 to {SCOFF_ITEMS}")
    if screening.get("menstrual", "normal") not in MENSTRUAL_STATES:
        raise ValueError(f"screening.menstrual must be one of {', '.join(MENSTRUAL_STATES)}")
    for injury in data.get("injuries") or []:
        _validate_injury(injury)
    number = data.get("emergency_number")
    if number is not None and not (isinstance(number, str) and EMERGENCY_NUMBER.match(number)):
        raise ValueError(f"emergency_number must be 2 to 6 digits, not {number!r}")


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
    _validate(data)
    return Profile(**data)


def save_profile(profile: Profile, path: Path) -> None:
    data = {k: v for k, v in asdict(profile).items() if v not in (None, [], {})}
    _validate(data)
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")
