"""Content checks behind `coach plan check`: plan.md's nutrition, lifts, loads and modalities
against the CLI and the safety flags (beta 3: the check used to read only the header)."""

from __future__ import annotations

import re
from typing import Any

from coach import export, safety, strength
from coach.text import fold

# convention: the plan's kcal and carbohydrate may differ from `coach macros` by about 20%, the
# tolerance nutrition.md "EU label rules and tolerances" gives main nutrients on a label (a figure
# borrowed, not a rule about plans); protein, fat and fibre use the ranges `coach macros` prints.
NUTRITION_TOLERANCE = 0.20
# convention: whole-gram rounding when a plan writes a target as an integer.
ROUNDING_G = 0.5
# convention: a typo check, not coaching (as checkins.RANGES): a planned load above 300 kg with no
# logged history of that lift is questioned; with history the client's own e1RM is the limit.
LOAD_PLAUSIBLE_KG = 300.0

NUTRITION = ("nutricion", "nutrition")
# Words (folded) that name each number in the Nutrition section, es and en.
NUTRIENTS = {
    "kcal": ("calorias", "calories", "kcal", "energia", "energy"),
    "protein": ("proteina", "proteinas", "protein"),
    "fat": ("grasa", "grasas", "fat"),
    "carbs": ("carbohidratos", "hidratos", "carbohydrate", "carbohydrates", "carbs"),
    "fibre": ("fibra", "fibre", "fiber"),
}
# A whole number; "1,850" and "1.850" are thousands. Per-kg and % figures ("1.6 g/kg", "30% of
# energy") are not the day's grams, so the next number is read instead.
_NUMBER = re.compile(r"(?<![\d.,])(\d+(?:[.,]\d+)*)(?!\d|[.,]\d|\s*(?:%|g\s*/\s*kg))")
# convention: a Nutrition line lists its nutrients in parts split at ; or at a comma that is not a
# decimal or thousands one ("1648 kcal, proteina 131,22 g"); a nutrient's number is in its part,
# or in the next part when that names no nutrient ("protein: 1.6 g/kg, about 120 g").
_PARTS = re.compile(r";|,(?!\d)")
# The number just before the word, with only g and de/of between ("1648 kcal", "131 g de
# proteina", "141 g protein"); any other number before it ("3 meals with protein", "1650 kcal
# protein") is not its.
_BEFORE = re.compile(_NUMBER.pattern + r"\s*g?\s*(?:de|of)?\s*$")
# A word that is a label ("week 2 calories: 1850") or a per-kg unit ("1,6 g de proteina por kg")
# does not own the number before it.
_NOT_BEFORE = re.compile(r"\s*(?::|(?:/|per|por)\s*kg\b)")
# A number in the next part needs the nutrient's unit: "4 meals" is no protein, "200 g" no kcal.
_UNIT = {
    key: re.compile(_NUMBER.pattern + (r"\s*k?cal\b" if key == "kcal" else r"\s*g\b"))
    for key in NUTRIENTS
}
_DATE = re.compile(r"\d{4}-\d{2}-\d{2}")
_THOUSANDS = re.compile(r"\d{1,3}(?:[.,]\d{3})+")
_KG = re.compile(r"(\d+(?:[.,]\d+)?)\s*kg\b", re.I)
_KM = re.compile(r"(\d+(?:[.,]\d+)?)\s*km\b", re.I)

# convention: words for the formats the safety flags rule out, from plan/SKILL.md Safety and
# recovery-habits.md "PAR-Q+ specific thresholds" (HIIT, 1RM tests, all-out sprints; SIT, REHIT).
SPRINT_WORDS = (
    "rehit",
    "sprint",
    "sprints",
    "esprint",
    "esprints",
    "all out",
    "all-out",
    "wingate",
)
VIGOROUS_WORDS = ("hiit", "tabata", "1rm", "rm test", "max attempt", "intento maximo")
_SIT = re.compile(r"\bSIT\b")  # case-sensitive: "sit-ups" is not sprint interval training
# convention: a format named after a negation earlier in its sentence is a prohibition, not a
# prescription ("No vigorous work: no HIIT, sprints or 1RM tests"); sentences end at . ; ! ?
# or "but"/"pero" (a list's commas do not end the negation's reach).
PROHIBITIONS = (*safety.NEGATIONS, "avoid", "evita", "evitar")
# "no more than 4 sprints" / "no mas de 4" is a limit: it still prescribes the format.
_LIMIT = re.compile(r"\b(?:no|not)\s+(?:more|mas)\s+(?:than|de|que)\b")
_SENTENCE_END = re.compile(r"[.;!?]|\bpero\b|\bbut\b")
PRESCRIBING = (*export.TRAINING_WEEK, "cardio")


