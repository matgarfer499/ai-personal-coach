"""Meal plans over several days: the draft /menu writes, the saved plan and its shopping list.

A draft (data/menu-draft.yaml) lists days, meals and dishes; each dish has a name, its recipe
source, steps, seasoning and `items` written as `NAME=GRAMS`, as in `coach menu --item` (one
serving: what is eaten). The CLI checks every day like `coach menu --targets`, refuses a dish
repeated within NO_REPEAT_DAYS unless it is a batch or a deliberate repeat (`servings: N`), and
saves an accepted plan to data/menus/<first date>.yaml with each day's totals and check.

`servings: N` on a dish says it comes back on purpose, up to N times (a batch cooked once, or a
simple breakfast made again each day): the repeats within its N servings are allowed, the shopping
list buys it once at N servings, and an appearance beyond N is an accidental repeat again.

`base: [PROTEIN, CARB]` on a dish names its main protein and carbohydrate base (one or two plain
words, e.g. `[pollo, arroz]` or `[garbanzos]`): two different dishes on the same base with a gap
of BASE_REPEAT_DAYS days or fewer are a repeat too. A dish without `base` (a breakfast, a snack)
is not checked.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

import yaml

from coach.foods import Food, find, parse_item
from coach.tastes import Tastes, _forms, matches
from coach.text import fold

MENUS_DIR = "menus"
# convention: chosen when the coach was designed (2026-10-25): a dish does not come back
# within 7 consecutive days; a longer plan may cycle its weeks.
NO_REPEAT_DAYS = 7
# convention: two dishes on the same protein and carb base with a gap of 3 days or fewer are a
# repeat, 4 or more passes (see docs/conventions.md): enough variety, a batch still counts once.
BASE_REPEAT_DAYS = 3
# A free meal is the client's choice, never a prescription; with a positive eating-disorder screen
# the CLI refuses it (loss-of-control eating is the risk the rule names).
FREE_MEAL_RULE = 'nutrition.md: "Refeeds and cheat meals"'
# convention: a day has at most one free meal, so a free meal replaces a planned one and cannot
# empty the day (see docs/conventions.md).
FREE_MEALS_PER_DAY = 1
ANY_CHAIN = "any"
UNIT_KEY = {"g": "grams", "ml": "ml"}


@dataclass
class Dish:
    name: str
    servings: int  # 1 unless the dish is a batch or a deliberate repeat
    items: list[tuple[str, float]]  # for one serving: what is eaten
    seasoning: list[str] = field(default_factory=list)
    base: list[str] = field(default_factory=list)  # main protein, then carb base; may be empty


@dataclass
class Meal:
    name: str
    tupper: bool  # carried in a lunchbox
    free: bool  # a free meal: no dishes, its energy is not planned
    dishes: list[Dish]

    @property
    def items(self) -> list[tuple[str, float]]:
        return [item for dish in self.dishes for item in dish.items]


@dataclass
class Day:
    date: date
    meals: list[Meal]

    @property
    def dishes(self) -> list[str]:
        return [dish.name for meal in self.meals for dish in meal.dishes]

    @property
    def items(self) -> list[tuple[str, float]]:
        return [item for meal in self.meals for item in meal.items]

    @property
    def free_meals(self) -> list[str]:
        return [meal.name for meal in self.meals if meal.free]

    @property
    def share(self) -> float:
        """The share of the day's targets the planned meals must carry: 1 without a free meal."""
        # convention: with a free meal, every meal of the day counts for an equal share of the
        # day, so the planned meals must reach planned/total of the kcal, protein, fat and fibre
        # targets by themselves (the free meal's food is unknown and never counted).
        return (len(self.meals) - len(self.free_meals)) / len(self.meals)


