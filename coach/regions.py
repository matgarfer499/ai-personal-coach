"""Region layer: regions/<code>/region.yaml and regions/<code>/products.csv."""

from __future__ import annotations

import csv
from dataclasses import dataclass
from datetime import date
from pathlib import Path

import yaml

from coach import catalogue
from coach.foods import PER_UNITS, ROOT, Food, check_unique, load_foods

PRODUCT_FIELDS = [
    "chain",
    "brand",
    "product_name",
    "category",
    "per",
    "kcal",
    "protein_g",
    "carbs_g",
    "sugars_g",
    "fat_g",
    "fibre_g",
    "url",
    "checked_on",
    "label_quote",
]


def _optional(value: str) -> float | None:
    return float(value) if value.strip() else None


@dataclass(frozen=True)
class Product:
    chain: str
    brand: str
    product_name: str
    category: str
    per: str
    kcal: float
    protein_g: float
    carbs_g: float
    sugars_g: float | None
    fat_g: float
    fibre_g: float | None  # None when the label does not list fibre
    url: str
    checked_on: date
    label_quote: str

    @classmethod
    def from_row(cls, row: dict) -> Product:
        return cls(
            chain=row["chain"],
            brand=row["brand"],
            product_name=row["product_name"],
            category=row["category"],
            per=row["per"],
            kcal=float(row["kcal"]),
            protein_g=float(row["protein_g"]),
            carbs_g=float(row["carbs_g"]),
            sugars_g=_optional(row["sugars_g"]),
            fat_g=float(row["fat_g"]),
            fibre_g=_optional(row["fibre_g"]),
            url=row["url"],
            checked_on=date.fromisoformat(row["checked_on"]),
            label_quote=row["label_quote"],
        )

    def as_food(self) -> Food:
        """The product as a food per 100 g or per 100 ml, as its label says: menu items for it
        are written in that unit and never converted (the coach has no densities)."""
        per = self.per.strip()
        if per not in PER_UNITS:
            raise ValueError(
                f"{self.product_name}: label is per {self.per}, not per 100 g or per 100 ml"
            )
        return Food(
            name_en=self.product_name,
            name_es=self.product_name,
            kcal=self.kcal,
            protein_g=self.protein_g,
            carbs_g=self.carbs_g,
            fat_g=self.fat_g,
            fibre_g=self.fibre_g,  # None stays missing
            source=f"label:{self.chain}",
            source_id=self.url,
            chain=self.chain,
            per=per,
        )


def region_dir(code: str, root: Path = ROOT) -> Path:
    path = root / "regions" / code
    if not (path / "region.yaml").exists():
        raise ValueError(f"unknown region {code!r}: no regions/{code}/region.yaml")
    return path


def load_region(code: str, root: Path = ROOT) -> dict:
    return yaml.safe_load((region_dir(code, root) / "region.yaml").read_text(encoding="utf-8"))


def emergency_number(code: str | None, root: Path = ROOT) -> str | None:
    """The region's emergency number, or None with no region."""
    return str(load_region(code, root)["emergency_number"]) if code else None


def load_products(code: str, root: Path = ROOT) -> list[Product]:
    path = region_dir(code, root) / "products.csv"
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return [Product.from_row(r) for r in csv.DictReader(handle)]


def menu_table(region: str | None, root: Path = ROOT, data_dir: Path | None = None) -> list[Food]:
    """Foods plus the region's products per 100 g or 100 ml (and the client's catalogue in
    `data_dir`), with every name unique."""
    table = load_foods(region, root)
    if region:
        table += [p.as_food() for p in load_products(region, root) if p.per.strip() in PER_UNITS]
    if data_dir is not None:
        table += catalogue.menu_foods(data_dir)
    check_unique(table)
    return table
