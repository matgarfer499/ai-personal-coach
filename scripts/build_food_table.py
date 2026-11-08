"""Build a food table from FoodData Central SR Legacy by fdc_id.

Input: one or more tab-separated ID lists (name_en, name_es, fdc_id, fdc_description, form_note,
and optional liquid, fibre_zero and unit columns).
Every number comes from the SR Legacy CSV release (April 2018, the final SR Legacy release, so it
is what FDC serves today), never typed by hand. A row whose fdc_id is unknown, whose description
does not match the release, or whose energy, protein, fat or carbohydrate is missing stops the
build.

Download the release once (not stored in the repo):
  https://fdc.nal.usda.gov/fdc-datasets/FoodData_Central_sr_legacy_food_csv_2018-04.zip

Usage:
  uv run python scripts/build_food_table.py --fdc-dir DIR --ids foods/base_ids.tsv \
      --out foods/base.csv
"""

from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

from coach.foods import FIELDS, energy_exception

# FDC nutrient ids: energy (kcal), protein, total lipid, carbohydrate by difference, total fibre.
NUTRIENTS = {
    "1008": "kcal",
    "1003": "protein",
    "1004": "fat",
    "1005": "carbs_total",
    "1079": "fibre",
}
SOURCE = "fdc_sr_legacy"
# convention: US customary volume definitions (not measurements), in millilitres. A row marked
# `liquid: yes` gets its density from the release's own portion weight for the first of these
# units it has (cup, then fl oz, then tbsp).
UNIT_ML = {"cup": 236.588, "fl oz": 29.5735, "tbsp": 14.7868}
# convention: dietary fibre is plant carbohydrate, so a row marked `fibre_zero: animal` whose
# source has no fibre value gets 0, with this note.
FIBRE_ZERO_NOTE = "fibre 0: animal food (convention)"


def load_release(fdc_dir: Path, ids: set[str]) -> tuple[dict[str, str], dict[str, dict]]:
    with (fdc_dir / "food.csv").open(newline="", encoding="utf-8") as handle:
        descriptions = {r["fdc_id"]: r["description"] for r in csv.DictReader(handle)}
    values: dict[str, dict] = {i: {} for i in ids}
    with (fdc_dir / "food_nutrient.csv").open(newline="", encoding="utf-8") as handle:
        for r in csv.DictReader(handle):
            if r["fdc_id"] in values and r["nutrient_id"] in NUTRIENTS:
                values[r["fdc_id"]][NUTRIENTS[r["nutrient_id"]]] = float(r["amount"])
    return descriptions, values


def load_groups(fdc_dir: Path, ids: set[str]) -> dict[str, str]:
    """fdc_id -> the release's food category description (e.g. "Fruits and Fruit Juices")."""
    with (fdc_dir / "food_category.csv").open(newline="", encoding="utf-8") as handle:
        categories = {r["id"]: r["description"] for r in csv.DictReader(handle)}
    with (fdc_dir / "food.csv").open(newline="", encoding="utf-8") as handle:
        return {
            r["fdc_id"]: categories[r["food_category_id"]]
            for r in csv.DictReader(handle)
            if r["fdc_id"] in ids
        }


def load_portions(fdc_dir: Path, ids: set[str]) -> dict[str, list[tuple[str, float]]]:
    """fdc_id -> (modifier, grams per one) for every portion, the modifier cut before " ("
    ("medium (3\" dia)" is "medium", "cup (8 fl oz)" is "cup"). SR Legacy writes the unit in
    `modifier`."""
    found: dict[str, list[tuple[str, float]]] = {}
    with (fdc_dir / "food_portion.csv").open(newline="", encoding="utf-8") as handle:
        for r in csv.DictReader(handle):
            if r["fdc_id"] in ids and float(r["amount"]) > 0:
                grams = float(r["gram_weight"]) / float(r["amount"])
                found.setdefault(r["fdc_id"], []).append(
                    (r["modifier"].split(" (")[0].strip(), grams)
                )
    return found


def density(portions: list[tuple[str, float]]) -> float | None:
    """Grams per ml from the first portion in a unit of UNIT_ML, in its order."""
    for unit, ml in UNIT_ML.items():
        for found, grams in portions:
            if found == unit:
                return round(grams / ml, 3)
    return None


