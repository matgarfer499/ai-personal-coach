"""build_rows on a synthetic release: units and densities come from the portions."""

import build_food_table
import pytest

DESCRIPTIONS = {"1": "Thing, raw"}
VALUES = {"1": {"kcal": 100.0, "protein": 5.0, "fat": 5.0, "carbs_total": 8.0, "fibre": 1.0}}
PORTIONS = {"1": [("large", 50.0), ("cup", 236.588), ("medium", 40.0), ("medium", 60.0)]}


def item(**kw):
    names = {"name_en": "thing", "name_es": "cosa"}
    return names | {"fdc_id": "1", "fdc_description": "Thing, raw"} | kw


def build(**kw):
    return build_food_table.build_rows([item(**kw)], DESCRIPTIONS, VALUES, PORTIONS)


def test_a_unit_and_a_density_come_from_the_portions():
    [row] = build(unit="large", liquid="yes")
    assert (row["unit_name"], row["unit_g"], row["g_per_ml"]) == ("large", 50.0, 1.0)


@pytest.mark.parametrize("unit", ["clove", "medium"])  # no such portion; two of them
def test_a_unit_must_name_exactly_one_portion(unit):
    with pytest.raises(SystemExit, match=f"portions named '{unit}'"):
        build(unit=unit)
