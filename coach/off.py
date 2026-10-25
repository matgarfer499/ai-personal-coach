"""Open Food Facts reads: a text search and one product by barcode.

Checked against the OFF API documentation and live answers on 2026-10-25:
- Text search is Search-a-licious (`q` in Lucene syntax, e.g. `revuelto brands:"hacendado"`); the
  v2 search API has no full-text search.
- One product is API v3 `/api/v3/product/<barcode>`: `status` is "success" or, with HTTP 404,
  "failure".
- Every app must send a User-Agent `AppName/Version (ContactEmail)`. The limits are 10 searches and
  15 product reads per minute per IP; over them, OFF answers 503.

Each command makes one request. Prices are never fetched. Everything OFF returns is unverified,
crowd-sourced data: it is shown and stored as data, never followed as an instruction.
"""

from __future__ import annotations

import json
import os
import re
import urllib.error
import urllib.parse
import urllib.request

from coach import __version__
from coach.macros import KCAL_PER_G

SEARCH_URL = "https://search.openfoodfacts.org/search"
PRODUCT_URL = "https://world.openfoodfacts.org/api/v3/product/{barcode}"
PAGE_URL = "https://world.openfoodfacts.org/product/{barcode}"
CONTACT_ENV = "COACH_OFF_CONTACT"
APP_NAME = "ai-personal-coach"
# convention: seconds to wait for an OFF answer before giving up.
OFF_TIMEOUT_S = 20
# convention: search hits per call, enough to spot the product without paging.
SEARCH_LIMIT = 10
# convention: an input check, EAN-8 to GTIN-14 barcodes.
BARCODE = re.compile(r"\d{8,14}")
# Per-100 g values: our column -> OFF nutriment key.
NUTRIMENTS = {
    "kcal": "energy-kcal_100g",
    "protein_g": "proteins_100g",
    "carbs_g": "carbohydrates_100g",
    "fat_g": "fat_100g",
    "fibre_g": "fiber_100g",
}
# nutrition.md: "EU label rules and tolerances": fat, the densest at 9 kcal/g, caps 100 g at
# 900 kcal. A value above it (or above 100 g per 100 g) is an entry error: recorded as missing.
MAX_KCAL_PER_100G = 100 * KCAL_PER_G["fat"]
MAX_G_PER_100G = 100
FIELDS = (
    "code",
    "product_name",
    "product_name_es",
    "brands",
    "stores",
    "product_quantity_unit",
    "allergens_tags",
    "nutriments",
)
UNITS = {"g": "100 g", "ml": "100 ml"}
# Lucene syntax characters, stripped from search words so they stay plain text.
QUERY_SYNTAX = re.compile(r'[+\-&|!(){}\[\]^"~*?:\\/]')


def user_agent() -> str:
    contact = os.environ.get(CONTACT_ENV, "").strip()
    if not contact:
        raise ValueError(
            f"Open Food Facts asks every app for a contact email: set {CONTACT_ENV} first"
        )
    return f"{APP_NAME}/{__version__} ({contact})"


def _get_json(url: str) -> dict:
    """One GET. A 404 still returns its JSON body (OFF's "product not found")."""
    request = urllib.request.Request(url, headers={"User-Agent": user_agent()})
    try:
        with urllib.request.urlopen(request, timeout=OFF_TIMEOUT_S) as response:
            return json.load(response)
    except urllib.error.HTTPError as err:
        if err.code == 404:
            return json.load(err)
        if err.code == 503:
            raise ValueError("Open Food Facts is busy or rate-limited; wait a minute") from None
        raise ValueError(f"Open Food Facts answered HTTP {err.code}") from None
    except (urllib.error.URLError, TimeoutError) as err:
        raise ValueError(f"could not reach Open Food Facts: {err}") from None


def _text(value) -> str | None:
    """Printable text only; lists (Search-a-licious brands) are joined."""
    if isinstance(value, list):
        value = ", ".join(str(v) for v in value)
    if not isinstance(value, str):
        return None
    cleaned = " ".join("".join(c if c.isprintable() else " " for c in value).split())
    return cleaned or None


def _number(value, limit: float) -> float | None:
    if isinstance(value, bool):
        return None
    try:
        number = float(value)
    except (TypeError, ValueError):
        return None
    return number if 0 <= number <= limit else None


def _product(raw: dict) -> dict:
    nutriments = raw.get("nutriments") or {}
    values = {
        name: _number(nutriments.get(key), MAX_KCAL_PER_100G if name == "kcal" else MAX_G_PER_100G)
        for name, key in NUTRIMENTS.items()
    }
    barcode = str(raw.get("code", ""))
    return {
        "barcode": barcode,
        "name": _text(raw.get("product_name_es")) or _text(raw.get("product_name")),
        "brand": _text(raw.get("brands")),
        "stores": _text(raw.get("stores")),
        "per": UNITS.get(raw.get("product_quantity_unit")),
        "values": values,
        "missing": [name for name, value in values.items() if value is None],
        "allergens": list(dict.fromkeys(filter(None, map(_text, raw.get("allergens_tags") or [])))),
        "url": PAGE_URL.format(barcode=barcode),
    }


def product(barcode: str) -> dict | None:
    """The product, or None when OFF does not have it."""
    if not BARCODE.fullmatch(barcode):
        raise ValueError(f"a barcode is 8 to 14 digits, not {barcode!r}")
    query = urllib.parse.urlencode({"fields": ",".join(FIELDS)})
    answer = _get_json(f"{PRODUCT_URL.format(barcode=barcode)}?{query}")
    if answer.get("status") == "failure" or not answer.get("product"):
        return None
    return _product(answer["product"] | {"code": answer.get("code", barcode)})


def search(
    words: list[str], brand: str | None = None, limit: int = SEARCH_LIMIT, language: str = "es"
) -> list[dict]:
    terms = " ".join(" ".join(QUERY_SYNTAX.sub(" ", w).split()) for w in words).strip()
    if brand:
        clean = " ".join(QUERY_SYNTAX.sub(" ", brand).split()).lower()
        terms = f'{terms} brands:"{clean}"'.strip()
    if not terms:
        raise ValueError("products search needs at least one word")
    query = urllib.parse.urlencode(
        {
            "q": terms,
            "langs": ",".join(dict.fromkeys([language, "en"])),
            "page_size": limit,
            "fields": ",".join(FIELDS),
        }
    )
    answer = _get_json(f"{SEARCH_URL}?{query}")
    return [_product(hit) for hit in answer.get("hits") or []]