def build_rows(
    id_rows: list[dict],
    descriptions: dict,
    values: dict,
    portions: dict | None = None,
    groups: dict | None = None,
) -> list[dict]:
    rows, errors = [], []
    for item in id_rows:
        fdc_id = item["fdc_id"].strip()
        if fdc_id not in descriptions:
            errors.append(f"{item['name_en']}: fdc_id {fdc_id} is not in the release")
            continue
        if descriptions[fdc_id] != item["fdc_description"].strip():
            errors.append(f"{item['name_en']}: description mismatch for {fdc_id}")
            continue
        v = values[fdc_id]
        missing = [k for k in ("kcal", "protein", "fat", "carbs_total") if k not in v]
        if missing:
            errors.append(f"{item['name_en']}: {fdc_id} lacks {', '.join(missing)}")
            continue
        fibre = v.get("fibre")
        zero_note = ""
        if fibre is None and (item.get("fibre_zero") or "").strip() == "animal":
            fibre, zero_note = 0.0, FIBRE_ZERO_NOTE
        g_per_ml = None
        if (item.get("liquid") or "").strip() == "yes":
            g_per_ml = density((portions or {}).get(fdc_id, []))
            if g_per_ml is None:
                errors.append(f"{item['name_en']}: liquid with no cup, fl oz or tbsp portion")
                continue
        unit = (item.get("unit") or "").strip()
        unit_g = None
        if unit:
            weights = [g for m, g in (portions or {}).get(fdc_id, []) if m == unit]
            if len(weights) != 1:
                errors.append(f"{item['name_en']}: {len(weights)} portions named {unit!r}, not 1")
                continue
            unit_g = round(weights[0], 1)
        # FDC "carbohydrate by difference" includes fibre; EU labels and this table give
        # available carbohydrate (nutrition.md: "EU label rules and tolerances"). Without a fibre
        # value, fibre stays blank and carbs_g is the total, which the form note says.
        carbs = max(v["carbs_total"] - (fibre or 0.0), 0.0)
        note = "; ".join(x for x in ((item.get("form_note") or "").strip(), zero_note) if x)
        if fibre is None:
            note = "; ".join(x for x in (note, "no fibre value in source, carbs_g is total") if x)
        row = {
            "name_en": item["name_en"].strip(),
            "name_es": item["name_es"].strip(),
            "kcal": v["kcal"],
            "protein_g": v["protein"],
            "carbs_g": round(carbs, 2),
            "fat_g": v["fat"],
            "fibre_g": "" if fibre is None else fibre,
            "source": SOURCE,
            "source_id": fdc_id,
            "source_description": descriptions[fdc_id],
            "form_note": note,
            "g_per_ml": "" if g_per_ml is None else g_per_ml,
            "unit_name": unit,
            "unit_g": "" if unit_g is None else unit_g,
            "food_group": (groups or {}).get(fdc_id, ""),
        }
        row["kcal_exception"] = energy_exception(row) or ""
        rows.append(row)
    if errors:
        raise SystemExit("food table build failed:\n" + "\n".join(errors))
    return rows


def read_ids(paths: list[Path]) -> list[dict]:
    rows = []
    for path in paths:
        with path.open(newline="", encoding="utf-8") as handle:
            rows.extend(csv.DictReader(handle, delimiter="\t"))
    return rows


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--fdc-dir", type=Path, required=True)
    parser.add_argument("--ids", type=Path, nargs="+", required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args(argv)
    id_rows = read_ids(args.ids)
    descriptions, values = load_release(args.fdc_dir, {r["fdc_id"].strip() for r in id_rows})
    ids = {r["fdc_id"].strip() for r in id_rows}
    rows = build_rows(
        id_rows,
        descriptions,
        values,
        load_portions(args.fdc_dir, ids),
        load_groups(args.fdc_dir, ids),
    )
    with args.out.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    exceptions = sum(1 for r in rows if r["kcal_exception"])
    print(f"wrote {len(rows)} foods to {args.out} ({exceptions} energy exceptions)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
