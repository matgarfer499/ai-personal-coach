# Conventions

A convention is a number or choice the coach needs where the evidence gives a range or no figure.
Every one is labelled where it lives: `# convention:` in code, "convention", "heuristic" or
"product policy" in a knowledge rule. This file lists them all so a reviewer can check each one.

## In the code (`coach/`, `scripts/`)

`tests/test_docs.py` fails if a constant behind a `# convention:` comment is missing here.

### Coaching numbers

| Constant | Value | Rule it builds on | Why this value |
|---|---|---|---|
| `energy.pal` | band midpoint | nutrition.md "Activity multipliers (PAL)" | midpoint as the point estimate |
| `macros.PROTEIN_DEFICIT`, `PROTEIN_OLDER`, `PROTEIN_GLP1` | midpoints 2.0, 1.4, 1.4 g/kg | "Protein during fat loss", "Older adults: protein targets", "GLP-1 users: protein, training and red flags" | midpoint of the rule's range |
| `macros.REFERENCE_BMI` | 25 | "Daily protein target for people who lift" (use fat-free mass or goal weight with obesity) | the coach knows neither, so it uses the weight at BMI 25 for the client's height |
| `macros.FAT_FRACTION` | 25% of energy | "Minimum dietary fat" (default 20-35%) | lower half of the default range, leaving room for carbohydrate |
| `trend.MIN_POINTS`, `MIN_DAYS` | 7 weigh-ins over 14 days | "Read the scale with weekly averages", "Recalibrate TDEE from the weight trend" | the plan's threshold before any trend is shown |
| `trend.WINDOW_DAYS`, `MAX_WINDOW_DAYS` | 28, at most 56 days | "Read the scale with weekly averages" (2-4 weeks) | 4 weeks, stretched for clients who weigh weekly, never older than 8 weeks |
| `trend.ENERGY_DENSITY_KCAL_PER_KG` | 7700 | "Expected weight change: the 3500 kcal rule is wrong" (asks for less early on, no figure) | judgment call: the higher density is the cautious error both ways |
| `energy.RECALIBRATE_STEP_KCAL` | 200, cuts only | "Recalibrate TDEE from the weight trend" (steps of about 100-200 kcal) | judgment call: eating more is never stepped |
| `strength.EPLEY_DIVISOR` | Epley e1RM, RIR added to reps | none names a formula | a common, simple estimate; only compares a lift with itself |
| `strength` hard-set default | a set with no RIR or RPE counts as hard | "Target reps in reserve" | logs often omit effort |
| `strength.INCREMENT_UPPER`, `INCREMENT_LOWER`, `LOAD_STEP_KG` | 2.5% / 5%, 0.5 kg | "Double progression" (2-10%, smaller for upper body) | smallest practical jumps |
| `strength.BREAK_DAYS`, `SHORT_BREAK_DAYS`, `RESTART_LONG` | over 7 days off; after 14 days restart at 85% | "Short breaks cost little" (about 90% under 2 weeks, 10-20% below after) | 85% is the midpoint of 10-20% below |
| `profile.EXPERIENCE` | novice: under 12 months of consistent training (about 2+ sessions a week); intermediate: 12 months or more, still progressing; advanced: 12 months or more, progress plateaued | "Novice strength gains and plateau" (fast gains in year one, slowing after 6-12 months), "Trained lifters: 12-20 weekly sets" (at least 1 year of training, plateaued) | no rule defines the levels; 12 months is the threshold both rules' populations share. Only novice and advanced load a rule of their own in /plan |
| `zones.TALK_TEST["light"]` | "can talk and sing" | "0-10 effort scale and talk-test anchors" (moderate and vigorous only) | completes the scale |
| `zones.PREGNANCY_RPE` light and vigorous | 9-12, 15-17 | "Gauge intensity by talk test and RPE" (moderate 13-14 from its source) | fills the bands around the source's moderate |
| `cli.PROGRESS_LOOKBACK_DAYS` | 28 | none | `strength progress` covers lifts trained in the last 4 weeks |
| `cli.MENU_KCAL_MARGIN` | a /menu day passes from the target up to 5% over, never under | none | close enough to plan meals without arithmetic by the model |
| `mealplan.NO_REPEAT_DAYS` | 7 | none | decided with the user (2026-10-25): a dish does not come back within 7 consecutive days, so a plan of any length stays varied without needing 100+ distinct dishes |
| `servings: N` on a dish (draft) | a dish marked `servings: N` may appear up to N times without the 7-day rule; items are for one serving; the shopping list buys it once at N servings; the N+1th appearance, or an unmarked repeat, is a repeat again; a second batch of the same dish starts at least 7 days after the last serving of the first | "Meal planning" (batch-cook and freeze) | cooking once for several days and repeating a simple breakfast are on purpose, not accidents; grouping by N keeps accidental repeats rejected and never lets a batch hide a day's targets (each appearance is still checked) |
| `tastes.matches` | a taste or pantry phrase matches a food when every word of the phrase is a whole word of its name (either language), plural or singular, case and accents ignored | none | "tomate" flags "tomate, crudo" and "salsa de tomate", "tomate crudo" only the first; no synonyms or categories ("lactosa" does not match "leche"), so a miss is never proof of safety |
| `tastes.RAW_WORDS`, `FILLER_WORDS` | crudo, fresco, raw, fresh say a food is raw or fresh; de, la, con and similar words are ignored | none | the table's plain names ("tomate") are the raw food, so a dislike of "tomate crudo" still reaches them but never "salsa de tomate" (a name with other content words is a different food) |
| `mealplan.BLOCKING_KINDS` | an allergy or intolerance named in tastes blocks `mealplan save` when a dish, item or seasoning matches; a dislike, an untried food or a never_again dish only warns | none | the client named the first two as foods to avoid; a dislike is a preference the client may overrule. Name matching knows no synonyms, so a miss never proves a dish is safe (the skill still says to check labels) |
| `mealplan.FREE_MEALS_PER_DAY`, `Day.share` | one free meal a day; with it, the planned meals must each reach an equal share (planned meals / all meals) of the kcal, protein, fat-minimum and fibre targets, and kcal may not pass the full target | "Refeeds and cheat meals" (a planned higher-calorie meal for psychological relief is fitted into the energy budget; never prescribed for metabolic reasons) | a free meal's food is unknown, so the plan must stand without it: the day cannot be mostly free and an under-target day is never hidden behind a budget. `coach mealplan` reports what the free meal has left to reach the targets (`free_meal.budget`) and refuses a free meal after a positive eating-disorder screen |
| `profile.research_reminder_months` | 6 | none (chosen when the coach was designed) | how often `/plan` and `/review` suggest `/research stale` |
| `tastes.COOKING_SKILLS`, `BUDGETS` | three levels each | none | enough for /menu to pick recipe difficulty and ingredients |
| `safety` injury pause (`_injuries`) | an active injury's listed lifts never progress; unassessed they get no load, assessed at most the last load (or the lower restart load after a break) | recovery-habits.md "Some pain during exercise is acceptable in chronic, assessed pain" (assessed pain is managed by load; acute or worsening pain is referred) | no rule says how fast to load an injured lift; whoever manages the injury decides, so `strength progress` says `paused` instead of progressing or calling it a stall |
| `strength.progression(stall_after=...)` | sessions on or before an injury's `cleared_on` never count towards a stall (also those before its `since`: the cautious direction) | "When progress stalls" | loads held on purpose are not a plateau |
| `safety.VIGOROUS_REVIEW_AGE` | 45, read as aged 45 or more | recovery-habits.md "PAR-Q+ specific thresholds" ("over 45") | the cautious reading of the cut-off |
| `safety` unanswered PAR-Q+ | treated like a YES for vigorous work and sprints | "PAR-Q+ specific thresholds" (sprints need every answer NO), cardio-health.md "Choosing HIIT vs MICT vs SIT" (unscreened: moderate first) | no vigorous work on an unknown screen |
| `foods.PER_UNITS` | a product is per 100 g or per 100 ml; its menu items are in that unit only | none | the coach has no densities, so grams and millilitres are never converted or mixed; `coach products add` refuses `--per` that disagrees with the pack unit Open Food Facts reports unless `--confirm-per` says the label was read |
| `export.QR_CM` | A4, 2.4 cm QR codes | none | the PDF printout: each recipe's source link as a QR that scans from paper or a phone screen; `coach mealplan export` needs the optional `pdf` extra |
| `recipes.SLUG_MAX` | 80 characters | none | recipe file names stay readable and far below any file system limit |
| `tastes.RATINGS` | loved, liked, disliked, never_again | none | /menu favours loved and liked dishes, offers disliked ones rarely, never_again ones never |

