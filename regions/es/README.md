# Spain (es)

- `region.yaml`: language, units, the six chains the coach knows and their own brands.
- `foods.csv`: Spain-typical foods not in `foods/base.csv` (pulpo, boquerones, morcilla, sepia,
  rape, habas...), per 100 g, built from FoodData Central SR Legacy by `fdcId` like the base table
  (`foods_ids.tsv` lists the matches).
- `products.csv`: own-brand products with the values printed on their labels, per 100 g, each
  with the product page it was read from (`url`), the date (`checked_on`) and a verbatim quote of
  the label (`label_quote`). No prices. Empty in this template: no chain's terms of use clearly
  allow its product data to be redistributed, so rows read from a chain's website stay in your
  private copy (or use the Open Food Facts catalogue below, whose data is openly licensed).

## Rules for products

- **No opened page, no row.** A value is only recorded when it was read on the chain's own product
  page. Search-engine snippets and third-party sites do not count, and nothing is estimated.
- **No scraping.** A handful of individual product pages are opened one at a time (an automated
  page fetch, not a crawler); bot protection is never worked around.
- `/menu` may use a web search to confirm that a product is still sold. It never fetches prices.

## The client's own products (Open Food Facts)

These rules cover `products.csv` only. Products a client buys that are not listed here go into a
personal catalogue in the data directory (`data/catalogue.csv`, gitignored), read from Open Food
Facts by barcode with `coach products add BARCODE --chain CHAIN`. `coach products search WORD
--brand BRAND` finds the barcode. Those rows are crowd-sourced, so each one says `Open Food Facts
(unverified)` and keeps the OFF page URL and the fetch date. A value OFF lacks stays blank and the
menu shows it as missing; it is never filled with zero or an estimate. OFF requires a contact
email in the User-Agent, so the commands need `COACH_OFF_CONTACT` set (under `env` in
`.claude/settings.local.json`; the README's Settings section shows how). Prices are never fetched.
Open Food Facts data is under the Open Database License (ODbL), and the row's URL is its
attribution. Catalogue rows never move into `products.csv`.

Coverage varies: many basic own-brand products are in OFF, often without a fibre value, while
some frozen ready meals are not.

## What each chain's website allows (checked 2026-10-24)

| Chain | Rows | Why |
|---|---|---|
| Eroski | 0 | product pages show the nutrition table as text, but the site's terms do not clearly allow redistributing it, so the rows were left out of the template |
| Mercadona | 0 | pages show no values as text; values are only in label photos behind the shop's internal API, which needs a browser identity to answer. Not used. |
| Lidl | 0 | product pages show nutrition only as images, or no longer exist |
| Carrefour | 0 | every page answers 403 to automated reads |
| Dia | 0 | every page answers 403 to automated reads |
| Alcampo | 0 | every page answers 403 to automated reads |

To add products in your private copy, open the product page in a browser, copy the per-100 g
values from the label and fill a row with the page URL, the date and the label text; set the
chain's `products_verified` in `region.yaml` to its row count. Do not publish rows copied from a
chain's website unless its terms allow it.

## Seasonal produce (not built yet: contributions welcome)

Status on 2026-10-25: no `season.csv` is shipped, and there is no `coach foods season` command or
/menu step yet. The ministry's own fruit and vegetable calendar (Ministerio de Agricultura, Pesca y
Alimentación, MAPA) is the intended source, but its terms of reuse could not be verified:

- The calendar page is <https://www.mapa.gob.es/es/alimentacion/temas/fruta-verdura-temporada>;
  search results list two PDF calendars under `/es/alimentacion/temas/desperdicio/`
  (`12calendario_frutas_completo_tcm30-623768.pdf`, `11calendario_verduras_completo_tcm30-623767.pdf`).
- The site could not be fetched with certificate checks on when this was written, so neither the
  calendars nor the legal notice (aviso legal) were read, and no month was recorded from memory or
  from third-party pages.
- Spanish state bodies usually publish under the general reuse conditions of Ley 37/2007 (reuse
  allowed, commercial or not, with attribution), but that is the pattern of other ministries; the
  MAPA notice itself is unchecked. The "Soy de temporada" app listed on datos.gob.es is CC BY-NC
  4.0, which does not fit a template that others may reuse commercially, so it is not a source.
- A press check (Maldita, 2025) says MAPA's calendar does not tell open-air from greenhouse crops,
  so "in season" would mean "harvested and sold in Spain", not "grown outdoors".

How to contribute it:

1. Open the aviso legal and confirm the reuse terms; record the URL, the date checked and the
   terms in this README.
2. Read the months from the two calendars (facts only; do not copy the layout or text) into
   `regions/es/season.csv`: `name_es` (matching a `foods/` or `regions/es/foods.csv` name where one
   exists), `kind` (`fruit` or `vegetable`), `months` (`1;2;12`), `source_url`, `checked_on`.
3. Add `coach foods season [--month M]` (default: the month of `--today`) listing the foods in
   season, and a /menu step that prefers produce in season for the menu dates and names the month
   it used. A test must check that every `name_es` resolves to a table food or is marked
   `no_table_entry`, and that every month is 1 to 12.
