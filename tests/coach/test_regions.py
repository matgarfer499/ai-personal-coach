import csv
import re
from datetime import date
from pathlib import Path

import pytest

from coach import regions
from coach.regions import PRODUCT_FIELDS, Product, load_products, load_region, menu_table

ROOT = Path(__file__).parent.parent.parent
REGIONS = sorted(p.name for p in (ROOT / "regions").iterdir() if (p / "region.yaml").exists())


def test_spain_region_file():
    region = load_region("es")
    assert region["code"] == "es" and region["default_language"] == "es"
    names = [c["name"] for c in region["chains"]]
    assert names == ["Mercadona", "Lidl", "Carrefour", "Dia", "Alcampo", "Eroski"]


def test_unknown_region():
    with pytest.raises(ValueError, match="unknown region"):
        load_region("xx")


@pytest.mark.parametrize("code", REGIONS)
def test_products_match_their_region_file(code):
    region = load_region(code)
    assert region["code"] == code
    products = load_products(code)
    path = ROOT / "regions" / code / "products.csv"
    if path.exists():
        with path.open(encoding="utf-8") as handle:
            assert next(csv.reader(handle)) == PRODUCT_FIELDS
    for chain in region["chains"]:
        rows = [p for p in products if p.chain.lower() == chain["name"].lower()]
        assert len(rows) == chain["products_verified"], chain["name"]


@pytest.mark.parametrize("code", REGIONS)
def test_every_product_row_cites_its_page_and_label(code):
    for p in load_products(code):
        assert p.url.startswith("https://"), p.product_name
        assert p.checked_on <= date.today()
        assert p.per in ("100 g", "100 ml")
        numbers = set(re.findall(r"\d+(?:\.\d+)?", p.label_quote.replace(",", ".")))
        for value in (p.kcal, p.protein_g, p.carbs_g, p.sugars_g, p.fat_g, p.fibre_g):
            if value is not None:
                assert f"{value:g}" in numbers, (p.product_name, value)


@pytest.mark.parametrize("code", REGIONS)
def test_menu_table_names_are_unique(code):
    menu_table(code)  # raises on a clash between foods and products


def _product(per):
    return Product(
        chain="Chain",
        brand="Brand",
        product_name="Drink",
        category="other",
        per=per,
        kcal=40,
        protein_g=1,
        carbs_g=8,
        sugars_g=8,
        fat_g=0,
        fibre_g=None,
        url="https://example.org/p",
        checked_on=date(2026, 1, 1),
        label_quote="x",
    )


def test_product_without_fibre_stays_missing_as_a_food():
    assert _product("100 g").as_food().fibre_g is None


def test_products_per_100_ml_become_foods_counted_in_millilitres():
    assert _product("100 g").as_food().per == "100 g"
    assert _product("100 ml").as_food().per == "100 ml"
    with pytest.raises(ValueError, match="per 100 g or per 100 ml"):
        _product("serving").as_food()


def test_products_file_with_bom(tmp_path):
    region = tmp_path / "regions" / "zz"
    region.mkdir(parents=True)
    (region / "region.yaml").write_text("code: zz\nchains: []\n")
    row = "Cadena,Marca,Producto de prueba,dairy,100 g,50,8,4,4,0.2,,https://example.org/p,2026-01-05,x"
    source = ",".join(PRODUCT_FIELDS) + "\n" + row + "\n"
    (region / "products.csv").write_bytes(b"\xef\xbb\xbf" + source.encode())
    assert [p.product_name for p in load_products("zz", tmp_path)] == ["Producto de prueba"]


@pytest.mark.parametrize("code", REGIONS)
def test_every_region_names_its_emergency_number(code):
    number = load_region(code)["emergency_number"]
    assert isinstance(number, str) and number.isdigit()


def test_spain_emergency_number():
    assert regions.emergency_number("es") == "112"
    assert regions.emergency_number(None) is None