### Tooling and input checks (not coaching)

| Constant | Value | Purpose |
|---|---|---|
| `cli.OUTPUT_DECIMALS` | 2 | numbers a skill quotes verbatim |
| `tastes.POSTAL_CODE` | 3 to 10 letters, digits, spaces or hyphens | rejects typos; fits any country's format |
| `off.BARCODE` | 8 to 14 digits (EAN-8 to GTIN-14) | rejects typos before asking Open Food Facts |
| `off.OFF_TIMEOUT_S` | 20 s | how long `coach products` waits for Open Food Facts |
| `off.SEARCH_LIMIT` | 10 hits | enough to spot a product without paging (OFF allows 10 searches a minute) |
| `checkins.RANGES` | weight 25-400 kg, waist 40-250 cm, intake 0-15,000 kcal, sleep 0-24 h | rejects typos and impossible values |
| `zones.HR_REST_RANGE`, `HR_MAX_RANGE` | 30-120, 100-230 bpm | rejects typos |
| `foods.ENERGY_TOLERANCE` | 10% of the 4/4/9 (+2 fibre) energy | flags a food row whose stated kcal disagrees, unless it carries a `kcal_exception` |
| `knowledge.HEADER_LINES` | 5 | where the "Evidence checked on" date may sit |
| `check_knowledge.LONG_TITLE_RUN`, `MIN_TITLE_RUN` | 80, 20 characters | how much of a PubMed title a citation must reproduce |
| `research.SLUG_MAX` | 40 | research branch names stay readable |
| `profile.EMERGENCY_NUMBER` | 2 to 6 digits | rejects typos in a client's emergency number (112, 911, 000) |

