import csv
import json
from datetime import date
from pathlib import Path

import pytest

from coach import catalogue, off
from coach.cli import main
from coach.profile import Profile, save_profile

FIXTURES = Path(__file__).parent.parent / "fixtures" / "off"
TODAY = "2026-10-25"


@pytest.fixture
def data_dir(tmp_path, monkeypatch):
    monkeypatch.setenv(off.CONTACT_ENV, "tester@example.org")
    save_profile(
        Profile(
            sex="female",
            birth_date=date(1992, 3, 10),
            height_cm=165,
            weight_kg=62,
            goal="maintenance",
            activity_level="desk",
            region="es",
            screening={"scoff_positive": False},
        ),
        tmp_path / "profile.yaml",
    )
    return tmp_path


@pytest.fixture
def off_returns(monkeypatch):
    """Serve one fixture file per call to Open Food Facts; record the URLs."""
    calls = []

    def serve(*names):
        queue = list(names)

        def get(url):
            calls.append(url)
            return json.loads((FIXTURES / queue.pop(0)).read_text(encoding="utf-8"))

        monkeypatch.setattr(off, "_get_json", get)
        return calls

    return serve


def run(capsys, data_dir, *args):
    code = main(["--data-dir", str(data_dir), "--today", TODAY, *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def add(capsys, data_dir, off_returns, fixture, barcode, *extra):
    off_returns(fixture)
    return run(capsys, data_dir, "products", "add", barcode, "--chain", "Mercadona", *extra)


def test_add_writes_a_catalogue_row(capsys, data_dir, off_returns):
    code, out = add(capsys, data_dir, off_returns, "product_found.json", "8400000000017")
    assert code == 0
    assert out["added"]["product_name"] == "Salteado campestre"
    assert out["added"]["source"] == catalogue.SOURCE == "Open Food Facts (unverified)"
    assert out["missing"] == [] and out["warnings"] == []
    with (data_dir / "catalogue.csv").open(encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    assert list(rows[0]) == catalogue.FIELDS
    assert rows[0] == {
        "barcode": "8400000000017",
        "product_name": "Salteado campestre",
        "brand": "Marca Prueba",
        "chain": "Mercadona",
        "per": "100 g",
        "kcal": "81",
        "protein_g": "1.7",
        "carbs_g": "15.5",
        "fat_g": "0.5",
        "fibre_g": "2.4",
        "allergens": "",
        "url": "https://world.openfoodfacts.org/product/8400000000017",
        "fetched_on": TODAY,
        "source": "Open Food Facts (unverified)",
        "pack_size": "",
        "replaces": "",
    }


def test_add_keeps_a_missing_value_blank(capsys, data_dir, off_returns):
    _, out = add(capsys, data_dir, off_returns, "product_missing_fibre.json", "8400000000024")
    assert out["missing"] == ["fibre_g"]
    row = catalogue.load(data_dir)[0]
    assert row.fibre_g is None and row.allergens == ("en:gluten",)
    text = (data_dir / "catalogue.csv").read_text(encoding="utf-8")
    assert ",150,2.5,20,6.1,,en:gluten," in text


def test_add_without_contact_is_refused(capsys, data_dir, monkeypatch):
    monkeypatch.delenv(off.CONTACT_ENV)
    code, out = run(capsys, data_dir, "products", "add", "8400000000017", "--chain", "Lidl")
    assert code == 2 and off.CONTACT_ENV in out["message"]


def test_add_not_found(capsys, data_dir, off_returns):
    code, out = add(capsys, data_dir, off_returns, "product_not_found.json", "8400000000062")
    assert code == 2 and "not in Open Food Facts" in out["message"]
    assert not (data_dir / "catalogue.csv").exists()


def test_add_without_name_or_unit_asks_for_them(capsys, data_dir, off_returns):
    code, out = add(capsys, data_dir, off_returns, "product_no_unit.json", "8400000000048")
    assert code == 2 and "--name" in out["message"]
    code, out = add(
        capsys, data_dir, off_returns, "product_no_unit.json", "8400000000048", "--name", "Patata"
    )
    assert code == 2 and "--per" in out["message"]
    code, out = add(
        capsys,
        data_dir,
        off_returns,
        "product_no_unit.json",
        "8400000000048",
        "--name",
        "Patata de prueba",
        "--per",
        "100 g",
    )
    assert code == 0 and out["added"]["per"] == "100 g"


def test_add_refuses_a_name_that_clashes_with_a_known_food(capsys, data_dir, off_returns):
    code, out = add(
        capsys,
        data_dir,
        off_returns,
        "product_found.json",
        "8400000000017",
        "--name",
        "Pechuga de pollo, cruda",
    )
    assert code == 2 and "--name" in out["message"]


def test_add_refuses_the_same_barcode_unless_replaced(capsys, data_dir, off_returns):
    add(capsys, data_dir, off_returns, "product_found.json", "8400000000017")
    code, out = add(capsys, data_dir, off_returns, "product_found.json", "8400000000017")
    assert code == 2 and "--replace" in out["message"]
    code, out = add(
        capsys,
        data_dir,
        off_returns,
        "product_found.json",
        "8400000000017",
        "--replace",
        "--name",
        "Salteado de la casa",
    )
    assert code == 0
    assert [p.product_name for p in catalogue.load(data_dir)] == ["Salteado de la casa"]


def test_add_records_impossible_values_as_missing(capsys, data_dir, off_returns):
    _, out = add(capsys, data_dir, off_returns, "product_bad_values.json", "8400000000055")
    assert out["missing"] == ["kcal", "protein_g", "carbs_g", "fibre_g"]
    assert "\n" not in out["added"]["product_name"]


def test_products_search_saves_nothing(capsys, data_dir, off_returns):
    calls = off_returns("search.json")
    code, out = run(capsys, data_dir, "products", "search", "salteado", "--brand", "Prueba")
    assert code == 0 and len(calls) == 1
    assert [h["barcode"] for h in out["hits"]] == ["8400000000017", "8400000000024"]
    assert out["source"] == "Open Food Facts (unverified)"
    assert not (data_dir / "catalogue.csv").exists()


def test_products_list(capsys, data_dir, off_returns):
    add(capsys, data_dir, off_returns, "product_found.json", "8400000000017")
    _, out = run(capsys, data_dir, "products", "list")
    assert [p["barcode"] for p in out["products"]] == ["8400000000017"]


def test_foods_search_and_menu_resolve_catalogue_products(capsys, data_dir, off_returns):
    add(capsys, data_dir, off_returns, "product_found.json", "8400000000017")
    add(capsys, data_dir, off_returns, "product_missing_fibre.json", "8400000000024")
    _, found = run(capsys, data_dir, "foods", "search", "salteado")
    assert found["products"] == [
        {
            "product_name": "Salteado campestre",
            "brand": "Marca Prueba",
            "chain": "Mercadona",
            "per": "100 g",
            "kcal": 81,
            "protein_g": 1.7,
            "carbs_g": 15.5,
            "fat_g": 0.5,
            "fibre_g": 2.4,
            "missing": [],
            "barcode": "8400000000017",
            "allergens": [],
            "source": "Open Food Facts (unverified)",
            "url": "https://world.openfoodfacts.org/product/8400000000017",
        }
    ]
    _, by_name = run(capsys, data_dir, "menu", "--item", "salteado campestre=200")
    _, by_code = run(capsys, data_dir, "menu", "--item", "8400000000017=200")
    assert by_name == by_code and by_name["kcal"] == 162 and by_name["unknown"] == []
    _, gajos = run(capsys, data_dir, "menu", "--item", "8400000000024=100")
    assert gajos["missing"] == {"fibre_g": ["8400000000024"]} and gajos["fibre_g"] == 0


def test_catalogue_products_per_100_ml_are_menu_items_in_millilitres(capsys, data_dir, off_returns):
    add(capsys, data_dir, off_returns, "product_liquid.json", "8400000000031")
    _, out = run(capsys, data_dir, "menu", "--item", "8400000000031=250ml")
    assert out["unknown"] == [] and out["kcal"] == 112.5
    _, found = run(capsys, data_dir, "foods", "search", "avena")
    assert [p["per"] for p in found["products"] if p.get("barcode")] == ["100 ml"]


def test_grams_of_a_liquid_product_are_refused(capsys, data_dir, off_returns):
    add(capsys, data_dir, off_returns, "product_liquid.json", "8400000000031")
    code, out = run(capsys, data_dir, "menu", "--item", "8400000000031=250")
    assert code == 2 and "per 100 ml" in out["message"]
    add(capsys, data_dir, off_returns, "product_found.json", "8400000000017")
    code, out = run(capsys, data_dir, "menu", "--item", "8400000000017=200ml")
    assert code == 2 and "per 100 g" in out["message"]


def test_add_refuses_a_basis_that_disagrees_with_the_pack_unit(capsys, data_dir, off_returns):
    """OFF says the pack is in ml, so its values are per 100 ml; saying per 100 g needs
    --confirm-per after reading the label."""
    code, out = add(
        capsys, data_dir, off_returns, "product_liquid.json", "8400000000031", "--per", "100 g"
    )
    assert code == 2 and "--confirm-per" in out["message"] and "100 ml" in out["message"]
    assert not (data_dir / "catalogue.csv").exists()
    code, out = add(
        capsys,
        data_dir,
        off_returns,
        "product_liquid.json",
        "8400000000031",
        "--per",
        "100 g",
        "--confirm-per",
    )
    assert code == 0 and out["added"]["per"] == "100 g"


def test_confirm_per_does_nothing_when_they_agree(capsys, data_dir, off_returns):
    code, out = add(
        capsys, data_dir, off_returns, "product_liquid.json", "8400000000031", "--per", "100 ml"
    )
    assert code == 0 and out["added"]["per"] == "100 ml"


def test_foods_search_lists_missing_values_for_every_entry(capsys, data_dir):
    skyr = catalogue.CatalogueProduct(
        barcode="8400000000048",
        product_name="Skyr de prueba",
        brand="Marca Prueba",
        chain="Eroski",
        per="100 g",
        kcal=50,
        protein_g=8,
        carbs_g=4.1,
        fat_g=0.2,
        fibre_g=None,
        allergens=(),
        url="https://world.openfoodfacts.org/product/8400000000048",
        fetched_on=date(2026, 10, 1),
    )
    catalogue.save([skyr], data_dir)
    _, out = run(capsys, data_dir, "foods", "search", "skyr")
    assert out["products"][0]["missing"] == ["fibre_g"]
    _, out = run(capsys, data_dir, "foods", "search", "lentejas")
    assert all(f["missing"] == [] for f in out["foods"])


def test_a_label_product_round_trips(tmp_path):
    product = catalogue.CatalogueProduct(
        barcode="label-proteina-chocolate",
        product_name="Proteina chocolate",
        brand="",
        chain="Mercadona",
        per="100 g",
        kcal=380,
        protein_g=30,
        carbs_g=40,
        fat_g=9.5,
        fibre_g=None,
        allergens=("soja",),
        url="",
        fetched_on=date(2026, 11, 1),
        source=catalogue.LABEL_SOURCE,
    )
    catalogue.save([product], tmp_path)
    assert catalogue.load(tmp_path) == [product]
    assert catalogue.LABEL_SOURCE == "label (entered by hand)"


def test_off_replace_never_overwrites_a_hand_entered_label_row(capsys, data_dir, off_returns):
    code, _ = run(
        capsys, data_dir, "products", "add", "--label", "--name", "Proteina choco",
        "--chain", "X", "--per", "100 g", "--kcal", "380", "--protein", "30", "--carbs", "40",
        "--fat", "9.5", "--allergens", "soja", "--barcode", "8400000000017",
    )  # fmt: skip
    assert code == 0
    code, out = add(
        capsys, data_dir, off_returns, "product_found.json", "8400000000017", "--replace"
    )
    assert code != 0 and "hand-entered label row" in out["message"]
    assert (
        "remove" not in out["message"]
        and "giving every label value again: --label --barcode 8400000000017 --replace"
        in out["message"]
    )
    assert catalogue.load(data_dir)[0].allergens == ("soja",)


def test_off_add_with_energy_but_no_macros_warns_in_a_full_sentence(capsys, data_dir, monkeypatch):
    raw = json.loads((FIXTURES / "product_found.json").read_text(encoding="utf-8"))
    for key in ("proteins_100g", "carbohydrates_100g", "fat_100g", "fiber_100g"):
        raw["product"]["nutriments"][key] = 0
    monkeypatch.setattr(off, "_get_json", lambda url: raw)
    _, out = run(capsys, data_dir, "products", "add", "8400000000017", "--chain", "X")
    assert out["warnings"] == [
        "kcal is stated but no energy-yielding macros are listed; check the pack"
    ]


def test_off_energy_gap_does_not_say_label(capsys, data_dir, monkeypatch):
    raw = json.loads((FIXTURES / "product_found.json").read_text(encoding="utf-8"))
    raw["product"]["nutriments"]["energy-kcal_100g"] = 400
    monkeypatch.setattr(off, "_get_json", lambda url: raw)
    _, out = run(capsys, data_dir, "products", "add", "8400000000017", "--chain", "X")
    warning = out["warnings"][0]
    assert warning.startswith("kcal is ") and "label" not in warning
    assert warning.endswith("(source uses food-specific factors); check the pack")


def test_add_keeps_the_pack_size_open_food_facts_gives(capsys, data_dir, off_returns):
    """A 1000 ml pack of a per-100 ml product: its pack size is 1000."""
    code, out = add(capsys, data_dir, off_returns, "product_liquid.json", "8400000000031")
    assert code == 0 and out["added"]["pack_size"] == 1000
    assert catalogue.load(data_dir)[0].pack_size == 1000


def test_add_ignores_a_pack_in_another_unit(capsys, data_dir, off_returns):
    """Values per 100 g on a pack sold in ml: the ml count is no pack size in grams."""
    code, out = add(
        capsys, data_dir, off_returns, "product_label_g_sold_ml.json", "8400000000086",
        "--per", "100 g", "--confirm-per",
    )  # fmt: skip
    assert code == 0 and out["added"]["pack_size"] is None


def test_pack_size_and_replaces_are_typed_and_checked(capsys, data_dir, off_returns):
    code, out = add(
        capsys, data_dir, off_returns, "product_liquid.json", "8400000000031",
        "--pack-size", "500", "--replaces", "leche semidesnatada",
    )  # fmt: skip
    assert code == 0 and out["added"]["pack_size"] == 500
    assert out["added"]["replaces"] == "semi-skimmed milk"
    # --replace without the flags keeps both
    code, out = add(
        capsys, data_dir, off_returns, "product_liquid.json", "8400000000031", "--replace"
    )
    assert code == 0 and out["added"]["pack_size"] == 500
    assert out["added"]["replaces"] == "semi-skimmed milk"


@pytest.mark.parametrize(
    "flags, message",
    [
        (["--pack-size", "0"], "--pack-size"),
        (["--pack-size", "nan"], "--pack-size"),
        (["--pack-size", "1.000"], "thousands"),  # a Spanish "1.000 ml" is not 1 ml
        (["--replaces", "huevo cocido"], "bought as"),  # shopping buys it as a raw egg
        (["--replaces", "leche de unicornio"], "not a food"),
        (["--replaces", "Salteado campestre"], "not a food"),
    ],
)
def test_bad_pack_size_or_replaces_is_refused(capsys, data_dir, off_returns, flags, message):
    add(capsys, data_dir, off_returns, "product_found.json", "8400000000017")
    code, out = add(capsys, data_dir, off_returns, "product_liquid.json", "8400000000031", *flags)
    assert code != 0 and message in out["message"]


def test_two_products_cannot_replace_the_same_food(capsys, data_dir, off_returns):
    add(capsys, data_dir, off_returns, "product_liquid.json", "8400000000031",
        "--replaces", "semi-skimmed milk")  # fmt: skip
    code, out = add(
        capsys, data_dir, off_returns, "product_label_ml_sold_ml.json", "8400000000079",
        "--replaces", "leche semidesnatada",
    )  # fmt: skip
    assert code != 0 and "already replaces" in out["message"]
    # an empty --replaces frees the food for the new product
    add(capsys, data_dir, off_returns, "product_liquid.json", "8400000000031",
        "--replace", "--replaces", "")  # fmt: skip
    code, out = add(
        capsys, data_dir, off_returns, "product_label_ml_sold_ml.json", "8400000000079",
        "--replaces", "leche semidesnatada",
    )  # fmt: skip
    assert code == 0 and out["added"]["replaces"] == "semi-skimmed milk"


def test_a_pack_size_in_another_unit_than_per_is_dropped(capsys, data_dir, off_returns):
    """OFF's 1000 ml pack, but the label read says per 100 g: 1000 is no pack size in grams."""
    code, out = add(capsys, data_dir, off_returns, "product_liquid.json", "8400000000031",
                    "--per", "100 g", "--confirm-per")  # fmt: skip
    assert code == 0 and out["added"]["pack_size"] is None


def test_replaces_needs_a_unit_the_product_can_take(capsys, data_dir, off_returns):
    """A per-100 g product can stand for any generic food (all are per 100 g); a per-100 ml
    product only for one with a density to turn its grams into ml."""
    code, out = add(capsys, data_dir, off_returns, "product_found.json", "8400000000017",
                    "--replaces", "garbanzos, cocidos")  # fmt: skip
    assert code == 0 and out["added"]["replaces"] == "chickpeas, cooked"
    code, out = add(capsys, data_dir, off_returns, "product_liquid.json", "8400000000031",
                    "--replaces", "garbanzos, cocidos")  # fmt: skip
    assert code != 0 and "no density" in out["message"]


@pytest.mark.parametrize("size", ["0", "-1", "nan"])
def test_a_hand_edited_pack_size_must_be_positive(capsys, data_dir, off_returns, size):
    add(capsys, data_dir, off_returns, "product_liquid.json", "8400000000031")
    path = data_dir / "catalogue.csv"
    rows = list(csv.DictReader(path.open(encoding="utf-8")))
    rows[0]["pack_size"] = size
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=catalogue.FIELDS)
        writer.writeheader()
        writer.writerows(rows)
    with pytest.raises(ValueError, match="pack_size"):
        catalogue.load(data_dir)


# Beta 3 p4-sara-N2: a dry product never stands in for a cooked food gram for gram.
def test_a_dry_product_cannot_replace_a_cooked_food(capsys, data_dir):
    code, out = run(
        capsys, data_dir, "products", "add", "--label", "--name", "Garbanzo seco prueba",
        "--chain", "Mercadona", "--per", "100 g", "--kcal", "360", "--protein", "20",
        "--carbs", "50", "--fat", "6", "--allergens", "ninguno",
        "--replaces", "garbanzos, cocidos",
    )  # fmt: skip
    assert code != 0 and "dry" in out["message"]


def test_a_cooked_product_can_replace_its_cooked_food(capsys, data_dir):
    code, out = run(
        capsys, data_dir, "products", "add", "--label", "--name", "Arroz cocido vasito prueba",
        "--chain", "Mercadona", "--per", "100 g", "--kcal", "150", "--protein", "3",
        "--carbs", "32", "--fat", "1", "--allergens", "ninguno",
        "--replaces", "arroz blanco, cocido",
    )  # fmt: skip
    assert code == 0 and out["added"]["replaces"] == "white rice, cooked"


def test_a_dry_rice_product_is_pointed_to_the_dry_food(capsys, data_dir):
    code, out = run(
        capsys, data_dir, "products", "add", "--label", "--name", "Arroz redondo prueba",
        "--chain", "Mercadona", "--per", "100 g", "--kcal", "350", "--protein", "7",
        "--carbs", "78", "--fat", "1", "--allergens", "ninguno",
        "--replaces", "arroz blanco, cocido",
    )  # fmt: skip
    assert code != 0 and "white rice, raw" in out["message"]