def _need(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _text_list(value, where: str) -> None:
    _need(
        value is None or (isinstance(value, list) and all(isinstance(v, str) for v in value)),
        f"{where} must be a list of text lines",
    )


def _flag(entry: dict, key: str, where: str) -> bool:
    value = entry.get(key, False)
    _need(isinstance(value, bool), f"{where}: `{key}:` must be true or false, not {value!r}")
    return value


def parse(data) -> tuple[dict, list[Day]]:
    """The plan document and its days; raises ValueError naming the first problem."""
    _need(isinstance(data, dict) and isinstance(data.get("days"), list), "a plan needs `days:`")
    _need(bool(data["days"]), "a plan needs at least one day in `days:`")
    days: list[Day] = []
    for entry in data["days"]:
        _need(isinstance(entry, dict), "each day needs `date:` and `meals:`")
        when = entry.get("date")
        _need(isinstance(when, date), f"each day needs `date: YYYY-MM-DD`, unquoted: {when!r}")
        _need(not days or when > days[-1].date, f"days must be in date order: {when}")
        listed_meals = entry.get("meals")
        _need(
            isinstance(listed_meals, list) and bool(listed_meals), f"{when}: the day needs `meals:`"
        )
        meals = []
        for meal in listed_meals:
            _need(isinstance(meal, dict), f"{when}: each meal needs `meal:` and `dishes:`")
            tupper = _flag(meal, "tupper", f"{when}")
            free = _flag(meal, "free", f"{when}")
            listed = meal.get("dishes")
            if free:
                _need(not listed, f"{when}: a free meal has no dishes (it replaces a planned one)")
                meals.append(Meal(str(meal.get("meal", "")).strip(), tupper, True, []))
                continue
            _need(isinstance(listed, list) and bool(listed), f"{when}: each meal needs `dishes:`")
            dishes = []
            for dish in listed:
                _need(isinstance(dish, dict), f"{when}: each dish needs `dish:` and `items:`")
                name = dish.get("dish")
                _need(isinstance(name, str) and bool(name.strip()), f"{when}: a dish needs `dish:`")
                for key in ("steps", "seasoning"):
                    _text_list(dish.get(key), f"{when} {name}: {key}")
                lines = dish.get("items")
                _need(isinstance(lines, list) and bool(lines), f"{when} {name}: needs `items:`")
                servings = dish.get("servings", 1)
                _need(
                    isinstance(servings, int) and not isinstance(servings, bool) and servings >= 1,
                    f"{when} {name}: `servings:` must be a whole number, 1 or more, not "
                    f"{servings!r}",
                )
                base = dish.get("base")
                _need(
                    base is None
                    or (
                        isinstance(base, list)
                        and len(base) in (1, 2)
                        and all(isinstance(w, str) and w.split() == [w] for w in base)
                    ),
                    f"{when} {name.strip()}: `base:` must list one or two plain words (no "
                    f"spaces), the main protein then the carb base, e.g. [pollo, arroz], not "
                    f"{base!r}",
                )
                dishes.append(
                    Dish(
                        name.strip(),
                        servings,
                        [parse_item(str(x)) for x in lines],
                        list(dish.get("seasoning") or []),
                        [w.strip() for w in base or []],
                    )
                )
            meals.append(Meal(str(meal.get("meal", "")).strip(), tupper, False, dishes))
        free_meals = [m for m in meals if m.free]
        _need(
            len(free_meals) <= FREE_MEALS_PER_DAY,
            f"{when}: at most one free meal a day (a convention)",
        )
        _need(len(free_meals) < len(meals), f"{when}: the day needs at least one planned meal")
        days.append(Day(when, meals))
    batches(days)  # raises on a batch dish whose items change
    return data, days


def load_draft(path: Path) -> tuple[dict, list[Day]]:
    try:
        data = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    except yaml.YAMLError as err:
        raise ValueError(f"{Path(path).name} is not valid YAML: {err}") from None
    return parse(data)


@dataclass
class Batch:
    """The appearances of one dish that belong together: one serving each, never more than
    `servings` of them (a dish without `servings:` is a group of its own, or of its same-day
    appearances)."""

    dish: str
    servings: int
    dates: list[date]
    items: list[tuple[str, float]]
    base: list[str] = field(default_factory=list)  # from the group's first appearance


def _signature(items: list[tuple[str, float]]) -> list[tuple[str, float, str]]:
    return sorted((fold(n), float(a), getattr(a, "unit", "g")) for n, a in items)


def batches(days: list[Day]) -> list[Batch]:
    """Group each dish's appearances (case and accents ignored) in date order. An appearance with
    `servings: N` joins the open group of that dish while it has the same N and fewer than N
    appearances, else it opens a new one; a dish without `servings:` only groups with itself on
    the same day. Raises ValueError when a batch dish's items change between its appearances."""
    groups: list[Batch] = []
    last: dict[str, Batch] = {}
    for day in days:
        for meal in day.meals:
            for dish in meal.dishes:
                key = fold(dish.name)
                group = last.get(key)
                if group and dish.servings > 1:
                    joins = group.servings == dish.servings and len(group.dates) < dish.servings
                elif group:
                    joins = group.servings == 1 and group.dates[-1] == day.date
                else:
                    joins = False
                if joins:
                    if dish.servings > 1 and _signature(dish.items) != _signature(group.items):
                        raise ValueError(
                            f"{day.date} {dish.name}: a batch dish needs the same items every "
                            "time it appears (its items are for one serving)"
                        )
                    group.dates.append(day.date)
                    if dish.servings == 1:
                        group.items += dish.items  # same day twice: both are eaten
                    continue
                group = Batch(dish.name, dish.servings, [day.date], list(dish.items), dish.base)
                groups.append(group)
                last[key] = group
    return groups


def same_base(a: list[str], b: list[str]) -> bool:
    """Two bases name the same foods in any order: each word of one is a word of the other,
    singular or plural, case and accents ignored (as in `tastes.matches`)."""
    x, y = ([_forms(fold(w)) for w in base] for base in (a, b))
    return all(any(f & g for g in y) for f in x) and all(any(f & g for f in x) for g in y)


def repeats(days: list[Day]) -> list[dict]:
    """Dishes (case and accents ignored) served again within NO_REPEAT_DAYS (`kind: dish`), then
    different dishes on the same `base` with a gap of BASE_REPEAT_DAYS or fewer (`kind: base`;
    a gap of 3 days flags, 4 passes). Both count
    between groups (see `batches`, so a batch is one appearance), from the last serving of one to
    the first of the next."""
    groups = batches(days)
    by_dish: dict[str, list[Batch]] = defaultdict(list)
    for group in groups:
        by_dish[fold(group.dish)].append(group)
    found = []
    for same in by_dish.values():
        close = {
            when
            for a, b in zip(same, same[1:], strict=False)
            if (b.dates[0] - a.dates[-1]).days < NO_REPEAT_DAYS
            for when in (a.dates[-1], b.dates[0])
        }
        if close:
            found.append({"kind": "dish", "dish": same[0].dish, "dates": sorted(close)})
    by_base: list[tuple[list[str], set[date]]] = []
    based = [g for g in groups if g.base]
    for i, a in enumerate(based):
        for b in based[i + 1 :]:
            # the same dish again is already a dish repeat (NO_REPEAT_DAYS is longer)
            if fold(a.dish) == fold(b.dish) or not same_base(a.base, b.base):
                continue
            if (b.dates[0] - a.dates[-1]).days <= BASE_REPEAT_DAYS:
                entry = next((e for e in by_base if same_base(e[0], a.base)), None)
                if entry is None:
                    entry = (a.base, set())
                    by_base.append(entry)
                entry[1].update((a.dates[-1], b.dates[0]))
    found += [
        {"kind": "base", "dish": " + ".join(base), "base": base, "dates": sorted(dates)}
        for base, dates in by_base
    ]
    return found


# What each taste list means for a plan: an allergy or intolerance blocks it (the client named the
# food as one to avoid), a dislike, an untried food or a never_again dish only warns.
BLOCKING_KINDS = ("allergy", "intolerance")
TASTE_LISTS = (
    ("allergy", "allergies"),
    ("intolerance", "intolerances"),
    ("disliked", "disliked_foods"),
    ("untried", "untried"),
)


def taste_flags(days: list[Day], tastes: Tastes, table: list[Food]) -> list[dict]:
    """Every place a plan meets a food the client avoids or has not tried: dish names, items
    (by the food's names in both languages, so a barcode finds its product) and seasoning, matched
    with `tastes.matches`. A `never_again` dish is flagged by its exact name. Name matching is
    a safety net, not a proof: it knows no synonyms."""
    flagged: dict[tuple, dict] = {}
    never = {fold(d): d for d in tastes.dishes("never_again")}

    def add(day, dish, kind, where, entry, text):
        key = (day.date, fold(dish), kind, where, fold(entry), fold(text))
        flagged.setdefault(
            key,
            {
                "date": day.date,
                "dish": dish,
                "kind": kind,
                "where": where,
                "entry": entry,
                "text": text,
                "blocking": kind in BLOCKING_KINDS,
            },
        )

    for day in days:
        for meal in day.meals:
            for dish in meal.dishes:
                if fold(dish.name) in never:
                    add(day, dish.name, "never_again", "dish", never[fold(dish.name)], dish.name)
                texts = [("dish", dish.name, (dish.name,))]
                texts += [("seasoning", s, (s,)) for s in dish.seasoning]
                for name, _ in dish.items:
                    food = find(name, table)
                    names = (name,) + ((food.name_en, food.name_es) if food else ())
                    texts.append(("item", name, names))
                for where, text, names in texts:
                    for kind, attribute in TASTE_LISTS:
                        for entry in getattr(tastes, attribute) or []:
                            if matches(entry, *names):
                                add(day, dish.name, kind, where, entry, text)
    return list(flagged.values())


def save(document: dict, data_dir: Path, replace: bool) -> str:
    """Write the checked plan; returns its path relative to the data dir."""
    relative = f"{MENUS_DIR}/{document['days'][0]['date'].isoformat()}.yaml"
    path = Path(data_dir) / relative
    if path.exists() and not replace:
        raise ValueError(f"{relative} already exists: add --replace to overwrite it")
    path.parent.mkdir(parents=True, exist_ok=True)
    text = yaml.safe_dump(document, sort_keys=False, allow_unicode=True)
    path.write_text(text, encoding="utf-8")
    return relative


def saved(data_dir: Path) -> list[Path]:
    """Saved plans, oldest first (file names are their first date)."""
    return sorted((Path(data_dir) / MENUS_DIR).glob("*.yaml"))


def shopping(
    days: list[Day], table: list[Food], language: str | None, pantry: list[str] | None = None
) -> dict:
    """What to buy: amounts per food or product grouped by chain (`any` for generic foods).

    A batch (`servings: N`) is bought once, at N servings, however many days it is eaten on; any
    other dish is bought for each appearance. Grams (`grams`) and millilitres (`ml`) are listed
    apart. Foods that match the client's `pantry` words are left out and named in
    `pantry_skipped`; names not in the table are listed in `unknown`."""
    amounts: dict[str, dict[tuple[str, str], float]] = defaultdict(lambda: defaultdict(float))
    unknown: list[str] = []
    skipped: dict[str, str] = {}
    cooked = []
    for group in batches(days):
        times = group.servings if group.servings > 1 else 1
        if group.servings > 1:
            cooked.append(
                {
                    "dish": group.dish,
                    "servings": group.servings,
                    "dates": group.dates,
                    "left_over": group.servings - len(group.dates),
                }
            )
        for name, amount in group.items:
            food = find(name, table)
            if food is None:
                unknown.append(name)
                continue
            label = food.name_en if language == "en" else food.name_es
            if any(matches(word, food.name_en, food.name_es) for word in pantry or []):
                skipped[fold(label)] = label
                continue
            amounts[food.chain or ANY_CHAIN][(label, food.unit)] += amount * times
    chains = sorted(amounts, key=lambda chain: (chain == ANY_CHAIN, fold(chain)))
    return {
        "chains": {
            chain: [
                {"name": name, UNIT_KEY[unit]: total}
                for (name, unit), total in sorted(amounts[chain].items())
            ]
            for chain in chains
        },
        "unknown": unknown,
        "batches": cooked,
        "pantry_skipped": [skipped[key] for key in sorted(skipped)],
    }
