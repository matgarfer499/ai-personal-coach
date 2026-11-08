"""PDF export of a saved menu (needs the optional `pdf` extra: uv sync --extra pdf)."""

import json
import sys
from dataclasses import replace
from datetime import date

import pytest
import yaml

from coach import catalogue
from coach import export as export_module
from coach.cli import main
from coach.profile import Profile, save_profile

TODAY = "2026-10-25"
FOOD = catalogue.CatalogueProduct(
    barcode="8400000000017",
    product_name="Comida de prueba",
    brand="Marca Prueba",
    chain="Mercadona",
    per="100 g",
    kcal=100,
    protein_g=8,
    carbs_g=12,
    fat_g=2.5,
    fibre_g=2,
    allergens=(),
    url="https://world.openfoodfacts.org/product/8400000000017",
    fetched_on=date(2026, 10, 25),
)
COLD_CUT = catalogue.CatalogueProduct(
    barcode="8400000000024",
    product_name="Fiambre de prueba",
    brand="Marca Prueba",
    chain="Mercadona",
    per="100 g",
    kcal=150,
    protein_g=18,
    carbs_g=2,
    fat_g=8,
    fibre_g=None,
    allergens=(),
    url="https://world.openfoodfacts.org/product/8400000000024",
    fetched_on=date(2026, 10, 25),
)
STEW = {
    "dish": "Estofado de prueba",
    "source": "https://example.org/estofado-de-prueba",
    "servings": 2,
    "steps": ["Dorar la carne", "Cocer despacio"],
    "seasoning": ["laurel"],
    "items": ["Comida de prueba=1800"],
}


@pytest.fixture
def data_dir(tmp_path):
    save_profile(
        Profile(
            sex="female",
            birth_date=date(1992, 3, 10),
            height_cm=165,
            weight_kg=62,
            goal="maintenance",
            activity_level="desk",
            language="es",
            region="es",
            screening={"scoff_positive": False},
        ),
        tmp_path / "profile.yaml",
    )
    catalogue.save([FOOD, COLD_CUT], tmp_path)
    draft = {
        "days": [
            {
                "date": date(2026, 10, 26),
                "meals": [
                    {
                        "meal": "Comida",
                        "tupper": True,
                        "dishes": [dict(STEW)],
                    },
                    {"meal": "Cena", "free": True},
                ],
            },
            {
                "date": date(2026, 10, 27),
                "meals": [
                    {
                        "meal": "Desayuno",
                        "dishes": [{"dish": "Bocadillo de prueba", "items": ["8400000000024=150"]}],
                    },
                    {"meal": "Comida", "dishes": [dict(STEW)]},
                ],
            },
        ]
    }
    (tmp_path / "menu-draft.yaml").write_text(
        yaml.safe_dump(draft, allow_unicode=True), encoding="utf-8"
    )
    return tmp_path


