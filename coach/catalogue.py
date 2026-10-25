"""The client's personal product catalogue: data/catalogue.csv.

Products the client buys, read from Open Food Facts by barcode (`coach products add`). OFF is
crowd-sourced, so every row says "Open Food Facts (unverified)"; `regions/<code>/products.csv`
keeps its own stricter rule (values read on the chain's page). A blank value is missing, never
zero. A product is per 100 g or per 100 ml; menu items for it are written in that unit (`NAME=200`
or `NAME=15ml`) and never converted, because the coach has no densities.
"""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from coach.foods import NUMBERS, PER_UNITS, Food

SOURCE = "Open Food Facts (unverified)"
FILE = "catalogue.csv"
FIELDS = [
    "barcode",
    "product_name",
    "brand",
    "chain",
    "per",
    *NUMBERS,
    "allergens",
    "url",
    "fetched_on",
    "source",
]


@dataclass(frozen=True)
class CatalogueProduct:
    barcode: str
    product_name: str
    brand: str
    chain: str
    per: str
    kcal: float | None
    protein_g: float | None
    carbs_g: float | None
    fat_g: float | None
    fibre_g: float | None
    allergens: tuple[str, ...]
    url: str
    fetched_on: date
    source: str = SOURCE

    @classmethod
    def from_row(cls, row: dict) -> CatalogueProduct:
        numbers = {n: float(row[n]) if row[n].strip() else None for n in NUMBERS}
        return cls(
            barcode=row["barcode"],
            product_name=row["product_name"],
            brand=row["brand"],
            chain=row["chain"],
            per=row["per"],
            **numbers,
            allergens=tuple(a for a in row["allergens"].split(";") if a),
            url=row["url"],
            fetched_on=date.fromisoformat(row["fetched_on"]),
            source=row["source"],
        )

    def to_row(self) -> dict:
        def number(value: float | None) -> str:
            # 6 significant digits drop OFF's float noise (1.70000004768372 -> 1.7).
            return "" if value is None else f"{value:g}"

        return {
            "barcode": self.barcode,
            "product_name": self.product_name,
            "brand": self.brand,
            "chain": self.chain,
            "per": self.per,
            **{n: number(getattr(self, n)) for n in NUMBERS},
            "allergens": ";".join(self.allergens),
            "url": self.url,
            "fetched_on": self.fetched_on.isoformat(),
            "source": self.source,
        }

    def missing(self) -> list[str]:
        return [n for n in NUMBERS if getattr(self, n) is None]

    def as_food(self) -> Food:
        return Food(
            name_en=self.product_name,
            name_es=self.product_name,
            **{n: getattr(self, n) for n in NUMBERS},
            source=self.source,
            source_id=self.url,
            barcode=self.barcode,
            chain=self.chain,
            per=self.per,
        )


def load(data_dir: Path) -> list[CatalogueProduct]:
    path = Path(data_dir) / FILE
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [CatalogueProduct.from_row(r) for r in csv.DictReader(handle)]


def save(products: list[CatalogueProduct], data_dir: Path) -> None:
    path = Path(data_dir) / FILE
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS)
        writer.writeheader()
        writer.writerows(p.to_row() for p in products)


def menu_foods(data_dir: Path) -> list[Food]:
    """Catalogue products a menu can count: labelled per 100 g or per 100 ml."""
    return [p.as_food() for p in load(data_dir) if p.per in PER_UNITS]
