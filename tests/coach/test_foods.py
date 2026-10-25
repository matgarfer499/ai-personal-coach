import pytest

from coach import foods
from coach.foods import Food, energy_exception, find, load_foods, menu_totals


def row(**kw):
    base = dict(
        name_en="test food",
        name_es="alimento",
        kcal=100.0,
        protein_g=10.0,
        carbs_g=10.0,
        fat_g=2.0,
        fibre_g=1.0,
        source="fdc_sr_legacy",
        source_id="1",
        source_description="Test",
        form_note="",
        kcal_exception="",
    )
    return base | kw


# nutrition.md "EU label rules and tolerances": 4 kcal/g protein and carbohydrate, 9 fat, 2 fibre
def test_energy_exception():
    # 4*10 + 4*10 + 9*2 + 2*1 = 100
    assert energy_exception(row()) is None
    assert energy_exception(row(kcal=109)) is None
    assert "%" in energy_exception(row(kcal=120))
    assert energy_exception(row(kcal=0, protein_g=0, carbs_g=0, fat_g=0, fibre_g=0)) is None
    # Measured against the computed value: 89 is 11% below 100.
    assert energy_exception(row(kcal=89)) is not None
    assert energy_exception(row(fibre_g="")) is None  # blank fibre counts as 0 (98 vs 100)


def test_find_is_exact_and_case_insensitive_in_both_languages():
    table = [Food.from_row(row(name_en="Apple", name_es="Manzana"))]
    assert find("apple", table).name_en == "Apple"
    assert find("MANZANA", table).name_es == "Manzana"
    assert find("apples", table) is None


def test_menu_totals_scales_per_100_g_and_lists_unknown_names():
    table = [Food.from_row(row(name_en="rice", name_es="arroz"))]
    totals = menu_totals([("arroz", 250), ("mystery stew", 100)], table)
    assert totals.kcal == pytest.approx(250)
    assert totals.protein_g == pytest.approx(25)
    assert totals.fibre_g == pytest.approx(2.5)
    assert totals.unknown == ["mystery stew"]
    assert totals.missing == {}


def test_blank_values_are_missing_never_zero():
    assert Food.from_row(row(fibre_g="")).fibre_g is None
    assert Food.from_row(row(fibre_g="0")).fibre_g == 0


def test_menu_totals_lists_items_missing_a_value():
    table = [
        Food.from_row(row(name_en="rice", name_es="arroz")),
        Food.from_row(row(name_en="ham", name_es="jamón", fibre_g="", kcal="")),
    ]
    totals = menu_totals([("arroz", 100), ("jamón", 50)], table)
    assert totals.fibre_g == pytest.approx(1)  # rice only: nothing is assumed for the ham
    assert totals.kcal == pytest.approx(100)
    assert totals.missing == {"kcal": ["jamón"], "fibre_g": ["jamón"]}


@pytest.mark.parametrize("grams", [-5, float("nan"), float("inf")])
def test_menu_totals_rejects_bad_grams(grams):
    table = [Food.from_row(row())]
    with pytest.raises(ValueError, match="finite"):
        menu_totals([("test food", grams)], table)


def write_table(path, *rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = [",".join(foods.FIELDS)]
    lines += [",".join(str(r[f]) for f in foods.FIELDS) for r in rows]
    path.write_text("\n".join(lines) + "\n")


def test_load_foods_merges_base_and_region(tmp_path):
    write_table(tmp_path / "foods" / "base.csv", row(name_en="rice"))
    write_table(tmp_path / "regions" / "es" / "foods.csv", row(name_en="octopus", name_es="pulpo"))
    assert [f.name_en for f in load_foods(None, tmp_path)] == ["rice"]
    assert [f.name_en for f in load_foods("es", tmp_path)] == ["rice", "octopus"]


def test_load_foods_refuses_duplicate_names(tmp_path):
    write_table(tmp_path / "foods" / "base.csv", row(), row())
    with pytest.raises(ValueError, match="duplicate"):
        load_foods(None, tmp_path)


def test_find_ignores_accents():
    platano = Food.from_row(row(name_en="banana", name_es="plátano"))
    assert find("platano", [platano]) is platano


def test_parse_item_reads_grams_or_millilitres():
    assert foods.parse_item("arroz=250") == ("arroz", 250)
    assert foods.parse_item("arroz=250g") == ("arroz", 250)
    assert foods.parse_item("arroz = 250 G") == ("arroz", 250)
    name, amount = foods.parse_item("salsa de soja=15ml")
    assert (name, float(amount), amount.unit) == ("salsa de soja", 15.0, "ml")
    assert foods.parse_item("salsa de soja=15 ML")[1].unit == "ml"
    assert foods.parse_item("arroz=250")[1].unit == "g"
    for bad in ("arroz=ml", "arroz=15l", "arroz=15mg", "=15ml", "arroz"):
        with pytest.raises(ValueError, match="NAME="):
            foods.parse_item(bad)


def liquid_table():
    return [
        Food.from_row(row(name_en="rice", name_es="arroz")),
        Food(
            name_en="oat drink", name_es="bebida de avena", kcal=50.0, protein_g=1.0, carbs_g=8.0,
            fat_g=1.5, fibre_g=None, source="x", source_id="y", per="100 ml",
        ),
    ]  # fmt: skip


def test_millilitres_count_per_100_ml_for_liquid_products():
    totals = menu_totals([foods.parse_item("bebida de avena=250ml")], liquid_table())
    assert totals.kcal == pytest.approx(125) and totals.protein_g == pytest.approx(2.5)
    assert totals.missing == {"fibre_g": ["bebida de avena"]}


def test_grams_and_millilitres_are_never_mixed():
    table = liquid_table()
    with pytest.raises(ValueError, match="per 100 ml.*ml"):
        menu_totals([foods.parse_item("bebida de avena=250")], table)
    with pytest.raises(ValueError, match="per 100 ml.*ml"):
        menu_totals([foods.parse_item("bebida de avena=250g")], table)
    with pytest.raises(ValueError, match="per 100 g.*grams"):
        menu_totals([foods.parse_item("arroz=100ml")], table)
    # plain tuples (callers that never use millilitres) are grams
    assert menu_totals([("arroz", 100)], table).kcal == pytest.approx(100)
