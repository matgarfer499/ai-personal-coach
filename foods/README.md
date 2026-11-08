# Food tables

`base.csv` lists common foods, per 100 g, with their source. Regional foods live in
`regions/<code>/foods.csv` with the same columns, and regional own-brand products in
`regions/<code>/products.csv`. Each client can also add the products they buy from Open Food
Facts to a personal catalogue in the data directory (`coach products add`; see
`regions/es/README.md`). Menus find all of them by exact name, and catalogue products by barcode
too. A blank value is missing: menu totals list the items that lack it and never count it as zero.

| Column | Meaning |
|---|---|
| `name_en`, `name_es` | names the coach accepts (exact match, any case) |
| `kcal`, `protein_g`, `fat_g`, `fibre_g` | per 100 g, as the source gives them; `fibre_g` is blank when the source has no value (then `carbs_g` is total carbohydrate and `form_note` says so) |
| `carbs_g` | available carbohydrate: the source's carbohydrate by difference minus fibre, as on EU labels |
| `source`, `source_id` | `fdc_sr_legacy` and the FoodData Central `fdcId` |
| `source_description` | the source's own name for the food, to judge the match |
| `form_note` | how the match differs from the name (closest form, variety, salt) |
| `kcal_exception` | set when stated energy is more than 10% from the 4/4/9 (+2 for fibre) energy, measured against that computed value |
| `g_per_ml` | liquids only: grams in one millilitre, so `NAME=300ml` works for a per 100 g row |
| `unit_name`, `unit_g` | countable foods only: the source's portion name (`large` for an egg, `medium` for an apple) and its grams, so `coach shopping` can add about how many units the grams make |
| `food_group` | the source's food category (`Fruits and Fruit Juices`, `Vegetables and Vegetable Products`, ...); menu checks count the day's vegetables and fruit from it |

## Where the numbers come from

Source and licence: U.S. Department of Agriculture, Agricultural Research Service. FoodData
Central, SR Legacy (https://fdc.nal.usda.gov/). FoodData Central data are in the public domain
(CC0 1.0); cite USDA as the source when you reuse these tables.

Every number comes from USDA FoodData Central, SR Legacy, by `fdcId`. SR Legacy was frozen at its
April 2018 release, so that release is what FDC serves today. `scripts/build_food_table.py`
fills the numbers from the release's CSV files; nothing is typed by hand. A spot check of 10 IDs
against the live FDC API matched every value within the API's one-decimal rounding (2026-10-24).

To change or add a food, edit `base_ids.tsv` (name_en, name_es, fdc_id, fdc_description,
form_note, and the optional `liquid`, `fibre_zero` and `unit` columns), download the release (link in the script's docstring) and rebuild:

```
uv run python scripts/build_food_table.py --fdc-dir <release dir> --ids foods/base_ids.tsv --out foods/base.csv
```

The build stops if an `fdc_id` does not exist, if its description differs from the one you wrote,
or if energy, protein, fat or carbohydrate is missing, or if a `liquid: yes` row has no cup, fl oz
or tbsp portion, or if a `unit` names no portion of that food or more than one.

Liquids: a row marked `liquid: yes` gets `g_per_ml` from the release's own portion weight (cup,
else fl oz, else tbsp, divided by the exact US volume). Milks, juices, broth, soy sauce, coconut
milk and kefir are marked; oils are not, they stay in grams. Each density comes from one SR
portion, so it is approximate (coconut milk and kefir most of all). Caldo de pastilla is the
made-up broth: enter ml (or g) of prepared broth, never the dry cube.

Units: a row's optional `unit` names one of the release's own portions (food_portion.csv) by its
modifier, cut before any " (" as for densities: `large` for eggs, `medium` for an apple, banana,
carrot or onion, `fruit` for an orange, kiwi or plum, `clove` for garlic. The build writes it as
`unit_name` and the portion's `gram_weight / amount` as `unit_g`. Only foods bought by the piece
carry one, and only when the release has exactly one portion of that name.

Food group: every row's `food_group` is the release's category for its `fdcId` (food.csv
`food_category_id`, named in food_category.csv). The day's vegetables and fruit (nutrition.md
"Dietary fibre": at least 400 g) count the rows in "Vegetables and Vegetable Products" and
"Fruits and Fruit Juices", except potatoes and other starchy roots (a convention, see
`docs/conventions.md`). Products have no group and count 0.

BEDCA (the Spanish food composition database) was tried for Spanish staples; its public query
endpoint answered searches but returned no nutrient values, so this version uses FDC only.
Seitan and skyr are missing because SR Legacy has no entry for them.

Fibre is blank for some foods because SR Legacy gives no value; it is never filled in by hand.
The one exception is a row marked `fibre_zero: animal`: dietary fibre is plant carbohydrate, so
unprocessed meat, fish, shellfish and eggs carry 0 g, and the build writes 0 where the source is
blank and adds "fibre 0: animal food (convention)" to `form_note`. Prawns are one: the plain raw
shrimp entry (175179) has no fibre value, and the only shrimp entries that do (174210, 171971,
171972: 0 g) are other products ("may contain additives to retain moisture", moist-heat cooked,
canned) whose energy and protein differ, so they are not used as a stand-in. Tempeh and canned
coconut milk stay blank (plant foods).
