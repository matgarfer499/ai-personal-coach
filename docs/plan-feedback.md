# Plan: tester feedback and open issues (2026-11-01)

Source: a tester ran /setup, /plan, /import and /menu and sent 19 numbered items. Items 10
(Lyfta importer) and 18 (CSV check-in import) are out of scope. This plan also decides every open
GitHub issue (#1 to #12). A separate unattended session implements it; this file is all it gets,
so each chunk below says what to change, which test fails first and how to check it.

Chunk status lives in GitHub: one PR per chunk, its title starting with the chunk ID, e.g.
`[C3] feat(coach): ...`. A chunk is done when its PR is merged.

## How every chunk is done

1. Branch from the latest `main` in a worktree. Read `CLAUDE.md` and `REVIEW.md` first.
2. Write the failing test named in the chunk, run it and watch it fail, then write the code.
3. Run the checks from `CLAUDE.md` ("## Checks") and paste their real output in the PR:
   `uv run pytest`, `uv run ruff check .`, `uv run ruff format --check .`, and for chunks that
   touch `knowledge/`, `uv run python scripts/check_knowledge.py` then
   `uv run python scripts/build_knowledge_index.py` and the check again.
4. One `/code-review medium --fix` pass (`high` for risk-path chunks R1 to R4). Use at most
   3 rounds; rounds 2 and 3 cover only the new diff.
5. The PR body has Testing, Risk and How to revert. Squash-merge green non-risk PRs without
   asking. Risk-path PRs (R1 to R4) stay open until Matías adds `human-ok`.
6. Rules that bind every chunk:
   - The privacy rule: fixtures are synthetic and written fresh. The tester's exercise names
     quoted in this plan are app library names, not personal data.
   - The constants rule: a new number cites its knowledge rule or is a `# convention:` listed
     in `docs/conventions.md`.
   - No en or em dashes in knowledge or skill files.
   - Recipe text never enters the repo; only ideas, ingredients and links do.
   - Kcal and macros come only from the coach CLI.
7. Skill text that cites a new CLI flag lands in the same PR as the flag.

## Why the risk-path chunks are separate

`.github/risk-paths` covers `coach/cli.py`, `coach/profile.py`, `coach/energy.py`,
`coach/macros.py`, `coach/safety.py`, `docs/safety.md`, `.github/` and `pyproject.toml`. Almost
every CLI feature would normally touch `coach/cli.py`. So the plan puts each feature's logic in
non-risk modules (`mealplan.py`, `strength.py`, `foods.py`, skills, data files) wherever the
existing CLI output already carries the result:
- Base repeats ride in the `repeats` list that `coach mealplan check` already prints.
- Eat-out meals and people ride in the draft that `coach shopping` already reads.
- The default rep range rides in the existing `--rep-range` flag.

Only four small risk-path chunks remain (R1 to R4). They come last and no other chunk depends on
them.

Possible follow-up for Matías, not in this plan: moving the non-safety commands out of
`coach/cli.py` would let most CLI work skip the human-ok gate. That change would itself be
risk-path work.

## Feedback items: where each goes

| Item | Summary | Chunk |
|---|---|---|
| 1 | PAR-Q+: link the Spanish PDF; flow for a PDF the client filled in | C5 |
| 2 | `emergency_number` not in `missing` | R2 |
| 3 | Returning lifter: ask whether the loads are from now or before | C5 |
| 4 | Activity level: 3-4 days falls between bands | C5 |
| 5 | `injury add --exercises` unmatched before any import; client does not know English names | C5 (setup text), C4 (aliases, re-check after /import) |
| 6 | No rules for heavy bag or functional training | C7 |
| 7 | `training_schedule` cannot say "fri or sat" | C2 |
| 8 | "Minimum effective dose" cites a heading that does not exist | C6 |
| 9 | Default rep range for every lift | C4 |
| 11 | Muscle map lacks Spanish Hevy and Lyfta names | C4 |
| 12 | Injury pause needs the exact Spanish Hevy name | C4 |
| 13 | Missing Spanish staples in the food table | C3 |
| 14 | Add a branded product by hand from its label | R3 |
| 15 | Eat-out meals end up on the shopping list; no cooking for two | C2 |
| 16 | Milk is per 100 g, so 300 ml must be written as 300 g | C3 |
| 17 | Output too long; summary table plus PDF by default | C2 |
| 19 | Windows: 7 failing tests; add windows-latest to CI | C8, R1 |
| Priority | Recipes are bland and repetitive; curated sources, flavour and variety rules | C1 |

None of the in-scope items is dropped. One judgement call for Matías is in C3: fibre 0 for
unprocessed animal foods reverses a decision in `foods/README.md` ("never filled in by hand").

## Open issues: decisions (nothing is closed in the planning session)

| # | Title | Decision |
|---|---|---|
| 1 | ACSM bands vs GETP 11th/12th | **Leave open.** Missing: the 11th and 12th editions are paywalled books; it needs someone with access, or a `/research` run that finds an open secondary source. |
| 2 | `no_training` still uses the activity level | **Implement in R4.** |
| 3 | Regenerate the dry runs in `docs/examples/` | **Leave open.** Missing: the final skill text. Run it in a follow-up session after R1 to R4 merge, or the dry runs go stale again. |
| 4 | `hold` and `paused` in a real `/plan` run | **Leave open.** Same follow-up session as #3 (record the runs as dry runs there). |
| 5 | `--rep-range` falls back silently | **Implement:** alias matching in C4, the unmatched list in R2. |
| 6 | `env` in `settings.local.json` reaches the commands | **Leave open.** Missing: a manual check in a fresh clone with a Claude Code restart, which an unattended session cannot do. R3 makes `COACH_OFF_CONTACT` optional for label entry. |
| 7 | Seasonal calendar for Spain | **Leave open.** Missing: MAPA's aviso legal could not be opened on 2026-11-01. The live page failed TLS (the FNMT root CA is not in the tool's trust store) and the old URLs return 404. A search snippet and the default regime of RD 1495/2011 suggest commercial reuse with attribution is allowed. Matías should open https://www.mapa.gob.es/es/atencion-al-ciudadano/aviso-legal in a browser and record the wording; the chunk can follow. When it is done, prefer a CSV the /menu skill reads directly (tested like C1's source list) over a new `coach foods season` command, which would be risk-path. |
| 8 | OFF nutrition basis vs pack unit | **Close as not planned, after a one-request check.** Fetch one drink labelled per 100 ml (for example a milk barcode) from `https://world.openfoodfacts.org/api/v3/product/<barcode>?fields=nutrition_data_per,product_quantity_unit`, the endpoint `coach/off.py` uses. If `nutrition_data_per` is `100g`, post the comment below. If it is `100ml`, implement the issue as written in a new non-risk chunk (`coach/off.py` only, with synthetic fixtures). |
| 9 | Shorten long quotes in `sources.md` | **Implement in C6.** |
| 10 | Imperial units | **Close as not planned.** |
| 11 | More languages | **Leave open.** Missing: a native speaker to write and review the deferral line for each new language. The safety text is copied exactly, so it cannot be machine-translated. |
| 12 | `/research` without the workflow runner | **Leave open.** Missing: a run in another agent (Codex, Gemini CLI or OpenCode), which this setup does not have. The SKILL.md description alone would be untested. |

Comment for #8 (to post when closing):

