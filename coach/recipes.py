"""The client's recipe library: data/recipes/<dish>.yaml, grown by rating dishes.

Recipes come from the web, so the library lives in the data directory (gitignored), never in the
repository; each file keeps the recipe's `source` URL as its attribution. A recipe is saved when
a dish is rated loved or liked: its steps, seasoning and items are copied from the newest saved
menu that has the dish, or, for a dish outside the menus, only its name and source are kept.
Items are written as `NAME=AMOUNT` like a draft's; the library stores no kcal or macros, so
every figure is checked again by the CLI when the dish goes into a new menu.
"""

from __future__ import annotations

import re
from datetime import date
from pathlib import Path

import yaml

from coach import mealplan
from coach.tastes import Tastes
from coach.text import fold

RECIPES_DIR = "recipes"
# convention: file names keep at most 80 characters of the dish name (readable, well under any
# file system limit).
SLUG_MAX = 80
# Dishes that are saved: the ones the client likes. Liked first when listing.
SAVED_RATINGS = ("loved", "liked")
RATING_ORDER = ("loved", "liked", "disliked", "never_again")


def slug(dish: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", fold(dish)).strip("-")[:SLUG_MAX].strip("-") or "dish"


def _relative(dish: str) -> str:
    return f"{RECIPES_DIR}/{slug(dish)}.yaml"


def _read(path: Path) -> dict:
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as err:
        raise ValueError(f"{path.name} is not valid YAML: {err}") from None
    if not isinstance(data, dict) or not isinstance(data.get("dish"), str):
        raise ValueError(f"{path.name} needs a `dish:` name")
    return data


def find_in_menus(data_dir: Path, dish: str) -> dict | None:
    """The dish as written in the newest saved menu that has it (case and accents ignored)."""
    for path in reversed(mealplan.saved(data_dir)):
        document = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
        for day in document.get("days") or []:
            for meal in day.get("meals") or []:
                for entry in meal.get("dishes") or []:
                    if fold(str(entry.get("dish", ""))) == fold(dish):
                        return entry
    return None


def save(
    data_dir: Path,
    dish: str,
    source: str,
    saved_on: date,
) -> str | None:
    """Write or update the dish's recipe; returns its path relative to the data dir, or None
    when there is nothing worth keeping (no menu recipe and no source)."""
    relative = _relative(dish)
    path = Path(data_dir) / relative
    recipe = _read(path) if path.exists() else {"dish": dish.strip()}
    entry = find_in_menus(data_dir, dish)
    if entry:
        recipe["dish"] = str(entry["dish"]).strip()
        for key in ("source", "steps", "seasoning", "items"):
            if entry.get(key):
                recipe[key] = entry[key]
        if isinstance(entry.get("servings"), int) and entry["servings"] > 1:
            recipe["servings"] = entry["servings"]
    if source:
        recipe["source"] = source
    if not any(recipe.get(key) for key in ("source", "steps", "items")):
        return None
    recipe["saved_on"] = saved_on
    path.parent.mkdir(parents=True, exist_ok=True)
    order = ("dish", "source", "servings", "steps", "seasoning", "items", "saved_on")
    recipe = {k: recipe[k] for k in order if k in recipe} | {
        k: v for k, v in recipe.items() if k not in order
    }
    path.write_text(yaml.safe_dump(recipe, sort_keys=False, allow_unicode=True), encoding="utf-8")
    return relative


def _rating(tastes: Tastes, dish: str) -> str | None:
    return next((r.rating for r in tastes.ratings if fold(r.dish) == fold(dish)), None)


def load_all(data_dir: Path, tastes: Tastes) -> list[dict]:
    """Every saved recipe with its current rating from the taste profile, loved first."""
    folder = Path(data_dir) / RECIPES_DIR
    recipes = []
    for path in sorted(folder.glob("*.yaml")):
        recipe = _read(path)
        recipes.append(
            recipe
            | {"rating": _rating(tastes, recipe["dish"]), "file": f"{RECIPES_DIR}/{path.name}"}
        )
    rank = {name: i for i, name in enumerate(RATING_ORDER)}
    return sorted(recipes, key=lambda r: rank.get(r["rating"], len(rank)))


def _text(recipe: dict) -> str:
    items = [str(i).rpartition("=")[0] or str(i) for i in recipe.get("items") or []]
    return " ".join([recipe["dish"], *items, *(recipe.get("seasoning") or [])])


def search(recipes: list[dict], words: list[str]) -> list[dict]:
    """Recipes whose dish, ingredients or seasoning have a word starting with each search word
    (accents and case ignored, as in `coach foods search`); never_again dishes are left out."""
    wanted = [fold(w) for w in words if w.strip()]
    if not wanted:
        raise ValueError("recipes search needs at least one word")
    found = []
    for recipe in recipes:
        if recipe["rating"] == "never_again":
            continue
        have = re.findall(r"\w+", fold(_text(recipe)))
        if all(any(h.startswith(w) for h in have) for w in wanted):
            found.append(recipe)
    return found


def get(recipes: list[dict], dish: str) -> dict:
    for recipe in recipes:
        if fold(recipe["dish"]) == fold(dish):
            return recipe
    raise ValueError(f"{dish!r} is not in the library")


def remove(data_dir: Path, recipes: list[dict], dish: str) -> str:
    recipe = get(recipes, dish)
    (Path(data_dir) / recipe["file"]).unlink()
    return recipe["file"]