def _number(text: str) -> float:
    return float(text.replace(",", "."))


def _hit(part: str, words: tuple[str, ...]) -> re.Match | None:
    """The leftmost of `words` in `part`."""
    hits = (m for w in words if (m := re.search(rf"\b{w}\b", part)))
    return min(hits, key=lambda m: m.start(), default=None)


def nutrition_numbers(text: str) -> dict[str, float]:
    """Each nutrient's number in the Nutrition section: the one just before its word, else the
    first after it in the same part of the line, else the first in a next part with no nutrient."""
    found: dict[str, float] = {}
    for heading, lines in export._plan_sections(text):
        if fold(heading) not in NUTRITION:
            continue
        for line in lines:
            parts = _PARTS.split(fold(line))
            for part, after in zip(parts, [*parts[1:], ""], strict=True):
                for key, words in NUTRIENTS.items():
                    if key in found or not (hit := _hit(part, words)):
                        continue
                    number = (
                        (
                            not _NOT_BEFORE.match(part, hit.end())
                            and _BEFORE.search(part[: hit.start()])
                        )
                        or _NUMBER.search(part, hit.end())
                        or (
                            not any(_hit(after, w) for w in NUTRIENTS.values())
                            and _UNIT[key].search(after)
                        )
                    )
                    if not number:
                        continue
                    raw = number.group(1)
                    thousands = _THOUSANDS.fullmatch(raw)
                    found[key] = float(re.sub("[.,]", "", raw)) if thousands else _number(raw)
    return found


def nutrition_problems(text: str, macros: dict[str, Any]) -> list[str]:
    got = nutrition_numbers(text)
    out = []
    if "protein" in got and not (
        macros["protein_min_g"] - ROUNDING_G
        <= got["protein"]
        <= macros["protein_max_g"] + ROUNDING_G
    ):
        out.append(
            f"Nutrition: protein {got['protein']:g} g is outside {macros['protein_min_g']:g}-"
            f"{macros['protein_max_g']:g} g from `coach macros`"
        )
    for key, floor in (("fat", "fat_min_g"), ("fibre", "fibre_g")):
        if key in got and got[key] < macros[floor] - ROUNDING_G:
            out.append(
                f"Nutrition: {key} {got[key]:g} g is below the {macros[floor]:g} g minimum from "
                "`coach macros`"
            )
    for key, target in (("kcal", "kcal"), ("carbs", "carbs_g")):
        want = macros[target]
        if key in got and want and abs(got[key] - want) > NUTRITION_TOLERANCE * want:
            unit = "kcal" if key == "kcal" else "g"
            out.append(
                f"Nutrition: {key} {got[key]:g} {unit} is more than "
                f"{NUTRITION_TOLERANCE:.0%} away from {want:g} {unit} from `coach macros`"
            )
    return out


# convention: words that make a training-week part a run, not a lift (es and en): a run bullet
# ("Easy run 40 min", "Rodaje suave 8 km") is checked against `runs plan`, never plan-week.yaml.
RUN_WORDS = (*safety.RUN_NAMES, "rodaje", "tirada", "trote", "jog", "jogging")


def _is_run(name: str) -> bool:
    return any(w in RUN_WORDS for w in re.findall(r"\w+", fold(name)))