> Closing as not planned. Open Food Facts documents `nutrition_data_per` as `100g` or `serving`
> (https://openfoodfacts.github.io/documentation/docs/Product-Opener/schemas/schemas/product_nutrition/);
> only the v3.5 nutrition schema adds `100ml`. For a drink labelled per 100 ml, the product API
> the coach calls returned `100g` (checked on BARCODE, DATE). Comparing it with the pack unit
> would therefore flag every liquid. The existing `--per` and `--confirm-per` checks stay.
> Reopen when the API returns `100ml` for drinks.

Comment for #10 (to post when closing):

> Closing as not planned. The coach is Spain-first and no current client uses imperial units.
> Supporting them means changes in `coach/profile.py` and `coach/cli.py` (both risk paths) plus
> the skills. Reopen when a region with imperial units is added; the design in this issue still
> holds.

## Chunks

The non-risk chunks are C1 to C8. The risk-path chunks are R1 to R4, last. Every chunk is checked
with the full `## Checks` list; the "Check" line names the extra command that proves the chunk.

### C1: Recipes that taste good: curated sources, flavour and variety rules

- **PR title:** `[C1] feat(menu): curated recipe sources, flavour and variety rules`
- **Covers:** the recipe priority (bland, repetitive dishes from SEO fitness blogs).
- **Files:**
  - `recipe-sources.yaml` (new, repo root: sources for cuisines from anywhere)
  - `regions/es/recipe-sources.yaml` (new: Spain's own sources)
  - `tests/coach/test_recipe_sources.py` (new)
  - `coach/mealplan.py` (`Dish.base`, `repeats`)
  - `coach/recipes.py` (keep `base`)
  - `tests/coach/test_mealplan.py`, `tests/coach/test_recipes.py`
  - `.claude/skills/menu/SKILL.md` (step 4, a new "Flavour and variety" section, `base:` in the draft format)
  - `docs/conventions.md` (one bullet)
  - `docs/adding-a-region.md`, `regions/es/README.md` (one line each)
- **Depends on:** none.
- **Risk path:** no.
- **Model:** opus. It is design-heavy: the variety check's semantics and the flavour rules decide whether the menus actually improve.

**Where the list and rules live (decision).** The sources go in two data files with the same
format:
- `recipe-sources.yaml` at the repo root: sources for cuisines from anywhere (Serious Eats,
  Maangchi, Paulina Cocina...), used by every client, with or without a region.
- `regions/<code>/recipe-sources.yaml`: a region's own sources (`regions/es/` for Spanish
  cooking).

The /menu skill reads them directly (small YAML files, like `region.yaml`); there is no new CLI
command, because that would need `coach/cli.py`, a risk path. A test validates them. The flavour rules are behaviour, so they live in the skill text. The one rule
that needs counting across days (the protein and carb base) is checked in code, inside the
existing `repeats` list of `coach mealplan check`. That way it blocks `mealplan save` like any
repeat, with no CLI change. A cuisine neither file covers falls back to the open web.

**Format of both files.** A list of entries with these fields:
- `id`: a kebab slug.
- `name`.
- `url`: canonical https.
- `kind`: `site` or `youtube`.
- `language`: a two-letter language code.
- `cuisines`: lower-case English words.
- `tags`: any of `healthy`, `quick`, `budget`, `batch`, `beginner`.
- `why`: one line, at most 120 characters.
- `checked_on`: the date.

No other keys. The test in `tests/coach/test_recipe_sources.py` checks:
- ids and urls are unique across the root file and every region file, and every url starts with
  `https://`;
- `kind` and `tags` take only the allowed values, and `language` matches `^[a-z]{2}$`;
- `why` is at most 120 characters;
- no `steps`, `ingredients` or `recipe` keys exist, so no recipe text is copied;
- the root file and every region folder's file (when present) parse.

The entries are in "Recipe sources (verified 2026-11-01)" at the end of this plan; copy them as
they are.

**Variety check in `coach/mealplan.py`.**
- A dish may carry `base: [PROTEIN, CARB]`: one or two plain words, the main protein first, then
  the carbohydrate base, e.g. `[pollo, arroz]`, `[garbanzos]`, `[merluza, patata]`.
  - Parse it in `parse`: a list of 1 to 2 non-empty strings, else a clear error naming the day
    and the dish.
  - Compare as a set of folded words, singular and plural alike: reuse `tastes._forms` through
    a small helper.
- `repeats(days)` adds entries
  `{"kind": "base", "dish": "pollo + arroz", "base": [...], "dates": [...]}` when the same base
  appears again within `BASE_REPEAT_DAYS = 3` days. That is a `# convention:` listed in
  `docs/conventions.md`; the client sees enough variety and batch cooking still fits.
  - Group by `batches(days)` exactly as dish repeats do, so a batch (`servings: N`) is one
    appearance, and the window runs from the last serving of one group to the first of the next.
  - Existing entries gain `"kind": "dish"`.
  - The save message in `coach/cli.py` reads `r['dish']` and `r['dates']`, so it works unchanged.
    Do not edit `cli.py`.
- A dish without `base` is not checked (breakfasts and snacks).
- `coach/recipes.py`: `save` also copies `base` from the menu entry. Add `base` to the key list
  and to `order`, so a reused library dish keeps it.

**Skill text (menu SKILL.md).**
- Step 4 "Recipes" becomes:
  1. First the client's library (as now).
  2. Then the curated sources: the region's `regions/<region>/recipe-sources.yaml` first for
     its own cooking, then the root `recipe-sources.yaml` for other cuisines:
     - Pick by the client's `cuisines`, `flavours`, `cooking_skill`, `cooking_minutes` and
       `budget`, using tags.
     - Search within those sites first, e.g. `site:directoalpaladar.com garbanzos espinacas`.
     - Prefer a source whose dishes the client rated loved or liked, by the domain of the
       `source` links in `coach recipes list`.
  3. Then the open web, for a dish the curated sources lack.
  - Replace "fitness recipe blogs" with "well-tested recipe sites and cooking channels". Keep the
    untrusted-data sentence.
- New section "Flavour and variety", short, after step 4. The rules:
  - **Every main dish has a flavour plan:** a sauce or dressing, or a spice blend, plus an acid
    to finish (lemon, lime, vinegar, yoghurt, tomato), plus fresh herbs or an aromatic
    (garlic, onion, ginger, spring onion).
  - **Contrast:** something crisp or crunchy against something soft (toasted nuts or seeds,
    raw vegetables, a crust from searing or roasting).
  - **Technique:** vary it across the week (roast, sear, braise or stew, grill or plancha, stir-fry,
    raw or marinated); never more than two dishes with the same technique on one day.
  - **No bare plates:** no plain boiled protein with plain boiled carb ("pollo con arroz" only as
    a real dish with its sauce, e.g. arroz con pollo al curry or pollo al ajillo).
  - **Spread over the menu:**
    - proteins: poultry, fish or seafood, legumes, eggs, red meat or pork, dairy or tofu;
    - carb bases: rice, pasta, potato, bread, legumes, grains such as couscous or quinoa;
    - cuisines: at least two from the client's `cuisines` across a week.
  - **The draft:** give each lunch and dinner dish its `base`. `coach mealplan check` lists a
    protein and carb base repeated within 3 days under `repeats` (`kind: base`); change one of
    the dishes.
  - **Tastes:** `flavours` steers the spice and acid choices. `favoured` dishes come back (still
    subject to repeats), `disliked` rarely, `excluded` never. A dislike excludes its flavour
    builders too (a client who dislikes cilantro gets parsley or none).
  - **Seasoning stays free only in its listed forms** (step 6): a sauce with oil, nuts, cheese or
    honey is an item with grams.
- Draft format: add `base: [pollo, limón]`. Fix that example to a realistic `[pollo, arroz]` and
  add a matching rice item.

**Failing tests first:**
- `tests/coach/test_mealplan.py::test_same_protein_and_carb_base_within_3_days_is_a_repeat`, plus:
  - `..._base_4_days_apart_is_fine`;
  - `..._a_batch_counts_once_for_base_repeats`;
  - `..._base_must_list_one_or_two_words`.
- `tests/coach/test_recipe_sources.py` (the checks above).
- `tests/coach/test_recipes.py::test_saved_recipe_keeps_its_base`.

**Check:** `uv run pytest tests/coach/test_mealplan.py tests/coach/test_recipe_sources.py
tests/coach/test_recipes.py tests/skills`.

### C2: Menu: eat-out meals, cooking for more people, variable training day, short output

- **PR title:** `[C2] feat(menu): eat-out meals, people per meal, flexible training day, short output`
- **Covers:** items 7, 15 and 17.
- **Files:**
  - `coach/mealplan.py` (`Meal`, `parse`, `shopping`)
  - `tests/coach/test_mealplan.py`
  - `.claude/skills/menu/SKILL.md` (Reads `training_schedule` line, step 3, step 9, draft format, Output)
  - `.claude/skills/plan/SKILL.md` (step 5, the `training_schedule` sentence only)
  - `docs/conventions.md` (`training_schedule` bullet)
- **Depends on:** C1 (shares `mealplan.py`, `test_mealplan.py`, menu SKILL.md); C4 must be
  merged (it shares plan SKILL.md).
- **Risk path:** no.
- **Model:** sonnet.

**Item 15, eat-out meals.** A meal may carry `eat_out: true`: planned food eaten at a bar,
canteen or restaurant.
- Its dishes count in the day's totals as usual.
- `shopping` skips its items and lists the dish names under a new `eaten_out` key.
- `eat_out` and `tupper` together is an error (a lunchbox comes from home).
- `free: true` stays as is (unplanned food, no dishes).

**Item 15, people per meal.** A meal may carry `people: N` (a whole number of 1 or more, default
1): the dishes are cooked for N people.
- `shopping` multiplies that meal's items by N. A batch is multiplied by its servings and by its
  people.
- The appearances of one batch must share `people`; otherwise `parse` raises an error naming the
  dish.
- Totals and checks stay per client serving (items are always one serving as eaten).

**Item 7, variable training day.** `training_schedule:` accepts `fri|sat 10:00`: one session on
either day.
- /menu treats both days as possible training days and arranges the meals around the session so
  they work on either day. It asks the client which one only when the meals would differ.
- /plan writes the line that way when the client says "viernes o sábado".
- Update the convention bullet in `docs/conventions.md`.

**Item 17, short output.**
- The menu skill's Output becomes one compact table per day: meal, dish, and the day's kcal and
  protein from `coach mealplan check`, then a line with any day that is not ok.
- Steps, items and seasoning are shown only for a dish the client asks about.
- After `coach mealplan save`, run `coach mealplan export` by default and give the PDF path; the
  PDF carries the recipes and the shopping list. If the CLI says the `pdf` extra is missing, say
  `uv sync --extra pdf` and show the shopping list as a table instead.
- Step 9 changes to match.

**Failing tests first:**
- `tests/coach/test_mealplan.py::test_eat_out_meal_counts_in_totals_but_is_not_bought`
- `tests/coach/test_mealplan.py::test_people_multiplies_the_shopping_amounts`
- `tests/coach/test_mealplan.py::test_a_batch_for_two_is_bought_at_servings_times_people`
- `tests/coach/test_mealplan.py::test_eat_out_and_tupper_together_is_an_error`

**Check:** `uv run pytest tests/coach/test_mealplan.py tests/coach/test_cli.py tests/skills`.

### C3: Food table: Spanish staples, liquids in millilitres, fibre of animal foods

- **PR title:** `[C3] feat(foods): Spanish staples, liquids in ml, fibre 0 for animal foods`
- **Covers:** items 13 and 16, and the prawn fibre part of item 13.
- **Files:**
  - `foods/base_ids.tsv`, `foods/base.csv`, `regions/es/foods_ids.tsv` if needed,
    `regions/es/foods.csv` (rebuilt with the new column)
  - `scripts/build_food_table.py`
  - `coach/foods.py`, `coach/mealplan.py` (one line in `shopping`)
  - `tests/coach/test_foods.py`, `tests/coach/test_food_tables.py`
  - `foods/README.md`, `docs/conventions.md`
  - `.claude/skills/menu/SKILL.md` (steps 5 and 7: the sentences on ml)
- **Depends on:** C2 (shares `mealplan.py` and menu SKILL.md).
- **Risk path:** no.
- **Model:** sonnet.

**Item 13, new staples.** Add these rows to `foods/base_ids.tsv`, matched in FoodData Central SR
Legacy by `fdcId`:
- orange juice, raw (zumo de naranja);
- bouillon or broth prepared from a cube (caldo de pastilla, preparado);
- white sandwich bread (pan de molde);
- rye bread (pan de centeno);
- flour tortilla (tortilla de trigo);
- fresh tuna, raw (atún fresco, crudo).

Rules for the rows:
- Find the IDs with the FDC search (https://fdc.nal.usda.gov/) and write the exact
  `fdc_description`. The build refuses a mismatch. If the website blocks automated requests,
  use the FDC API with `api_key=DEMO_KEY`. This is the chunk most likely to stall on the
  network: if neither the release download nor the API works, stop and report rather than type
  any number.
- Rebuild with the command in `foods/README.md`. It needs the SR Legacy release download, linked
  in the script docstring.
- Nothing is typed by hand.

**Item 16, liquids in ml.** Add a `g_per_ml` column, built from SR Legacy's own portion data, so
no density is typed by hand:
- For a row marked liquid in the ids file (a new `liquid` column, `yes` or blank), the build reads
  the food's portion whose unit is `cup`, `fl oz` or `tbsp`, in that order of preference. It
  divides `gram_weight` by the exact US volume: cup 236.588 ml, fl oz 29.5735 ml, tbsp 14.7868 ml.
- Those volumes are unit definitions; label them `# convention:` in the script and list them in
  `docs/conventions.md`.
- The build stops if a liquid row has none of those portions.
- Mark milks, juices, broths, soy sauce, coconut milk and drinks. Not oils: they keep grams, as
  the menu skill already weighs fats.

In `coach/foods.py`:
- `Food` gains `g_per_ml: float | None`.
- `menu_totals` accepts `NAME=300ml` for a per-100 g food with `g_per_ml`, counting
  `300 * g_per_ml` grams. A food without it keeps today's error.
- In `mealplan.shopping`, key the amount by the unit the item was written in, so the client buys
  "leche semidesnatada: 2100 ml".
- Update the sentence in `foods/README.md` that says the coach applies no densities.

**Prawn fibre (judgement call for Matías).**
- Dietary fibre is plant carbohydrate, so unprocessed meat, fish, shellfish and eggs carry 0 g.
- Add a `fibre_zero` column in the ids file (`animal`). The build writes `0` when the source
  value is blank and adds `form_note` "fibre 0: animal food (convention)".
- Add a `# convention:` in the script and a bullet in `docs/conventions.md`.
- Change the prawns paragraph in `foods/README.md`.
- If Matías rejects it at review, drop this part only.

**Failing tests first:**
- `tests/coach/test_foods.py::test_a_liquid_with_a_density_can_be_written_in_ml`
- `tests/coach/test_foods.py::test_ml_for_a_food_without_density_is_still_an_error`
- `tests/coach/test_food_tables.py::test_new_spanish_staples_resolve` (the six `name_es` above)
- `tests/coach/test_food_tables.py::test_animal_foods_have_fibre`
- `tests/coach/test_mealplan.py::test_shopping_lists_a_liquid_written_in_ml_in_ml`

**Check:** `uv run pytest tests/coach/test_foods.py tests/coach/test_food_tables.py
tests/coach/test_mealplan.py`. Also rebuild twice and run `git diff --exit-code foods/` after the
second build to show the build is reproducible.

### C4: Strength: default rep range, Spanish and app exercise names

- **PR title:** `[C4] feat(strength): default rep range and Spanish and app exercise aliases`
- **Covers:**
  - items 9, 11 and 12;
  - item 5, the /import part;
  - issue #5, the alias part.
- **Files:**
  - `coach/strength.py`, `coach/muscle_map.yaml`
  - `tests/coach/test_strength.py`
  - `.claude/skills/plan/SKILL.md` (Reads `--rep-range` line, step 2 rep-range bullet, step 5 header lines)
  - `.claude/skills/review/SKILL.md` (the `--rep-range` line)
  - `.claude/skills/import/SKILL.md` (step 4 and a new injury re-check step)
- **Depends on:** none.
- **Risk path:** no.
- **Model:** sonnet.

**Item 9, default rep range.**
- `parse_rep_range` accepts `*=6-8`: the default for every lift. `rep_range_for` uses a
  named range first, then `*`, then `REP_RANGE`.
- `rep_range_for` matches names through the muscle map (issue #5): call
  `named_in(exercise, [name], load_muscle_map())`, cached, so `coach/cli.py` stays unchanged.
- /plan writes an optional line after `training_schedule:` in `data/plan.md`:
  `rep_range: 6-8`, the client's usual range. Lifts with another range keep their
  `LIFT: LOW-HIGH reps` line.
- /plan and /review pass `--rep-range "*=LOW-HIGH"` from that line, plus one `--rep-range` per
  lift that differs.

**Items 11 and 12, names.**
- In `_base_name`, also drop a trailing `- variant` part, as in "Seated Cable Row - Bar Grip" or
  "Remo Sentado con Cable - Agarre Recto". Then look up the base. Keep the full name tried
  first, so an entry that names the variant wins.
- Add aliases to `coach/muscle_map.yaml`:
  - Spanish names as Hevy shows them in Spanish. At least these, from the feedback, map to
    existing entries: "press de pecho iso-lateral" (chest press), "remo sentado con cable"
    (seated cable row), "tirón a la cara" (face pull), "press de piernas" (leg press),
    "extensión de pierna" (leg extension).
  - The common English app forms: "iso-lateral chest press", "seated cable row" variants, "lat
    pulldown" variants.
  - Where Hevy's or Lyfta's public exercise library pages can be opened, take names from them.
    Never take names from a personal export.
  - New exercises get an entry only with credits under the rules in the file header.
- `named_in` already uses the map, so injury pauses (item 12) follow with no code change. Add a
  test that proves it.

**Item 5, /import part.** New step in the import skill after step 4:
- Run `coach injury list`. If `unmatched` lists names, show the logged names from this import's
  lifts and ask which one each listed lift is.
- Then run `coach injury add AREA --exercises "..."` again with that name. A Spanish or English
  name the map knows needs no change.
- Step 4's sentence on `unmapped` says the alias list is the fix.

**Failing tests first:**
- `tests/coach/test_strength.py::test_star_rep_range_is_the_default_for_every_lift`
- `tests/coach/test_strength.py::test_a_named_range_beats_the_star`
- `tests/coach/test_strength.py::test_rep_range_names_match_through_aliases`
- `tests/coach/test_strength.py::test_spanish_hevy_names_are_counted`. It is parametrized over
  the 5 names above with their "(Máquina)" or " - Agarre Recto" suffixes, asserting `lookup`
  finds the right entry.
- `tests/coach/test_strength.py::test_injury_pause_matches_a_spanish_name`

**Check:** `uv run pytest tests/coach/test_strength.py tests/sessions tests/skills`.

### C5: /setup: PAR-Q+ in Spanish, returning lifters, activity days, injuries before an import

- **PR title:** `[C5] docs(setup): Spanish PAR-Q+ flow, returning lifters, activity days`
- **Covers:**
  - items 1, 3 and 4;
  - item 5, the setup part.
  Item 2 is in R2.
- **Files:**
  - `.claude/skills/setup/SKILL.md` (steps 4 and 8)
  - `forms/README.md`
  - `docs/conventions.md` (the `desk_training` bullet)
- **Depends on:** none.
- **Risk path:** no.
- **Model:** sonnet.

**Item 1, PAR-Q+.**
- With no PDF in `forms/`, send the Spanish form to a Spanish client:
  https://eparmedx.com/wp-content/uploads/2023/12/Spanish.pdf ("PAR-Q+ en español"). Also give
  the listing page https://eparmedx.com/print-versions-of-par-q/languages/ in case the file
  moves. Send English clients https://eparmedx.com/print-versions-of-par-q/.
- Say in one plain line what to do: fill it in, then send it back or answer two questions.
- Note in `forms/README.md` that the Spanish form is the 2018-based translation and the English
  one is the 2025 version. Both are official; use the client's language.

**Item 1, a filled-in PDF.** New sub-step for when the client sends one:
1. Read it where it is, without copying it.
2. List back only the outcome: any YES on the 7 questions, and any YES on the follow-ups. The
   answers themselves are not stored.
3. Ask the client to confirm, then store `screening.parq_any_yes` and
   `screening.parq_followup_yes`.
4. A field that cannot be read is asked as printed.
5. Never store the file in `data/`.

**Item 3, returning lifters.** In step 8, ask first "¿Entrenas ahora o lo dejaste? ¿Desde
cuándo?". For any loads the client gives, ask whether they are from now or from before the
break. Choose the level from what they lift today (the current rule). Loads from before the
break are history: /plan restarts lower per "Short breaks cost little".

**Item 4, activity level.** Ask for the training days in a usual week as one number. A range such
as "3-4" takes the lower number, per `coach knowledge section nutrition "Self-reported activity
is noisy"` ("choose the lower plausible multiplier when unsure"). So 3-4 days is `desk`, and
4 days in most weeks is `desk_training`. Say so in one line; the weight trend corrects it after
2-4 weeks. Update the `docs/conventions.md` bullet.

**Item 5, setup part.** In step 8, ask the lifts an injury affects in the client's own words, in
Spanish or English; aliases map common names (C4).
- Before any import, `coach injury add` prints every name under `unmatched`. Say that is
  expected and that /import re-checks it.
- Do not ask the client for English app names.

**Failing test first:** none (skill text). Run `uv run pytest tests/skills`, which checks every
cited knowledge section resolves.

**Check:** `uv run pytest tests/skills`.

### C6: Knowledge hygiene: broken heading references, shorter source quotes

- **PR title:** `[C6] docs(knowledge): fix heading references, shorten long source quotes`
- **Covers:** item 8 and issue #9.
- **Files:**
  - `knowledge/strength-hypertrophy.md`, `knowledge/nutrition.md`, `knowledge/sources.md`
  - `scripts/check_knowledge.py`, `tests/scripts/test_check_knowledge.py`
  - `knowledge/index.md` and `README.md` if the build changes them
- **Depends on:** none.
- **Risk path:** no.
- **Model:** sonnet.

**Item 8.** A scan on 2026-11-01 found five `(see "...")` references to headings that do not
exist. Point each at the real heading:
- `knowledge/strength-hypertrophy.md` line 57: "Counting sets"
- line 101: "Maintenance dose", which becomes "Maintenance dose during busy periods" (the
  tester's case)
- line 481: "Returning lifters"
- line 555: "Bone health"
- `knowledge/nutrition.md` line 997: "Deficit size for weight loss"

Add `check_references(knowledge_dir)` to `scripts/check_knowledge.py`: every `see "X"` in a
knowledge file must name a `### X` heading in some knowledge file. Call it in `main`. Since this
problem has now appeared five times, it becomes a check.

**Issue #9.** 52 `Supports:` lines are over 500 characters, 21 of them over 800.
- Shorten each to at most 500, keeping the sentences that carry the numbers the citing rules
  use. Mark the cuts with `...`.
- Never read `sources.md` whole: list the long lines with a short script, then open each by ID
  (`grep -n -A6 '^### S123$'`).
- For each source, grep the rules citing it and confirm their numbers are still in the quote.
- Add `check_quote_length` (`# convention:` 500 characters, matching the research skill's step
  4, listed in `docs/conventions.md`), so new long quotes fail.
- Run the online check for the changed sources, as the issue says.

**Failing tests first:**
- `tests/scripts/test_check_knowledge.py::test_a_reference_to_a_missing_heading_fails`
- `tests/scripts/test_check_knowledge.py::test_a_supports_quote_over_500_characters_fails`

Both use the fixtures in `tests/fixtures/knowledge/`.

**Check:**
- `uv run python scripts/check_knowledge.py` (it must pass with both new checks);
- `uv run python scripts/build_knowledge_index.py` then `git diff --exit-code knowledge/index.md README.md`.

`docs/conventions.md` is also touched, for one bullet.

### C7: Knowledge rules: heavy-bag boxing and functional training

- **PR title:** `[C7] docs(knowledge): heavy-bag boxing and functional training rules`
- **Covers:** item 6.
- **Files:**
  - `knowledge/cardio-health.md` (two rules)
  - `knowledge/sources.md` (new sources)
  - `knowledge/index.md`, `README.md` (counts, built)
  - `docs/research-log/2026-11-xx-boxing-functional.md`
  - `.claude/skills/plan/SKILL.md` (one Reads line and one cardio sentence)
- **Depends on:** C6 (shares `sources.md`; its new checks must pass); C4 must be merged (plan
  SKILL.md).
- **Risk path:** no.
- **Model:** sonnet.

Follow `docs/research-methodology.md` and the format in `CLAUDE.md`. Open every source below
before citing it, and quote at most 500 characters. Sources, checked to exist and be open on
2026-11-01:

- **Rule "Heavy-bag boxing as conditioning"**, grade emerging. Heavy-bag rounds are vigorous
  interval work: about 7 to 10.8 METs depending on punch rate, and a simulated round 9.3 METs.
  In a pilot trial, rounds at RPE 15-17 reached 86-89% of age-predicted HRmax. Prescribe them
  as HIIT under the same safety flags. Brief all-out bag bursts cost more energy than
  steady-state estimates suggest.
  - Herrmann SD et al. 2024 Adult Compendium of Physical Activities, J Sport Health Sci
    2024;13(1):6-12, doi:10.1016/j.jshs.2023.10.010, https://pmc.ncbi.nlm.nih.gov/articles/PMC10818145/
    (the MET values are on https://pacompendium.com/sports/: codes 15110, 15113, 15115, 15118, 15125).
  - Cheema BS et al. 2015, BMC Sports Sci Med Rehabil 7:3, doi:10.1186/2052-1847-7-3,
    https://pmc.ncbi.nlm.nih.gov/articles/PMC4429464/ (pilot RCT, n=12).
  - Scott C. 2019, European Journal of Human Movement 42:101-107,
    https://dialnet.unirioja.es/descarga/articulo/7383013.pdf (lab study, 10 men).
- **Rule "Functional training circuits"**, grade moderate. High-intensity functional training
  (multi-joint whole-body movements with short breaks) improves endurance and strength against no
  exercise, and matches moderate continuous training and HIIT for endurance. Count it as
  vigorous interval work when done hard. Its strength moves still need the lifting rules for
  progression. Use 2 to 4 sessions a week; no dose-response was found.
  - Wilke J, Mohr L. 2020, Sci Rep 10:21680, doi:10.1038/s41598-020-78615-5,
    https://pmc.ncbi.nlm.nih.gov/articles/PMC7728805/ (meta-analysis, 16 RCTs).
  - Feito Y et al. 2018, Sports 6(3):76, doi:10.3390/sports6030076,
    https://pmc.ncbi.nlm.nih.gov/articles/PMC6162410/ (definition only).
  - Liu C-J et al. 2024, Eur Rev Aging Phys Act 21:32, doi:10.1186/s11556-024-00366-3,
    https://pmc.ncbi.nlm.nih.gov/articles/PMC11664925/ (older adults, systematic review).

The rule text above is a draft. Write the final wording from what the opened sources say, with
"Applies to" and "Individual variation / conflicts" (small pilot, mostly men, moderate PEDro). If
a source cannot be opened or does not say what is listed here, drop that claim and log it in
`docs/dropped-claims.md`.

In plan SKILL.md step 3, add one sentence for an activity with no rule of its own: use the rule
of the closest modality by intensity, say which one, and suggest `/research`.

**Failing test first:** add the two new `coach knowledge section cardio-health "..."` lines to
plan SKILL.md first. `tests/skills/test_skill_files.py::test_cited_knowledge_sections_resolve`
then fails until the rules exist.

**Check:** `uv run python scripts/check_knowledge.py`,
`uv run python scripts/build_knowledge_index.py`, the check again, and `uv run pytest tests/skills`.

### C8: Windows: tests that write text without an encoding, line endings

- **PR title:** `[C8] fix(tests): explicit UTF-8 in tests, LF line endings`
- **Covers:** item 19, the code part.
- **Files:**
  - every test file that calls `write_text` or `read_text` without `encoding=`. On 2026-11-01
    there were 57 calls in 15 files:
    - `tests/coach/`: `test_checkins`, `test_cli`, `test_export`, `test_foods`,
      `test_knowledge`, `test_mealplan`, `test_profile`, `test_recipes`, `test_regions`;
    - `tests/scripts/`: `test_build_knowledge_index`, `test_check_knowledge`, `test_research`;
    - `tests/sessions/`: `test_importer_doc_example`, `test_importers`, `test_store`.
  - `.gitattributes` (new)
  - `tests/test_text_io_encoding.py` (new)
- **Depends on:** none.
- **Risk path:** no. `.gitattributes` is not in risk-paths; `.gitignore` is.
- **Model:** sonnet.

**Root causes found in planning.**
- On Windows, `Path.write_text` without an encoding writes cp1252. The readers decode UTF-8, so
  a non-ASCII fixture raises `UnicodeDecodeError`, a `ValueError`, which the CLI turns into
  exit 2. That accounts for the five recipe tests; `test_recipes.py` line 70 writes the menu with
  "calabacín".
- The BOM test (`test_checkins.py` line 44) cannot even encode `﻿` in cp1252.
- `test_hevy_basic` fails because git checks the fixture out with CRLF, so the quoted multi-line
  note reads "Line one\r\nline two".

**Fix.**
- Add `encoding="utf-8"` to every such call in `tests/`. `coach/` and `scripts/` already pass
  one.
- `.gitattributes`: `* text=auto eol=lf`, plus `*.png binary`, `*.gif binary`, `*.pdf binary`.
  The repo is already LF, so nothing renormalises; confirm with `git add --renormalize .` and
  an empty `git status`.

**The lint rule.** Ruff's `PLW1514` does not flag `Path.write_text`, so add
`tests/test_text_io_encoding.py`. It parses every `.py` file under `coach/`, `scripts/` and
`tests/` with `ast` and fails on a call to `open`, `.open`, `.read_text` or `.write_text` that
opens text without an `encoding` keyword. A binary mode (`"rb"`, `"wb"`) is exempt.

**Failing test first:** `tests/test_text_io_encoding.py`. It fails on the 57 calls, then passes.

**Check:** `uv run pytest`. If a Windows machine or VM is available, run `uv run pytest` there
too; otherwise R1's CI job proves it.

### R1: CI on Windows (risk path)

- **PR title:** `[R1] chore(ci): run the checks on windows-latest too`
- **Covers:** item 19, the CI part.
- **Files:** `.github/workflows/checks.yml`.
- **Depends on:** C8.
- **Risk path:** yes (`^\.github/`). It waits for `human-ok`.
- **Model:** sonnet.

The change:
- Add `strategy: matrix: os: [ubuntu-latest, windows-latest]` and `runs-on: ${{ matrix.os }}`,
  with `fail-fast: false`.
- Run the `es_ES.UTF-8` locale step only on Ubuntu (`if: runner.os == 'Linux'`). On Windows the
  locale test skips itself, which `-rs` shows.
- Keep "Index and README counts are fresh" on both; `.gitattributes` from C8 keeps line endings
  LF.
- The risk-gate's required check names may change with the matrix, e.g. `checks (ubuntu-latest)`.
  Check `.github/workflows/risk-gate.yml` and branch protection, and say in the PR what Matías
  must update.

**Failing test first:** none. The PR's own Windows job is the test; it must be green.

### R2: CLI: emergency number in `missing`, unmatched rep-range names (risk path)

- **PR title:** `[R2] feat(coach): emergency_number in profile missing, unmatched rep ranges`
- **Covers:** item 2 and issue #5, the report part.
- **Files:**
  - `coach/cli.py` (`PROFILE_REQUIRED`, `cmd_strength`)
  - `tests/coach/test_cli.py`
  - `.claude/skills/setup/SKILL.md` (step 1: drop "If they cannot say, use 112", which `missing`
    now enforces; step 9)
  - `.claude/skills/plan/SKILL.md` and `.claude/skills/review/SKILL.md` (act on
    `unmatched_rep_ranges`)
- **Depends on:** C4 and C5.
- **Risk path:** yes (`coach/cli.py`).
- **Model:** sonnet.

**Item 2.** Add `emergency_number` to `PROFILE_REQUIRED`. The region fallback in `coach safety`
stays for profiles saved before this change. The setup skill asks for the number in step 1; if
the client cannot say, it stores the region's number after saying so, so `missing` still clears.

**Issue #5.** `strength progress` returns
`{"lifts": {...}, "unmatched_rep_ranges": [...]}`. List the names given with `--rep-range`
(not `*`) that match no logged lift, through aliases.
- Changing the top-level shape is a breaking change for the skills, so update both skills in the
  same PR.
- Alternatively, keep the shape and add the reserved key `"_unmatched_rep_ranges"`. Pick one and
  say why in the PR. The cleaner shape (`lifts`) is preferred.
- /plan and /review: ask the client which logged lift each unmatched name is and rerun.

**Failing tests first:**
- `tests/coach/test_cli.py::test_profile_show_lists_a_missing_emergency_number`
- `tests/coach/test_cli.py::test_progress_reports_rep_range_names_that_match_no_lift`

### R3: Add a product by hand from its label (risk path)

- **PR title:** `[R3] feat(coach): add a product from its label without Open Food Facts`
- **Covers:** item 14; it also eases issue #6.
- **Files:**
  - `coach/cli.py` (`cmd_products`, the `products add` parser)
  - `coach/catalogue.py`
  - `tests/coach/test_cli.py`, `tests/coach/test_catalogue.py`
  - `.claude/skills/menu/SKILL.md` (step 5 bullets)
  - `regions/es/README.md`
- **Depends on:** C3 (menu SKILL.md chain; C1 to C3 merged).
- **Risk path:** yes (`coach/cli.py`).
- **Model:** sonnet.

**The command.**
`coach products add --label --name NAME --chain CHAIN --per "100 g" --kcal K --protein P
--carbs C --fat F [--fibre FI] [--barcode B] [--allergens "a, b"]`.
- No network and no `COACH_OFF_CONTACT`.
- `source` is `label (entered by hand)`.
- Without a barcode the key is a slug of the name, e.g. `label-proteina-chocolate`.
- Validate exactly like OFF values: the same `_number` limits, the 10% `energy_exception`
  warning, and the existing name-clash check.
- Carbs are the label's carbohydrate (EU labels give available carbohydrate).

**Skill.** Use `--label` when OFF has no match or `COACH_OFF_CONTACT` is missing. Read each value
from the label with the client, never estimate, and mark the product "values from the label".

**Failing tests first:**
- `tests/coach/test_cli.py::test_products_add_label_stores_the_label_values_without_network`
- `tests/coach/test_cli.py::test_label_values_out_of_range_are_refused`
- `tests/coach/test_catalogue.py::test_a_label_product_round_trips`

### R4: Energy with `no_training` uses the activity level without training (risk path)

- **PR title:** `[R4] fix(coach): no_training drops planned training from the PAL`
- **Covers:** issue #2.
- **Files:**
  - `coach/energy.py`, `tests/coach/test_energy.py`
  - `docs/safety.md` (flags table, `no_training` row)
  - `docs/conventions.md` if needed
- **Depends on:** none (merge after the others to keep the human-ok queue in order).
- **Risk path:** yes (`coach/energy.py`, `docs/safety.md`).
- **Model:** sonnet.

**Rule.** `nutrition.md` "Activity multipliers (PAL)" defines desk work with little exercise as
1.4-1.5, and desk work plus about 1 h of training most days as 1.6-1.75.
- With `no_training`, `desk_training` uses the `desk` band; that follows directly from the rule.
- `active` may come from the job or from exercise. Keep it, and add a note asking the client
  which; the skill reruns with `--pal` when it was exercise. Shipped in R4: the note only, no
  skill step. R4b added the `setup` and `plan` skill step and the `estimate_chosen` parameter,
  so an explicit `--pal` or `--tdee` silences the note.
- Compute this inside `energy.tdee` from `safety.flags(profile, today)`. `energy.py` already
  imports from `coach.safety`. As shipped, `cmd_energy` also passes the flag it holds and
  `estimate_chosen` (R4b); the rerun value is the `desk` midpoint, not an active-band value.
- An explicit `--pal` still wins.

**Failing tests first:**
- `tests/coach/test_energy.py::test_no_training_uses_the_desk_band_for_desk_training`
- `tests/coach/test_energy.py::test_no_training_keeps_active_with_a_note`

## Parallel groups

Up to 3 agents, each in its own worktree. A group starts when everything it depends on is merged.
Inside a group no two chunks share a file.

| Group | Chunks | Why together |
|---|---|---|
| G1 | C1, C4, C8 | No dependencies. The only overlap is C8's one-line `encoding="utf-8"` edits in `tests/coach/test_mealplan.py` and `test_recipes.py`, where C1 only appends new tests; git merges these cleanly. C1 is the long pole (opus), so start it first. |
| G2 | C5, C6 | No dependencies and no shared files (setup SKILL.md vs knowledge). Start each as soon as a G1 slot frees up. |
| G3 | C2, C7 | C2 starts after C1 and C4 merge; C7 after C4 and C6. Both touch plan SKILL.md in different sentences (C2 step 5, C7 step 3 and Reads), so run them one after the other, or in parallel and rebase the second. |
| G4 | C3 | After C2 (menu chain). |
| R | R1, R4 in parallel; then R2; then R3 | R1 needs C8. R2 needs C4 and C5. R3 needs C3. R2 and R3 both edit `coach/cli.py`, so they run in turn. R4 does not touch `cli.py`. |

The critical path is C1, C2, C3, R3 (the menu chain). Everything else fits beside it.

### Files several chunks touch, and how the edits are split

| File | Chunks | Split |
|---|---|---|
| `.claude/skills/menu/SKILL.md` | C1, C2, C3, R3 | C1: step 4, the new "Flavour and variety" section, `base:` in the draft. C2: the Reads `training_schedule` line, step 3, step 9, the draft's meal keys, Output. C3: the ml sentences in steps 5 and 7. R3: step 5 bullets. They run in sequence, each rebased on the last. |
| `.claude/skills/plan/SKILL.md` | C4, C2, C7, R2 | C4: Reads `--rep-range` line, step 2 rep-range bullet, step 5 header (`rep_range:`). C2: step 5 `training_schedule` sentence. C7: Reads cardio line, step 3 fallback sentence. R2: the `unmatched_rep_ranges` sentence after the Reads line. |
| `.claude/skills/setup/SKILL.md` | C5, R2 | C5: steps 4 and 8. R2: step 1 emergency sentence, step 9. |
| `coach/mealplan.py`, `tests/coach/test_mealplan.py` | C1, C2, C3 | C1: `Dish`, `parse` dish block, `repeats`. C2: `Meal`, `parse` meal block, `shopping`. C3: one line in `shopping`. Sequential chain. New tests are appended at the end of the file. |
| `coach/cli.py` | R2, R3 | R2: `PROFILE_REQUIRED`, `cmd_strength`. R3: `cmd_products`, the `products add` parser block. Run in turn. |
| `docs/conventions.md` | C1, C2, C3, C5, C6, R4 | Each chunk edits or appends only its own bullet in the matching section ("In the code" or "In the skills"). Never reflow neighbours. |
| `knowledge/sources.md`, `scripts/check_knowledge.py` | C6, C7 | C6 first; C7 appends new sources at the end of the file. |
| `tests/**` (encoding one-liners) | C8 vs C1, C3 | C8 only adds `encoding="utf-8"` to existing calls; C1 and C3 append new tests. Git merges these cleanly. If not, rebase and keep both. |
| `regions/es/README.md` | C1, R3 | C1: one line on `recipe-sources.yaml` in the file list. R3: the products section. |

## Turn estimate

Each estimate includes the review rounds, the PR and the merge.

| Chunk | Turns |
|---|---|
| C1 (opus) | 60 |
| C2 | 40 |
| C3 (data download and build) | 50 |
| C4 | 40 |
| C5 | 20 |
| C6 (52 quotes) | 60 |
| C7 | 40 |
| C8 | 25 |
| R1 | 15 |
| R2 | 25 |
| R3 | 30 |
| R4 | 20 |
| Orchestration (worktrees, merges, rebases, waiting on CI) | 60 |
| **Total** | **about 485** |

Set the session's turn limit to **550**. That leaves about 15% margin for a third review round or
a C3 rebuild. Risk-path PRs stop at "open, waiting for human-ok", so the session ends without
merging them.

## Recipe sources (verified 2026-11-01)

Copy these as they are, with `checked_on: 2026-11-01`
(`tags` may be empty). `last_active` is evidence for this plan, not a YAML field. Checked on
2026-11-01 from each site's RSS feed or news sitemap, YouTube's channel feed, or dates on the
page.

Things to know:
- Recetas de Rechupete moved: recetasderechupete.com now redirects to abc.es.
- Esbieta's website is parked; her channel is kept for its large back catalogue of recipes.
- Jauja is on hiatus. Juan Llorca's recent posts are recipes for young children.
- Serious Eats and EatingWell block bots. They are free, but the menu skill may get no page
  text: use their search results and links only.
- El Comidista's site may hit El País's metered paywall; its YouTube channel is active.
- Gap: Spanish healthy-cooking creators who really cook are few (Chef Bosquet, Juan Llorca).
  BBC Good Food, EatingWell, Pick Up Limes and Rainbow Plant Life cover healthy dishes in
  English.

`language` is any two-letter code (`hi` appears), so the C1 test checks the format
`^[a-z]{2}$`, not a fixed list.

Region file, `regions/es/recipe-sources.yaml` (Spanish cooking):

| id | name | url | kind | language | cuisines | tags | last_active | why |
|---|---|---|---|---|---|---|---|---|
| directo-al-paladar | Directo al Paladar | https://www.directoalpaladar.com/ | site | es | spanish, mediterranean, international | quick, budget | 2026-11 | Big Spanish food magazine, several new recipes a day, step-by-step photos, wide range of styles |
| recetas-de-rechupete | Recetas de Rechupete | https://www.abc.es/recetasderechupete/ | site | es | spanish, galician, mediterranean | beginner | 2026-11 | Classic Spanish home cooking with detailed steps; old domain recetasderechupete.com redirects here (ABC partnership) |
| hogarmania-arguinano | Hogarmanía (Karlos Arguiñano) | https://www.hogarmania.com/cocina/recetas/ | site | es | spanish, basque, mediterranean | quick, budget, beginner | 2026-11 | Recipes from Arguiñano's daily TV show, cooked on camera by a chef, cheap seasonal Spanish food |
| el-comidista-site | El Comidista (El País) | https://elpais.com/gastronomia/el-comidista/ | site | es | spanish, mediterranean, international | quick | unknown | Food journalism with tested, opinionated recipes; site blocks fetching and may hit El País metered paywall |
| el-comidista-yt | El Comidista en EL PAÍS | https://www.youtube.com/@elcomidistaenelpais | youtube | es | spanish, mediterranean, international | quick | 2026-10 | Video versions of El Comidista recipes, clear technique, lots of flavour and world dishes |
| las-recetas-de-mj | Las Recetas de MJ | https://www.lasrecetasdemj.com/ | site | es | spanish, mediterranean, international | beginner, budget | 2026-11 | Popular Spanish home cook, every written recipe has a matching video (youtube.com/lasrecetasdemj) |
| cocina-familiar | Cocina Familiar (Javier Romero) | https://cocina-familiar.com/ | site | es | spanish, riojan, mediterranean | budget, beginner | 2026-10 | Rioja cook with a TV show and 2,600+ home recipes; YouTube channel/UCXMrqL3QHKQP6Q-iObZjrXA also active |
| bon-viveur | Bon Viveur | https://bonviveur.com/es/ | site | es | spanish, mediterranean, international | batch, budget | 2026-11 | Spanish recipe site with a weekly menu (Mon-Sun) plus shopping list, good for menu planning |
| loli-dominguez | La Cocina de Loli Domínguez | https://www.youtube.com/@lolidominguezjimenez | youtube | es | spanish, andalusian | budget, beginner | 2026-10 | Andalusian home cook since 2013, traditional guisos and family dishes, ~2.9M subscribers |
| recetas-de-esbieta | Recetas de Esbieta | https://www.youtube.com/@RecetasdeEsbieta | youtube | es | spanish, bread, baking | beginner | 2026-09 | Large tested back catalogue (bread, baking); recent uploads are food-history essays, not recipes |
| chef-bosquet | Chef Bosquet | https://www.youtube.com/@chefbosquet | youtube | es | spanish, healthy | healthy, quick | 2026-10 | Spanish chef cooking light versions of popular dishes and desserts; mostly short videos |
| juan-llorca | Juan Llorca | https://juanllorca.com/ | site | es | spanish, mediterranean | healthy, batch | 2026-07 | Valencia chef for school and family food; recent posts are infant and BLW recipes, use for family meals only |

Root file, `recipe-sources.yaml` (cuisines from anywhere, any language):

| id | name | url | kind | language | cuisines | tags | last_active | why |
|---|---|---|---|---|---|---|---|---|
| paulina-cocina | Paulina Cocina | https://www.paulinacocina.net/ | site | es | argentinian, latin-american, international | quick, beginner | 2026-10 | Argentine cook with clear, humorous, tested guides; also active on YouTube @PaulinaCocina |
| de-mi-rancho | De Mi Rancho a Tu Cocina | https://www.youtube.com/@DeMiRanchoaTuCocina | youtube | es | mexican | budget | 2026-10 | Doña Ángela cooks traditional rural Mexican food over wood fire, real home technique |
| jauja-cocina-mexicana | Jauja Cocina Mexicana | https://www.youtube.com/@JaujaCocinaMexicana | youtube | es | mexican | budget, beginner | 2026-03 | Large library of home Mexican recipes by Janet; on hiatus since 2026-03 (family health) |
| serious-eats | Serious Eats | https://www.seriouseats.com/ | site | en | american, international | | 2026-11 | Deeply tested, technique-led recipes; date from sitemap only (site blocks bots, it is free, not paywalled) |
| bbc-good-food | BBC Good Food | https://www.bbcgoodfood.com/ | site | en | british, international | healthy, quick, budget, batch | 2026-10 | Test-kitchen recipes with nutrition per serving; some content is behind a Premium tier (partial paywall) |
| recipetin-eats | RecipeTin Eats | https://www.recipetineats.com/ | site | en | international, asian, australian | quick | 2026-10 | Nagi's recipes are known for reliable results and big flavour, very well tested |
| eatingwell | EatingWell | https://www.eatingwell.com/ | site | en | american, international | healthy, quick | 2026-11 | Healthy recipes from a test kitchen with dietitian review; date from sitemap only (blocks bots) |
| budget-bytes | Budget Bytes | https://www.budgetbytes.com/ | site | en | american, international | budget, batch, beginner | 2026-10 | Low-cost recipes with cost per serving, meal-prep friendly, tested |
| ethan-chlebowski | Ethan Chlebowski | https://www.youtube.com/@EthanChlebowski | youtube | en | american, international | quick, budget | 2026-10 | Home cooking technique and flavour building, how to make everyday meals taste better |
| kenji-lopez-alt | J. Kenji López-Alt | https://www.youtube.com/@JKenjiLopezAlt | youtube | en | american, international, asian | quick | 2026-10 | Food-science chef, unedited POV cooking that teaches technique |
| just-one-cookbook | Just One Cookbook | https://www.justonecookbook.com/ | site | en | japanese | | 2026-10 | Authoritative Japanese home cooking by Namiko Chen, tested with step photos |
| maangchi | Maangchi | https://www.youtube.com/@Maangchi | youtube | en | korean | | 2026-10 | The reference for Korean home cooking; written recipes also at maangchi.com (blocks bots) |
| woks-of-life | The Woks of Life | https://thewoksoflife.com/ | site | en | chinese | | 2026-11 | Chinese family of cooks, tested Chinese and Chinese-American recipes with technique notes |
| made-with-lau | Made With Lau | https://www.youtube.com/@MadeWithLau | youtube | en | chinese, cantonese | | 2026-09 | Retired Cantonese restaurant chef teaches home dishes; written recipes at madewithlau.com |
| hot-thai-kitchen | Hot Thai Kitchen (Pailin Chongchitnant) | https://hot-thai-kitchen.com/ | site | en | thai | | 2026-10 | Trained Thai chef explaining real Thai flavour balance; videos on YouTube @PailinsKitchen |
| pati-jinich | Pati Jinich | https://patijinich.com/ | site | en | mexican | | 2026-10 | Mexican chef and PBS host, deeply regional Mexican recipes |
| rick-bayless | Rick Bayless | https://www.youtube.com/@RickBayless | youtube | en | mexican | | 2026-10 | Chef of Frontera Grill, regional Mexican technique (his website has not posted since 2024) |
| giallo-zafferano | GialloZafferano | https://www.giallozafferano.it/ | site | it | italian | beginner | 2026-10 | Italy's main recipe site, own test kitchen, step-by-step photos for every recipe |
| ranveer-brar | Chef Ranveer Brar | https://www.youtube.com/@RanveerBrar | youtube | hi | indian | | 2026-11 | Indian chef explaining regional dishes and technique (mostly Hindi); channel also runs a talk show |
| hebbars-kitchen | Hebbar's Kitchen | https://hebbarskitchen.com/ | site | en | indian, vegetarian | quick, beginner | 2026-08 | Large library of vegetarian Indian home recipes with short videos |
| ottolenghi | Ottolenghi | https://ottolenghi.co.uk/pages/recipes/ | site | en | middle-eastern, mediterranean, plant-based | healthy | 2026-10 | Vegetable-forward recipes famous for flavour; videos on YouTube @Ottolenghi (2026-09) |
| pick-up-limes | Pick Up Limes | https://www.pickuplimes.com/recipe/ | site | en | plant-based | healthy, quick | 2026-11 | Dietitian-led vegan recipe index with nutrition info; YouTube is now mostly lifestyle shorts |
| rainbow-plant-life | Rainbow Plant Life | https://rainbowplantlife.com/ | site | en | plant-based, international | healthy, budget | 2026-10 | Vegan recipes built for flavour (Nisha Vora), well tested |

Dropped, with the reason:
- Dime qué comes: no recipe since 2015.
- recetasdeesbieta.com: the domain is parked.
- Chef Bosquet website: masterclass sales only, no recipe archive.
- Karlos Arguiñano YouTube: no official channel found.
- Directo al Paladar YouTube: news, not recipes.
- Rick Bayless website: last post 2024.
- Serious Eats YouTube: last upload 2024-10.
- EatingWell YouTube: last upload 2024-11.
- Hebbar's Kitchen YouTube: could not be verified.
- Las Recetas de Laura: weight-loss vlogs.
- Velocidad Cuchara: roundups only.
- Webos Fritos: the domain did not resolve.
