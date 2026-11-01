"""Checks on the committed food tables (foods/base.csv, regions/*/foods.csv)."""

import csv
from pathlib import Path

import pytest

from coach.foods import FIELDS, energy_exception, find, load_foods

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


NEW_STAPLES = [
    "zumo de naranja",
    "caldo de pastilla, preparado",
    "pan de molde",
    "pan de centeno",
    "tortilla de trigo",
    "atún fresco, crudo",
]


def test_new_spanish_staples_resolve():
    table = load_foods()
    for name in NEW_STAPLES:
        food = find(name, table)
        assert food is not None and food.kcal is not None and food.protein_g is not None, name


def id_rows(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle, delimiter="\t"))


def test_animal_foods_have_fibre():
    """Rows marked `fibre_zero: animal` carry 0, never blank, and say why in the form note."""
    by_id = {r["source_id"]: r for r in rows(ROOT / "foods" / "base.csv")}
    marked = [r for r in id_rows(ROOT / "foods" / "base_ids.tsv") if r["fibre_zero"] == "animal"]
    assert any(r["name_en"] == "prawns, raw" for r in marked)
    for item in marked:
        built = by_id[item["fdc_id"]]
        assert built["fibre_g"] != "", item["name_en"]
        assert "no fibre value" not in built["form_note"], item["name_en"]
    prawns = next(r for r in rows(ROOT / "foods" / "base.csv") if r["name_en"] == "prawns, raw")
    assert float(prawns["fibre_g"]) == 0
    assert "fibre 0: animal food (convention)" in prawns["form_note"]


def test_liquid_rows_have_a_density_from_the_source():
    marked = [r for r in id_rows(ROOT / "foods" / "base_ids.tsv") if r["liquid"] == "yes"]
    names = {r["name_en"] for r in marked}
    assert {"whole milk", "soy sauce", "coconut milk, canned"} <= names
    built = {r["name_en"]: r for r in rows(ROOT / "foods" / "base.csv")}
    for name in names:
        assert 0.9 < float(built[name]["g_per_ml"]) < 1.3, name
    assert built["olive oil"]["g_per_ml"] == ""  # fats keep grams


def test_every_density_is_plausible():
    for path in TABLES:
        for r in rows(path):
            if r["g_per_ml"]:
                assert 0.8 <= float(r["g_per_ml"]) <= 1.3, r["name_en"]


def test_new_staples_use_the_chosen_fdc_ids():
    expected = {
        "zumo de naranja": "169098",
        "caldo de pastilla, preparado": "174566",
        "pan de molde": "172818",
        "pan de centeno": "172684",
        "tortilla de trigo": "167535",
        "atún fresco, crudo": "173706",
    }
    table = load_foods()
    for name, fdc_id in expected.items():
        assert find(name, table).source_id == fdc_id, name