def run(capsys, data_dir, *args):
    code = main(["--data-dir", str(data_dir), "--today", TODAY, *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def save(capsys, data_dir):
    code, out = run(capsys, data_dir, "mealplan", "save", "menu-draft.yaml", "--kcal", "2000")
    assert code == 0, out


def test_export_writes_a_pdf_next_to_the_saved_menu(capsys, data_dir):
    pytest.importorskip("reportlab")
    save(capsys, data_dir)
    code, out = run(capsys, data_dir, "mealplan", "export")
    assert code == 0 and out["pdf"] == "menus/2026-10-26.pdf" and out["days"] == 2
    data = (data_dir / "menus" / "2026-10-26.pdf").read_bytes()
    assert data.startswith(b"%PDF")
    # pages are not compressed, so the text and the recipe link can be found in the file
    assert b"Estofado de prueba" in data and b"https://example.org/estofado-de-prueba" in data
    assert b"Lista de la compra" in data and b"Dorar la carne" in data
    # the shopping list buys the batch once at its 2 servings: 3,600 g
    assert b"3600" in data or b"3.600" in data


def test_export_has_an_optional_qr_per_recipe(capsys, data_dir):
    pytest.importorskip("reportlab")
    save(capsys, data_dir)
    run(capsys, data_dir, "mealplan", "export", "--out", "con-qr.pdf")
    run(capsys, data_dir, "mealplan", "export", "--out", "sin-qr.pdf", "--no-qr")
    with_qr = (data_dir / "con-qr.pdf").stat().st_size
    without_qr = (data_dir / "sin-qr.pdf").stat().st_size
    assert with_qr > without_qr


def test_export_names_the_menu_or_takes_the_newest(capsys, data_dir):
    pytest.importorskip("reportlab")
    code, out = run(capsys, data_dir, "mealplan", "export")
    assert code == 2 and "mealplan save" in out["message"]
    save(capsys, data_dir)
    code, out = run(capsys, data_dir, "mealplan", "export", "menus/2026-10-26.yaml")
    assert code == 0


def test_export_in_english_uses_english_labels(capsys, data_dir):
    pytest.importorskip("reportlab")
    save(capsys, data_dir)
    run(capsys, data_dir, "profile", "set", "language", "en")
    run(capsys, data_dir, "mealplan", "export")
    data = (data_dir / "menus" / "2026-10-26.pdf").read_bytes()
    assert b"Shopping list" in data and b"Lista de la compra" not in data


def test_export_without_the_extra_says_how_to_install_it(capsys, data_dir, monkeypatch):
    save(capsys, data_dir)
    for name in [n for n in sys.modules if n == "reportlab" or n.startswith("reportlab.")]:
        monkeypatch.delitem(sys.modules, name)
    monkeypatch.setitem(sys.modules, "reportlab", None)  # as if it were not installed
    code, out = run(capsys, data_dir, "mealplan", "export")
    assert code == 2 and "uv sync --extra pdf" in out["message"]
    assert not (data_dir / "menus" / "2026-10-26.pdf").exists()


@pytest.mark.parametrize(
    "source,link",
    [
        ("https://example.org/receta", "https://example.org/receta"),
        ("http://example.org/receta", "http://example.org/receta"),
        ("javascript:alert(1)", None),
        ("file:///etc/passwd", None),
        ("https://", None),
        ("example.org/receta", None),
    ],
)
def test_only_web_addresses_become_links(source, link):
    from coach.export import web_link

    assert web_link(source) == link


def test_a_source_that_is_not_a_web_address_is_printed_without_a_link(capsys, data_dir):
    pytest.importorskip("reportlab")
    draft = yaml.safe_load((data_dir / "menu-draft.yaml").read_text(encoding="utf-8"))
    for day in draft["days"]:
        for meal in day["meals"]:
            for dish in meal.get("dishes") or []:
                if dish["dish"] == "Estofado de prueba":
                    dish["source"] = "javascript:alert(1)"
    (data_dir / "menu-draft.yaml").write_text(
        yaml.safe_dump(draft, allow_unicode=True), encoding="utf-8"
    )
    save(capsys, data_dir)
    run(capsys, data_dir, "mealplan", "export", "--out", "con-qr.pdf")
    run(capsys, data_dir, "mealplan", "export", "--out", "sin-qr.pdf", "--no-qr")
    data = (data_dir / "con-qr.pdf").read_bytes()
    assert b"javascript:alert" in data  # still printed as text (PDF escapes the brackets)
    assert b"/URI" not in data  # but never as a link
    # and no QR code either: the file is the same size as the one exported without QR codes
    assert len(data) == (data_dir / "sin-qr.pdf").stat().st_size


def export(capsys, data_dir) -> bytes:
    pytest.importorskip("reportlab")
    save(capsys, data_dir)
    code, _ = run(capsys, data_dir, "mealplan", "export")
    assert code == 0
    return (data_dir / "menus" / "2026-10-26.pdf").read_bytes()


def test_a_recipe_eaten_on_several_days_is_printed_once(capsys, data_dir):
    data = export(capsys, data_dir)
    assert data.count(b"Dorar la carne") == 1
    assert (
        data.count(b"/URI (https://example.org/estofado-de-prueba)") == 1
    )  # one link, not one a day


def test_the_week_overview_has_a_row_per_day(capsys, data_dir):
    data = export(capsys, data_dir)
    assert b"lun 26" in data and b"mar 27" in data


def test_missing_data_names_the_product_not_its_barcode(capsys, data_dir):
    data = export(capsys, data_dir)
    assert b"Fiambre de prueba" in data and b"8400000000024" not in data


def test_a_recipe_longer_than_a_page_still_exports(capsys, data_dir):
    pytest.importorskip("reportlab")
    draft = yaml.safe_load((data_dir / "menu-draft.yaml").read_text(encoding="utf-8"))
    for day in draft["days"]:
        for meal in day["meals"]:
            for dish in meal.get("dishes") or []:
                if dish["dish"] == "Estofado de prueba":
                    dish["steps"] = [f"Paso {n}: " + "remover despacio " * 30 for n in range(40)]
    (data_dir / "menu-draft.yaml").write_text(
        yaml.safe_dump(draft, allow_unicode=True), encoding="utf-8"
    )
    save(capsys, data_dir)
    code, out = run(capsys, data_dir, "mealplan", "export")
    assert code == 0, out
    data = (data_dir / "menus" / "2026-10-26.pdf").read_bytes()
    assert b"(40) Tj" in data and b"Paso 39" in data  # the last step is printed, not cut off


@pytest.mark.parametrize(
    "first, last, text",
    [
        (date(2026, 11, 2), date(2026, 11, 8), "2 – 8 de noviembre de 2026"),
        (date(2026, 10, 30), date(2026, 11, 5), "30 de octubre – 5 de noviembre de 2026"),
        (date(2025, 12, 29), date(2026, 1, 4), "29 de diciembre de 2025 – 4 de enero de 2026"),
        (date(2026, 11, 2), date(2026, 11, 2), "2 de noviembre de 2026"),
    ],
)
def test_the_date_range_names_the_month_and_year_only_where_they_change(first, last, text):
    assert export_module._date_range(first, last, export_module.LABELS["es"]) == text


def test_a_dish_without_a_recipe_still_prints_its_amounts(capsys, data_dir):
    data = export(capsys, data_dir)
    assert data.count(b"Bocadillo de prueba") == 2  # the week table and its card
    assert data.count(b"(150 g)") == 2  # the card and the shopping list


def test_a_breakfast_without_a_recipe_gets_a_full_card(capsys, data_dir):
    data = export(capsys, data_dir)
    # the label stands on its own line in every card, the stew's and the breakfast's, with each
    # amount on a line of its own below it (not run together on one line)
    assert data.count(rb"(1 raci\363n) Tj") == 2  # the PDF writes ó as \363


def test_a_meal_for_several_people_scales_its_card(capsys, data_dir):
    pytest.importorskip("reportlab")
    draft = yaml.safe_load((data_dir / "menu-draft.yaml").read_text(encoding="utf-8"))
    for day in draft["days"]:
        for meal in day["meals"]:
            if meal["meal"] == "Comida":
                meal["people"] = 2
    (data_dir / "menu-draft.yaml").write_text(
        yaml.safe_dump(draft, allow_unicode=True), encoding="utf-8"
    )
    data = export(capsys, data_dir)
    # the label says the amounts are 2 x the client's own portion (the PDF writes x as \327)
    assert rb"(para 2 personas \(2 \327 tu) Tj" in data
    assert b"(3600 g) Tj" in data  # 1,800 g a serving, for 2 people
    assert b"7200" in data or b"7.200" in data  # bought: 2 servings for 2 people
    run(capsys, data_dir, "profile", "set", "language", "en")
    run(capsys, data_dir, "mealplan", "export")
    assert rb"for 2 people \(2 \327 your" in (data_dir / "menus" / "2026-10-26.pdf").read_bytes()


def test_the_shopping_list_counts_whole_units_of_countable_foods(capsys, data_dir):
    pytest.importorskip("reportlab")
    draft = yaml.safe_load((data_dir / "menu-draft.yaml").read_text(encoding="utf-8"))
    breakfast = draft["days"][1]["meals"][0]["dishes"][0]
    breakfast["items"] = ["8400000000024=100", "huevo entero, crudo=100"]
    (data_dir / "menu-draft.yaml").write_text(
        yaml.safe_dump(draft, allow_unicode=True), encoding="utf-8"
    )
    data = export(capsys, data_dir)
    assert b"(aprox. 2 ud. grandes) Tj" in data  # 100 g of 50 g large eggs
    run(capsys, data_dir, "profile", "set", "language", "en")
    run(capsys, data_dir, "mealplan", "export")
    assert b"(about 2 large) Tj" in (data_dir / "menus" / "2026-10-26.pdf").read_bytes()


def test_the_shopping_list_counts_whole_packs(capsys, data_dir):
    pytest.importorskip("reportlab")
    products = catalogue.load(data_dir)
    catalogue.save(
        [replace(p, pack_size=60) if p.barcode == "8400000000024" else p for p in products],
        data_dir,
    )
    draft = yaml.safe_load((data_dir / "menu-draft.yaml").read_text(encoding="utf-8"))
    draft["days"][1]["meals"][0]["dishes"][0]["items"] = [
        "8400000000024=100",
        "huevo entero, crudo=100",
    ]
    (data_dir / "menu-draft.yaml").write_text(
        yaml.safe_dump(draft, allow_unicode=True), encoding="utf-8"
    )
    data = export(capsys, data_dir)
    assert b"(2 envases de 60 g) Tj" in data
