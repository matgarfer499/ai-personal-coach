"""Checks on the committed food tables (foods/base.csv, regions/*/foods.csv)."""

import csv
from pathlib import Path

import pytest

from coach.foods import FIELDS, energy_exception, load_foods

ROOT = Path(__file__).parent.parent.parent
TABLES = [ROOT / "foods" / "base.csv", *sorted(ROOT.glob("regions/*/foods.csv"))]


def rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


@pytest.mark.parametrize("path", TABLES, ids=lambda p: str(p.relative_to(ROOT)))
def test_every_row_is_sourced_and_checked(path):
    table = rows(path)
    assert table, f"{path} is empty"
    assert list(table[0]) == FIELDS
    for row in table:
        assert row["source"] == "fdc_sr_legacy", row["name_en"]
        assert row["source_id"].isdigit(), row["name_en"]
        assert row["source_description"], row["name_en"]
        assert row["name_en"] and row["name_es"], row
        for column in ("kcal", "protein_g", "carbs_g", "fat_g"):
            assert float(row[column]) >= 0, (row["name_en"], column)
        if row["fibre_g"] == "":
            assert "no fibre value" in row["form_note"], row["name_en"]
        else:
            assert float(row["fibre_g"]) >= 0, row["name_en"]
        # Energy within 10% of 4/4/9 (+2 fibre), or the exception is recorded.
        assert bool(energy_exception(row)) == bool(row["kcal_exception"]), row["name_en"]


def test_base_table_size():
    assert len(rows(ROOT / "foods" / "base.csv")) >= 140


def test_names_unique_across_base_and_each_region():
    for region in [p.name for p in (ROOT / "regions").iterdir() if p.is_dir()]:
        load_foods(region)  # raises on a duplicate name in either language


@pytest.mark.parametrize(
    "name", ["salsa de soja", "leche de coco, en lata", "levadura de panadero, seca", "mostaza"]
)
def test_common_cooking_foods_are_in_the_base_table(name):
    from coach.foods import find

    food = find(name, load_foods())
    assert food is not None and food.kcal is not None and food.protein_g is not None


def test_prawns_keep_no_fibre_value_because_the_source_has_none():
    """SR Legacy 175179 has no fibre; the other shrimp entries with fibre 0 are different foods
    (moisture-retaining additives change the macros), so the value stays blank, never typed."""
    row = next(r for r in rows(ROOT / "foods" / "base.csv") if r["name_en"] == "prawns, raw")
    assert row["fibre_g"] == "" and "no fibre value" in row["form_note"]
