"""Food tables (per 100 g) and macro totals for a menu.

`foods/base.csv` holds generic foods; `regions/<code>/foods.csv` adds regional ones. Every row
names its source and the source's ID. Lookup is exact (English or Spanish name, any case); the
skill asks the client when a name is not found instead of guessing. A blank value is missing
(None), never zero: menu totals list the items that lack each value.
"""

from __future__ import annotations

import csv
import math
import re
from dataclasses import dataclass, field
from pathlib import Path

from coach.macros import KCAL_PER_G
from coach.regioncode import real_region
from coach.tastes import matches
from coach.text import fold

ROOT = Path(__file__).resolve().parent.parent
FIELDS = [
    "name_en",
    "name_es",
    "kcal",
    "protein_g",
    "carbs_g",
    "fat_g",
    "fibre_g",
    "source",
    "source_id",
    "source_description",
    "form_note",
    "kcal_exception",
    "g_per_ml",
    "unit_name",
    "unit_g",
    "food_group",
    "buy_as",
]
NUMBERS = ("kcal", "protein_g", "carbs_g", "fat_g", "fibre_g")
# nutrition.md: "EU label rules and tolerances": fibre counts 2 kcal/g in label energy.
FIBRE_KCAL_PER_G = 2
# convention: a row's stated energy must be within 10% of the 4/4/9 (+2 for fibre) energy, measured
# against that computed value, or carry a kcal_exception (SR Legacy uses food-specific Atwater
# factors, so exact agreement is not expected).
ENERGY_TOLERANCE = 0.10
# nutrition.md: "Dietary fibre": vegetables and fruit, by the source's food category.
VEG_FRUIT_GROUPS = ("Vegetables and Vegetable Products", "Fruits and Fruit Juices")
# convention: potatoes and other starchy roots are not counted as vegetables (the source record
# for the 400 g rule does not say which foods count; they are the meal's carbohydrate base).
# Matched as whole words of the English name, as `tastes.matches` does.
STARCHY_ROOTS = ("potato", "cassava", "yam", "taro")


# convention: the two bases a table value can have. Grams and millilitres are never mixed (see
# `menu_totals`); a product per 100 ml is a menu item only in millilitres, and a per 100 g food
# can be written in millilitres only when its row has `g_per_ml` (from the source's own portion
# weights, see foods/README.md).
PER_UNITS = {"100 g": "g", "100 ml": "ml"}


class Amount(float):
    """An item's quantity with its unit ("g" or "ml"); behaves as the plain number everywhere."""

    unit: str

    def __new__(cls, value: float, unit: str = "g") -> Amount:
        amount = super().__new__(cls, value)
        amount.unit = unit
        return amount


@dataclass(frozen=True)
class Food:
    name_en: str
    name_es: str
    kcal: float | None
    protein_g: float | None
    carbs_g: float | None
    fat_g: float | None
    fibre_g: float | None
    source: str
    source_id: str
    source_description: str = ""
    form_note: str = ""
    kcal_exception: str = ""
    barcode: str = ""  # catalogue products, which `find` also matches by barcode
    chain: str = ""  # products: the supermarket, for the shopping list
    per: str = "100 g"  # the basis of the values: "100 g" (all generic foods) or "100 ml"
    g_per_ml: float | None = None  # liquids per 100 g: grams in one millilitre
    unit_name: str = ""  # countable foods: the source's portion name ("large" for an egg)
    unit_g: float | None = None  # grams in one such unit
    food_group: str = ""  # the source's food category; blank for products
    buy_as: str = ""  # another form's name_en, bought instead (boiled egg -> raw egg), by unit
    pack_size: float | None = None  # catalogue products: one pack, in this food's unit
    replaces: str = ""  # catalogue products: the generic food's name_en it is bought for

    @classmethod
    def from_row(cls, row: dict) -> Food:
        values = {name: row.get(name, "") or "" for name in FIELDS}
        for name in NUMBERS:
            text = str(values[name]).strip()
            values[name] = float(text) if text else None
        for name in ("g_per_ml", "unit_g"):
            text = str(values[name]).strip()
            values[name] = float(text) if text else None
            number = values[name]
            if number is not None and not (math.isfinite(number) and number > 0):
                raise ValueError(f"{values['name_en']}: {name} must be a positive number")
        return cls(**values)

    @property
    def unit(self) -> str:
        """ "g" or "ml": the unit an item of this food is written in."""
        return PER_UNITS[self.per]

    def missing(self) -> list[str]:
        return [name for name in NUMBERS if getattr(self, name) is None]


def label_energy(row: dict) -> float:
    return (
        KCAL_PER_G["protein"] * float(row["protein_g"])
        + KCAL_PER_G["carbs"] * float(row["carbs_g"])
        + KCAL_PER_G["fat"] * float(row["fat_g"])
        + FIBRE_KCAL_PER_G * float(row["fibre_g"] or 0)
    )


