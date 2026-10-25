"""The client's taste profile: data/tastes.yaml.

/menu reads it on every run and asks only for the fields in `missing()`. A field that is absent
has not been asked yet; an empty list (or an empty postal code) means asked, with no answer.
Ratings record how the client liked a dish the coach offered.
"""

from __future__ import annotations

import re
from dataclasses import asdict, dataclass, field, fields
from datetime import date
from pathlib import Path

import yaml

from coach.text import fold

LIST_FIELDS = (
    "loved_foods",
    "disliked_foods",
    "allergies",
    "intolerances",
    "cuisines",
    "flavours",
    "equipment",
    "chains",  # any chain names: not limited to regions/<code>/region.yaml
    "pantry",  # foods always at home: /menu leaves them off the shopping list (optional)
    "untried",  # foods never tried: not a dislike; /menu offers them sparingly (optional)
)
# convention: three levels each, enough for /menu to pick recipe difficulty and ingredients.
COOKING_SKILLS = ("beginner", "intermediate", "advanced")
BUDGETS = ("low", "medium", "high")
# convention: /menu favours loved and liked dishes, offers disliked ones rarely and never_again
# ones never.
RATINGS = ("loved", "liked", "disliked", "never_again")
ENUMS = {"cooking_skill": COOKING_SKILLS, "budget": BUDGETS}
# convention: an input check, 3 to 10 letters, digits, spaces or hyphens (any country's format).
POSTAL_CODE = re.compile(r"[A-Za-z0-9 -]{3,10}")
# The fields /menu asks for, in this order.
ASKED = (
    "loved_foods",
    "disliked_foods",
    "allergies",
    "intolerances",
    "cuisines",
    "flavours",
    "cooking_minutes",
    "cooking_skill",
    "equipment",
    "budget",
    "postal_code",
    "chains",
)
# `coach tastes set` also takes the optional fields, which /menu never asks for.
SETTABLE = (*ASKED, "pantry", "untried")


# convention: words that only say a food is raw or fresh. The table's plain names ("tomate") are
# the raw food, so a phrase such as "tomate crudo" must still reach them (see `matches`).
RAW_WORDS = ("crudo", "fresco", "raw", "fresh")
# convention: words that carry no meaning of their own in a food name.
FILLER_WORDS = ("de", "del", "la", "el", "los", "las", "con", "en", "y", "a", "al")


def _forms(word: str) -> frozenset[str]:
    """The forms a folded Spanish or English word may take once plural and gender are removed:
    tomates is tomate or tomat, limones is limon, cruda is crud, so equal forms mean one word."""
    forms = {word}
    if len(word) > 4 and word.endswith("es"):
        forms.add(word[:-2])
    if len(word) > 3 and word.endswith("s"):
        forms.add(word[:-1])
    forms |= {f[:-1] for f in forms if len(f) > 3 and f[-1] in "ao"}
    return frozenset(forms)


def _words(text: str) -> list[frozenset[str]]:
    return [_forms(w) for w in re.findall(r"\w+", fold(text))]


def _has(words: list[frozenset[str]], wanted: frozenset[str]) -> bool:
    return any(word & wanted for word in words)


def matches(phrase: str, *names: str) -> bool:
    """Does a taste or pantry phrase name this food? Every word of the phrase must be a word of
    one of the names (plural or singular, either gender, case and accents ignored), in any order.

    So "tomate" matches "tomate" and "salsa de tomate"; "tomate crudo" matches "tomate, crudo" and
    the plain table name "tomate" (the raw food) but not "salsa de tomate", because a name with
    other words of its own is a different food. A phrase matches words, not parts of words:
    "pollo" does not match "repollo".

    A convention (docs/conventions.md): whole words, no synonyms, translations or categories
    ("lactosa" does not match "leche"), so a miss is never proof."""
    wanted = _words(phrase)
    if not wanted:
        return False
    raw = _words(" ".join(RAW_WORDS))
    core = [w for w in wanted if not _has(raw, w)]
    filler = _words(" ".join(FILLER_WORDS))
    for name in names:
        found = _words(name)
        if all(_has(found, w) for w in wanted):
            return True
        # "tomate crudo" reaches the unmarked name "tomate", never "salsa de tomate"
        content = [w for w in found if not _has(filler, w)]
        if core and len(core) < len(wanted) and content:
            if all(_has(core, word) for word in content):
                return True
    return False


@dataclass
class Rating:
    dish: str
    rating: str
    date: date
    source: str = ""
    note: str = ""


