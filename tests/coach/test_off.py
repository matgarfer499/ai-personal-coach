import io
import json
import urllib.error
import urllib.parse
from pathlib import Path

import pytest

from coach import off

FIXTURES = Path(__file__).parent.parent / "fixtures" / "off"


def fixture(name):
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


@pytest.fixture
def contact(monkeypatch):
    monkeypatch.setenv(off.CONTACT_ENV, "tester@example.org")


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def test_user_agent_needs_the_contact(monkeypatch):
    monkeypatch.delenv(off.CONTACT_ENV, raising=False)
    with pytest.raises(ValueError, match=off.CONTACT_ENV):
        off.user_agent()
    monkeypatch.setenv(off.CONTACT_ENV, "tester@example.org")
    assert off.user_agent() == "ai-personal-coach/0.1.0 (tester@example.org)"


def test_get_json_sends_the_user_agent(monkeypatch, contact):
    seen = {}

    def urlopen(request, timeout):
        seen["agent"] = request.get_header("User-agent")
        seen["timeout"] = timeout
        return FakeResponse(b'{"status": "success"}')

    monkeypatch.setattr(off.urllib.request, "urlopen", urlopen)
    assert off._get_json("https://example.org/x") == {"status": "success"}
    assert seen == {"agent": off.user_agent(), "timeout": off.OFF_TIMEOUT_S}


def http_error(code, body=b""):
    return urllib.error.HTTPError("https://example.org", code, "error", {}, io.BytesIO(body))


def test_get_json_reads_the_body_of_a_404(monkeypatch, contact):
    body = (FIXTURES / "product_not_found.json").read_bytes()

    def urlopen(request, timeout):
        raise http_error(404, body)

    monkeypatch.setattr(off.urllib.request, "urlopen", urlopen)
    assert off._get_json("https://example.org/x")["status"] == "failure"


@pytest.mark.parametrize("code, message", [(503, "wait a minute"), (500, "500")])
def test_get_json_server_errors(monkeypatch, contact, code, message):
    def urlopen(request, timeout):
        raise http_error(code)

    monkeypatch.setattr(off.urllib.request, "urlopen", urlopen)
    with pytest.raises(ValueError, match=message):
        off._get_json("https://example.org/x")


def test_get_json_network_failure(monkeypatch, contact):
    def urlopen(request, timeout):
        raise urllib.error.URLError("no route")

    monkeypatch.setattr(off.urllib.request, "urlopen", urlopen)
    with pytest.raises(ValueError, match="could not reach Open Food Facts"):
        off._get_json("https://example.org/x")


def fake_get(responses, calls):
    def get(url):
        calls.append(url)
        return fixture(responses[0] if len(responses) == 1 else responses.pop(0))

    return get


def test_product_reads_the_five_values(monkeypatch):
    calls = []
    monkeypatch.setattr(off, "_get_json", fake_get(["product_found.json"], calls))
    product = off.product("8400000000017")
    assert calls[0].startswith(off.PRODUCT_URL.format(barcode="8400000000017") + "?fields=")
    assert product["name"] == "Salteado campestre"
    assert product["brand"] == "Marca Prueba" and product["stores"] == "Super Prueba"
    assert product["per"] == "100 g"
    assert product["values"] == {
        "kcal": 81,
        "protein_g": pytest.approx(1.7),
        "carbs_g": 15.5,
        "fat_g": 0.5,
        "fibre_g": 2.4,
    }
    assert product["missing"] == [] and product["allergens"] == []
    assert product["url"] == "https://world.openfoodfacts.org/product/8400000000017"


def test_product_missing_value_is_none_never_zero(monkeypatch):
    monkeypatch.setattr(off, "_get_json", fake_get(["product_missing_fibre.json"], []))
    product = off.product("8400000000024")
    assert product["values"]["fibre_g"] is None
    assert product["missing"] == ["fibre_g"]
    assert product["allergens"] == ["en:gluten"]


def test_product_volume_and_unknown_unit(monkeypatch):
    monkeypatch.setattr(off, "_get_json", fake_get(["product_liquid.json"], []))
    assert off.product("8400000000031")["per"] == "100 ml"
    monkeypatch.setattr(off, "_get_json", fake_get(["product_no_unit.json"], []))
    product = off.product("8400000000048")
    assert product["per"] is None and product["name"] is None


def test_product_impossible_values_are_missing_and_text_is_cleaned(monkeypatch):
    monkeypatch.setattr(off, "_get_json", fake_get(["product_bad_values.json"], []))
    product = off.product("8400000000055")
    # Over 900 kcal or 100 g per 100 g, negative, or not a number: recorded as missing.
    assert product["values"] == {
        "kcal": None,
        "protein_g": None,
        "carbs_g": None,
        "fat_g": 50,
        "fibre_g": None,
    }
    assert "\n" not in product["name"]
    assert product["brand"] == "Marca Prueba"


def test_product_not_found(monkeypatch):
    monkeypatch.setattr(off, "_get_json", fake_get(["product_not_found.json"], []))
    assert off.product("8400000000062") is None


@pytest.mark.parametrize("barcode", ["123", "84000000000170000", "84a0000000017", ""])
def test_product_rejects_a_malformed_barcode(barcode):
    with pytest.raises(ValueError, match="barcode"):
        off.product(barcode)


def test_search_builds_a_text_and_brand_query(monkeypatch):
    calls = []
    monkeypatch.setattr(off, "_get_json", fake_get(["search.json"], calls))
    hits = off.search(["revuelto", "rústico"], brand="Hacendado", limit=5, language="es")
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(calls[0]).query)
    assert calls[0].startswith(off.SEARCH_URL + "?")
    assert query["q"] == ['revuelto rústico brands:"hacendado"']
    assert query["langs"] == ["es,en"] and query["page_size"] == ["5"]
    assert [h["barcode"] for h in hits] == ["8400000000017", "8400000000024"]
    assert hits[1]["missing"] == ["fibre_g"] and hits[1]["brand"] == "Marca Prueba"


def test_search_strips_query_syntax_from_words(monkeypatch):
    calls = []
    monkeypatch.setattr(off, "_get_json", fake_get(["search.json"], calls))
    off.search(['pollo"', "brands:x", "(asado)"], brand='a" OR b')
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(calls[0]).query)
    assert query["q"] == ['pollo brands x asado brands:"a or b"']
    assert query["page_size"] == [str(off.SEARCH_LIMIT)]