NO_MACROS = "no_macros"  # kinds of `energy_check`, shared with cli.py
GAP = "gap"


def energy_check(row: dict, typed: bool = False) -> tuple[str, str] | None:
    """None when stated kcal is within 10% of the label factors, else (kind, short reason):
    kind is NO_MACROS (kcal but no energy-yielding macros) or GAP.

    `typed`: the kcal was typed from a label, so the reason does not blame a source."""
    stated, computed = float(row["kcal"]), label_energy(row)
    if stated == computed == 0:
        return None
    if computed == 0:
        return NO_MACROS, "no energy-yielding macros listed"
    gap = abs(stated - computed) / computed
    if gap <= ENERGY_TOLERANCE:
        return None
    if typed:
        return GAP, f"{gap:.0%} from the 4/4/9 factors"
    return GAP, f"{gap:.0%} from 4/4/9 factors (source uses food-specific factors)"


def energy_exception(row: dict, typed: bool = False) -> str | None:
    """The reason text of `energy_check`, or None."""
    check = energy_check(row, typed)
    return check[1] if check else None


def _read(path: Path) -> list[Food]:
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [Food.from_row(r) for r in csv.DictReader(handle)]


def load_foods(region: str | None = None, root: Path = ROOT) -> list[Food]:
    table = _read(root / "foods" / "base.csv")
    region = real_region(region)
    if region:
        table += _read(root / "regions" / region / "foods.csv")
    check_unique(table)
    return table


def check_unique(table: list[Food]) -> None:
    """Lookup returns the first match, so every name must be unique in both languages (ignoring
    case and accents, as lookup does)."""
    seen: set[str] = set()
    for food in table:
        for name in {fold(food.name_en), fold(food.name_es)}:
            if name in seen:
                raise ValueError(f"duplicate food name {name!r}")
            seen.add(name)


def find(name: str, table: list[Food]) -> Food | None:
    """Exact name in either language, or a product's barcode; case and accents do not matter."""
    wanted = fold(name)
    return next(
        (f for f in table if wanted in (fold(f.name_en), fold(f.name_es)) or wanted == f.barcode),
        None,
    )


AMOUNT = re.compile(r"(.+?)\s*(ml|g)?", re.IGNORECASE)


def parse_item(text: str) -> tuple[str, Amount]:
    """`NAME=AMOUNT` as used by `coach menu --item`: a food or product name (or a barcode) and
    grams (`150` or `150g`) or millilitres (`15ml`: per 100 ml products or `g_per_ml`)."""
    name, sep, amount = text.rpartition("=")
    if not sep or not name.strip():
        raise ValueError(f"an item needs NAME=GRAMS (or NAME=MLml), got {text!r}")
    match = AMOUNT.fullmatch(amount.strip())
    try:
        if match is None:
            raise ValueError
        return name.strip(), Amount(float(match.group(1)), (match.group(2) or "g").lower())
    except ValueError:
        raise ValueError(f"an item needs NAME=GRAMS (or NAME=MLml), got {text!r}") from None


@dataclass
class MenuTotals:
    kcal: float = 0.0
    protein_g: float = 0.0
    carbs_g: float = 0.0
    fat_g: float = 0.0
    fibre_g: float = 0.0
    veg_fruit_g: float = 0.0  # vegetables and fruit from the food tables; products count 0
    unknown: list[str] = field(default_factory=list)
    # value -> items lacking it; those totals count only the items that have the value
    missing: dict[str, list[str]] = field(default_factory=dict)


def menu_totals(items: list[tuple[str, float]], table: list[Food]) -> MenuTotals:
    """Totals for (food name, grams) pairs; names not in the table are listed in `unknown`, and
    items without a value are listed under that value in `missing` (never counted as zero)."""
    totals = MenuTotals()
    for name, grams in items:
        if not math.isfinite(grams) or grams < 0:
            raise ValueError(f"{name}: grams must be a finite number, 0 or more")
        food = find(name, table)
        if food is None:
            totals.unknown.append(name)
            continue
        unit = getattr(grams, "unit", "g")
        if unit == "ml" and food.unit == "g" and food.g_per_ml:
            grams = grams * food.g_per_ml
        elif unit != food.unit:
            if food.unit == "ml":
                raise ValueError(f"{name} is per 100 ml: write it in millilitres ({name}=NNml)")
            raise ValueError(f"{name} is per 100 g: write it in grams ({name}=NNN), not {unit}")
        if food.food_group in VEG_FRUIT_GROUPS and not any(
            matches(root, food.name_en) for root in STARCHY_ROOTS
        ):
            totals.veg_fruit_g += grams
        for attr in NUMBERS:
            value = getattr(food, attr)
            if value is None:
                totals.missing.setdefault(attr, []).append(name)
            else:
                setattr(totals, attr, getattr(totals, attr) + value * grams / 100)
    return totals