@dataclass
class Tastes:
    loved_foods: list[str] | None = None
    disliked_foods: list[str] | None = None
    allergies: list[str] | None = None
    intolerances: list[str] | None = None
    cuisines: list[str] | None = None
    flavours: list[str] | None = None
    cooking_minutes: int | None = None  # typical minutes per meal
    cooking_skill: str | None = None
    equipment: list[str] | None = None
    budget: str | None = None
    postal_code: str | None = None
    chains: list[str] | None = None
    pantry: list[str] | None = None  # optional: never asked, so not in `missing()`
    untried: list[str] | None = None  # optional, likewise
    ratings: list[Rating] = field(default_factory=list)

    def missing(self) -> list[str]:
        return [name for name in ASKED if getattr(self, name) is None]

    def dishes(self, *ratings: str) -> list[str]:
        """Rated dish names, in the order of `ratings` given."""
        return [r.dish for wanted in ratings for r in self.ratings if r.rating == wanted]

    def rate(self, rating: Rating) -> None:
        """A new rating of the same dish (case and accents ignored) replaces the earlier one."""
        self.ratings = [r for r in self.ratings if fold(r.dish) != fold(rating.dish)]
        self.ratings.append(rating)


def _check_value(name: str, value) -> None:
    if value is None:
        return
    if name in LIST_FIELDS:
        if not isinstance(value, list) or not all(isinstance(v, str) for v in value):
            raise ValueError(f"{name} must be a list of words, not {value!r}")
    elif name == "cooking_minutes":
        if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
            raise ValueError(f"cooking_minutes must be a whole number above 0, not {value!r}")
    elif name == "postal_code":
        if not isinstance(value, str) or (value and not POSTAL_CODE.fullmatch(value)):
            raise ValueError(f"postal_code must be 3 to 10 letters or digits, quoted: {value!r}")
    elif name in ENUMS and value not in ENUMS[name]:
        raise ValueError(f"{name} must be one of {', '.join(ENUMS[name])}, not {value!r}")


def _rating(entry) -> Rating:
    if not isinstance(entry, dict) or set(entry) - {f.name for f in fields(Rating)}:
        raise ValueError(f"each rating needs dish, rating, date (source, note): {entry!r}")
    if entry.get("rating") not in RATINGS:
        raise ValueError(f"rating must be one of {', '.join(RATINGS)}, not {entry.get('rating')!r}")
    if not isinstance(entry.get("dish"), str) or not entry["dish"].strip():
        raise ValueError(f"a rating needs the dish name: {entry!r}")
    if not isinstance(entry.get("date"), date):
        raise ValueError(f"a rating date must be YYYY-MM-DD, unquoted: {entry!r}")
    return Rating(**entry)


def load_tastes(path: Path) -> Tastes:
    path = Path(path)
    if not path.exists():
        return Tastes()
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as err:
        raise ValueError(f"{path.name} is not valid YAML: {err}") from None
    if not isinstance(data, dict):
        raise ValueError(f"{path.name} must hold field: value lines")
    unknown = sorted(set(data) - {f.name for f in fields(Tastes)})
    if unknown:
        raise ValueError(f"unknown tastes keys: {', '.join(unknown)}")
    for name, value in data.items():
        if name != "ratings":
            _check_value(name, value)
    ratings = data.pop("ratings", None) or []
    if not isinstance(ratings, list):
        raise ValueError("ratings must be a list")
    return Tastes(**data, ratings=[_rating(r) for r in ratings])


def save_tastes(tastes: Tastes, path: Path) -> None:
    for name in SETTABLE:
        _check_value(name, getattr(tastes, name))
    for rating in tastes.ratings:
        _rating(asdict(rating))
    data = {k: v for k, v in asdict(tastes).items() if v is not None and k != "ratings"}
    if tastes.ratings:
        data["ratings"] = [asdict(r) for r in tastes.ratings]
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")


def parse_value(name: str, raw: str):
    """A `coach tastes set` value: lists comma-separated, `none` for an empty answer."""
    if name == "ratings":
        raise ValueError("ratings are recorded with `coach tastes rate DISH RATING`")
    if name not in SETTABLE:
        raise ValueError(f"unknown tastes field {name!r}: {', '.join(SETTABLE)}")
    empty = raw.strip().lower() == "none"
    if name in LIST_FIELDS:
        return [] if empty else [item.strip() for item in raw.split(",") if item.strip()]
    if name == "postal_code":
        return "" if empty else raw.strip()
    if name == "cooking_minutes":
        if not raw.strip().isdigit():
            raise ValueError(f"cooking_minutes must be a whole number, not {raw!r}")
        return int(raw)
    return raw.strip()