### In the skills (`.claude/skills/`)

- /setup: `desk_training` means about 1 h of training on 4 or more days ("most days" read as 4+).
- /checkin: one row per day; weight is that morning's, intake the previous day's, sleep the
  night before; the weekly cycle and BP questions are asked when no note of the last 7 days
  records them.
- /plan: plyometric jumps count as vigorous work for `review_before_vigorous` (the rule
  "PAR-Q+ specific thresholds" names HIIT, 1RM tests and all-out sprints; jumps are maximal-effort
  work by the same caution). Jump rope is vigorous by its own rule.
- /plan, /review: after missed sessions the rotation (A, B, A, B) continues where the client left
  off; sessions are never doubled up or added to catch up. "How long habits take" says one missed
  session does not undo progress and to get back on track at the next opportunity, but no rule
  gives the order of sessions, so the order is a convention. Loads after a break come from
  `coach strength progress` ("Short breaks cost little").
- /plan: with no workout log, 2-3 working sets per exercise; with a log, each muscle stays near
  its last logged week; when two rules give different RIR, the more conservative wins.
- /menu: dried herbs, spices, salt, pepper, vinegar and lemon juice count as free seasoning; any
  other seasoning with energy (oil, butter, sauces, honey, cheese) is an item with grams. The
  horizon is asked in days because `data/plan.md` records no block end.
- /plan and /menu: `data/plan.md` may carry a line `training_schedule: mon 18:30; wed 18:30; sat`
  (English day tokens, optional 24 h start times); /menu reads it to place the meals around
  sessions per "Protein timing and the \"anabolic window\"" and "Carbohydrate around long or
  fasted sessions". The line format is a convention; the rules give no clock times, so the
  skill only places a protein meal within a few hours of a session and a carbohydrate snack
  before fasted or long (over about 45 min) sessions.
- /menu: a meal marked `tupper: true` is eaten away from home (cold or reheatable, no
  last-minute cooking); the CLI only records it.
- /review: a calorie change is proposed only when the weight-change rate is outside the goal's
  range (undefined for maintenance and recomposition, which have no rate rule).

## In the knowledge files

These rules label part of their content as a convention, heuristic or product policy (the label
is in the rule text). Grades describe the evidence, not the labelled part.

- **cardio-health.md:** ACSM intensity bands (vigorous HRR capped at 84%); Exercise for bone:
  resistance plus impact; Energy compensation: burned calories under-deliver; Wearable calorie
  estimates are unreliable.
- **nutrition.md:** Activity multipliers (PAL); Recalibrate TDEE from the weight trend (100-200
  kcal steps); Deficit size for weight loss (overweight and obesity); Daily protein target for
  people who lift (goal-weight protein with obesity); Eyeballing portions versus weighing;
  Under-18s; GLP-1 users: protein, training and red flags.
- **recovery-habits.md:** Possible sleep apnoea: suggest a doctor; Deloads are optional and
  reactive; Short breaks do not erase progress; Simple readiness monitoring; Brief warm-up before
  every session; Pain-monitoring traffic light for tendon problems; How long habits take; Fever
  and systemic illness: do not train; Train it: aerobic and resistance work both lower BP;
  Breathing and load: avoid Valsalva in at-risk clients; Coach scope vs medical nutrition
  therapy; Screening: brief questions as a prompt, not a diagnosis; Warning signs that warrant
  referral; Adolescents: no deficits; Missed periods and low energy availability; How to raise a
  concern; Diastasis is not a marker of pelvic-floor dysfunction.
- **strength-hypertrophy.md:** Effort limits for older adults and cardiovascular risk (RIR to
  Borg mapping, age cut-off, 8-week step); Exercise variation; Double progression; When progress
  stalls; Deloads (30-50% volume cut); Short breaks cost little; Returning lifters and "muscle
  memory"; Starting load and ramp-up (ICFSR); Do not keep older clients on light weights forever;
  How to prescribe power training; Frail older adults.

The 2026-10-24 dropped-claims research run (`docs/research-log/2026-10-24-dropped-claims.md`)
added one, in
recovery-habits.md: "Foam rolling before training: optional" (keep it brief).

To regenerate the knowledge list, search the rule files for "convention", "heuristic", "product
policy" and "not trial-derived" under each `###` heading.
