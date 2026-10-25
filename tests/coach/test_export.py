"""PDF export of a saved menu (needs the optional `pdf` extra: uv sync --extra pdf)."""

import json
import sys
from datetime import date

import pytest
import yaml

from coach import catalogue
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
    catalogue.save([FOOD], tmp_path)
    draft = {
        "days": [
            {
                "date": date(2026, 10, 26),
                "meals": [
                    {
                        "meal": "Comida",
                        "tupper": True,
                        "dishes": [
                            {
                                "dish": "Estofado de prueba",
                                "source": "https://example.org/estofado-de-prueba",
                                "servings": 2,
                                "steps": ["Dorar la carne", "Cocer despacio"],
                                "seasoning": ["laurel"],
                                "items": ["Comida de prueba=1800"],
                            }
                        ],
                    },
                    {"meal": "Cena", "free": True},
                ],
            }
        ]
    }
    (tmp_path / "menu-draft.yaml").write_text(yaml.safe_dump(draft, allow_unicode=True))
    return tmp_path


def run(capsys, data_dir, *args):
    code = main(["--data-dir", str(data_dir), "--today", TODAY, *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def save(capsys, data_dir):
    code, _ = run(capsys, data_dir, "mealplan", "save", "menu-draft.yaml", "--kcal", "2000")
    assert code == 0


def test_export_writes_a_pdf_next_to_the_saved_menu(capsys, data_dir):
    pytest.importorskip("reportlab")
    save(capsys, data_dir)
    code, out = run(capsys, data_dir, "mealplan", "export")
    assert code == 0 and out["pdf"] == "menus/2026-10-26.pdf" and out["days"] == 1
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
    draft = yaml.safe_load((data_dir / "menu-draft.yaml").read_text())
    dish = draft["days"][0]["meals"][0]["dishes"][0]
    dish["source"] = "javascript:alert(1)"
    (data_dir / "menu-draft.yaml").write_text(yaml.safe_dump(draft, allow_unicode=True))
    save(capsys, data_dir)
    run(capsys, data_dir, "mealplan", "export", "--out", "con-qr.pdf")
    run(capsys, data_dir, "mealplan", "export", "--out", "sin-qr.pdf", "--no-qr")
    data = (data_dir / "con-qr.pdf").read_bytes()
    assert b"javascript:alert" in data  # still printed as text (PDF escapes the brackets)
    assert b"/URI" not in data  # but never as a link
    # and no QR code either: the file is the same size as the one exported without QR codes
    assert len(data) == (data_dir / "sin-qr.pdf").stat().st_size
