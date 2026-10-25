# Content licence

The written content of this repository is licensed under the Creative Commons Attribution 4.0
International licence (CC BY 4.0): https://creativecommons.org/licenses/by/4.0/
(full legal code: https://creativecommons.org/licenses/by/4.0/legalcode).

It covers:

- `knowledge/`: the graded rules, the index and the source list. The rules are summaries written
  for this project; each one cites its sources, and the studies, guidelines and books cited
  remain under their own copyright and licences. The quoted passages on the `Supports:` lines of
  `knowledge/sources.md` are excerpts reproduced as quotations, so a reader can check each claim;
  they stay under their publishers' copyright and are not covered by CC BY 4.0.
- `docs/`, the skill instructions in `.claude/skills/`, and every other text file not listed under
  MIT below (`README.md`, `CLAUDE.md`, and the READMEs, `region.yaml` and ID mappings in `foods/`,
  `regions/` and `forms/`).
- The images in `assets/`.

Attribution: "AI personal coach by matgarfer499
(https://github.com/matgarfer499/ai-personal-coach), CC BY 4.0", with a note of any changes you
made.

The code (`coach/`, `scripts/`, `tests/`, `.github/`, `.claude/workflows/`) is under the MIT
licence in `LICENSE`. The nutrient values in `foods/` and `regions/` are USDA data in the public
domain (below).

## Third-party data

- `foods/base.csv` and `regions/es/foods.csv`: nutrient values from USDA FoodData Central, SR
  Legacy (U.S. Department of Agriculture, Agricultural Research Service, FoodData Central,
  https://fdc.nal.usda.gov/). FoodData Central data are in the public domain (CC0 1.0); USDA asks
  to be cited as the source.
- Open Food Facts: no Open Food Facts data ships with the repository. Products a user adds with
  `coach products add` are stored in their own data directory and stay under the Open Database
  License (https://opendatacommons.org/licenses/odbl/1-0/); each row keeps its product URL as
  attribution.
- The PAR-Q+ form is not redistributed: users download it from https://eparmedx.com (see
  `forms/README.md`).
