# Adding a region

A region tells the coach what people there eat, where they shop and which number to call in an
emergency. Spain (`regions/es/`) is the first one. The profile's `region` field picks the layer;
`/menu`, `coach menu` and `coach safety` read it.

## Do you need one?

Not to start. Without a region the coach still works everywhere: every number, the training and
safety rules, menus from the general food table (`foods/base.csv`), and your own supermarket
products from Open Food Facts, which covers most countries:

```
uv run python -m coach products search WORD --brand BRAND --json
uv run python -m coach products add BARCODE --chain "YOUR SHOP" --json
```

Those products go into your private catalogue in the data folder and work in `/menu` and the
shopping list like any other food. `/setup` asks for your emergency number when there is no
region and stores it in your profile.

Add a region when you want what is specific to a country: foods the general table lacks, the
local supermarket chains and their own brands (`/menu` accepts any chain, but the region documents
which ones exist and what their websites allow), and the emergency number for everyone who picks
that region.

## Checklist

1. Copy `regions/es/` to `regions/<code>/` (two-letter country code) and edit `region.yaml`,
   including `emergency_number`.
2. Replace `foods_ids.tsv` and rebuild `foods.csv` (below), or leave both empty with the header.
3. Leave `products.csv` with only its header unless you have rows you may publish (below).
4. Rewrite the region's `README.md`: sources, coverage, what each chain's website allows.
5. In `.claude/skills/setup/SKILL.md`, step 1, name the new region next to `region es`.
6. Run `uv run pytest`: the region tests pick up the new folder.

The coach speaks Spanish and English only. A region in another language works, but the
conversation, the deferral line in `docs/safety.md`, the PDF labels in `coach/export.py` and the
food names (`name_en`, `name_es`) stay in those two languages; adding a language means extending
all four.

## Files

```
regions/<code>/
  region.yaml        code, name, default language, units, chains and their own brands
  foods.csv          regional foods missing from foods/base.csv (same columns)
  foods_ids.tsv      the FoodData Central matches foods.csv is built from
  products.csv       own-brand products with label values (optional)
  README.md          sources, coverage and anything a reviewer should know
```

`<code>` is the two-letter country code. Copy `regions/es/` as a template.

### region.yaml

```yaml
code: mx
name: México
default_language: es         # es or en: the languages the coach speaks
emergency_number: "911"      # quoted, digits only; coach safety prints it
units: {mass: kg, energy: kcal, decimal_separator: "."}
food_sources: [fdc_sr_legacy]
chains:
  - name: Soriana
    website: https://www.soriana.com
    own_brands: [Soriana]
    products_verified: 0     # must equal the chain's rows in products.csv
```

### foods.csv

Same columns as `foods/base.csv` (see `foods/README.md`). Never type numbers: list the foods in
`foods_ids.tsv` (name_en, name_es, fdc_id, fdc_description, form_note) and build:

```
uv run python scripts/build_food_table.py --fdc-dir <SR Legacy release> \
    --ids regions/<code>/foods_ids.tsv --out regions/<code>/foods.csv
```

Names must not repeat a name in `foods/base.csv`, in either language (`load_foods` refuses
duplicates). Add a second-language column only if the coach is extended to that language; the
current tables carry English and Spanish names. A national food composition database can replace
FDC for a region if it has a machine-readable release: add a `source` value for it, record the
database's own food ID in `source_id`, and extend `scripts/build_food_table.py` to read it.

### products.csv

Columns: `chain, brand, product_name, category, per, kcal, protein_g, carbs_g, sugars_g, fat_g,
fibre_g, url, checked_on, label_quote`.

- **No opened page, no row.** Every row comes from the chain's own product page, opened and read.
  Search snippets, comparison sites and memory do not count; nothing is estimated.
- **No scraping, no prices.** Open a handful of pages; never work around bot protection. If a
  chain blocks automated reads, leave it at 0 rows and say so in the README; a person can add rows
  from a browser.
- **Publish only what the chain allows.** Rows copied from a chain's website can stay in your
  private copy, but only go into a public repo or a pull request if the chain's terms of use
  allow redistributing that data. That is why Spain's `products.csv` ships empty. Open Food
  Facts products (above) are the shareable alternative.
- `per` is `100 g` or `100 ml`; leave `sugars_g` or `fibre_g` blank when the label omits them.
  A product per 100 ml is a menu item in millilitres (`NAME=15ml`), a product per 100 g in grams;
  the coach has no densities and never converts or mixes the two.
- `label_quote` is a verbatim snippet containing the values; the tests check that each recorded
  number appears in it as a whole number token.
- Open Food Facts never fills this file. Clients add the products they buy from OFF to their own
  catalogue in the data directory (`coach products add`), labelled unverified; see
  `regions/es/README.md`.

## Tests

`tests/coach/test_food_tables.py` and the parametrised tests in `tests/coach/test_regions.py`
pick up every folder with a `region.yaml`: every food row sourced and energy-checked, names
unique across foods and products, products citing a page and their label, `products_verified`
matching the rows. Add region-specific checks (like `test_spain_region_file`) by hand. Run
`uv run pytest`.