def lift_mismatch(text: str, planned: list[str], muscle_map: dict[str, dict]) -> list[str]:
    """Lifts in one file and not the other (plan.md training week, plan-week.yaml)."""
    # Only session bullets: a prose bullet ("Rest 2-3 min between sets") names no lift.
    parts = list(export._plan_parts(text, muscle_map))
    sessions = export._session_bullets(parts)
    in_plan = [
        name for bullet, _, name, _ in parts if bullet in sessions and name and not _is_run(name)
    ]
    planned = [n for n in planned if not _is_run(n)]

    def missing(names: list[str], others: list[str]) -> list[str]:
        return [
            n
            for n in dict.fromkeys(names)
            if not any(strength.named_in(n, [o], muscle_map) for o in others)
        ]

    out = []
    if only := missing(planned, in_plan):
        out.append(f"in plan-week.yaml but not in plan.md: {', '.join(only)}")
    if only := missing(in_plan, planned):
        out.append(f"in plan.md but not in plan-week.yaml: {', '.join(only)}")
    return out


def _prescribing_lines(text: str) -> list[str]:
    return [
        line
        for heading, lines in export._plan_sections(text)
        if fold(heading) in PRESCRIBING
        for line in lines
    ]


def _prescribes(line: str, words: tuple[str, ...]) -> bool:
    """One of `words` (or SIT) in a sentence with no negation before it."""
    for sentence in _SENTENCE_END.split(line):
        sentence = sentence.strip()  # fold strips: keep the SIT offsets on the same text
        folded = fold(sentence)
        hits = [m.start() for w in words for m in re.finditer(rf"\b{re.escape(w)}\b", folded)]
        hits += [m.start() for m in _SIT.finditer(sentence)]
        for start in hits:
            before = _LIMIT.sub(" ", folded[:start])
            if not any(w in PROHIBITIONS for w in re.findall(r"\w+", before)):
                return True
    return False


def veto_problems(text: str, flags: safety.SafetyFlags) -> list[str]:
    lines = _prescribing_lines(text)
    out = []
    if flags.no_all_out_sprints and any(_prescribes(line, SPRINT_WORDS) for line in lines):
        out.append(
            "the plan has all-out sprints (SIT, REHIT, sprints), which `coach safety` rules out "
            "(no_all_out_sprints)"
        )
    if (flags.review_before_vigorous or flags.cap_moderate) and any(
        _prescribes(line, VIGOROUS_WORDS + SPRINT_WORDS) for line in lines
    ):
        out.append(
            "the plan has vigorous or maximal work (HIIT, 1RM tests, sprints) while "
            "`coach safety` caps intensity (review_before_vigorous or cap_moderate)"
        )
    return out


def load_problems(text: str, logged: list[Any], muscle_map: dict[str, dict]) -> list[str]:
    out = []
    seen = set()
    for _, part, name, _ in export._plan_parts(text, muscle_map):
        loads = [_number(x) for x in _KG.findall(part)]
        if not name or not loads or _is_run(name) or (name, max(loads)) in seen:
            continue
        load = max(loads)
        seen.add((name, load))
        best = max(
            (
                strength.e1rm(s.weight_kg, s.reps, strength.effective_rir(s) or 0)
                for s in logged
                if strength.is_working(s)
                and s.weight_kg
                and strength.named_in(s.exercise, [name], muscle_map)
            ),
            default=None,
        )
        if best is not None and load > best:
            out.append(
                f"{name} {load:g} kg is above the estimated 1RM from the log ({best:.1f} kg)"
            )
        elif best is None and load > LOAD_PLAUSIBLE_KG:
            out.append(
                f"{name} {load:g} kg is above {LOAD_PLAUSIBLE_KG:g} kg with no logged history: "
                "check for a typo"
            )
    return out


def planned_km(text: str) -> list[float]:
    """The km of each run in the training week and Cardio sections (one figure per bullet)."""
    out = []
    for line in _prescribing_lines(text):
        km = [_number(x) for x in _KM.findall(line)]
        if line.startswith(("- ", "* ")) and km:
            out.append(max(km))
    return out


def prescribes_training(text: str, muscle_map: dict[str, dict]) -> bool:
    """The plan lists sessions of lifts, or a bullet with a number (sets, load, km, minutes,
    hours) in its training week or Cardio: after a training stop it is stale."""
    # convention: any number but a date in a training bullet counts, so an unread format errs on
    # stale.
    return bool(export.plan_sessions(text, muscle_map)) or any(
        line.startswith(("- ", "* ")) and re.search(r"\d", _DATE.sub("", line))
        for line in _prescribing_lines(text)
    )
