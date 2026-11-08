# Incidents

One line per bug that reached main: what broke, and which review layer should have caught it.

- 2026-11-08 (beta p3-antonio-I1): `coach energy` and `coach macros` printed a calorie deficit
  while `no_training` had stopped training for cardiac symptoms. Layer: tests of the flags table
  (no case combined `no_training` with a fat-loss goal).
- 2026-11-08 (beta p3-antonio-I2): `coach safety` listed "light-to-moderate work only" next to
  "no training until a clinician clears it". Layer: skill dry run (docs/examples cardiac case).
- 2026-11-08 (beta p1-lucia-I8, p3-antonio-I5): symptoms reported at a check-in could not set any
  flag from the CLI; detection depended on the model. Layer: design review of docs/safety.md
  "What protects what".
- 2026-11-08 (beta p1-lucia-I1, p6-james-I1): `checkin add` accepted dates after today and the
  trend used them. Layer: tests (input validation of `checkin add`).
- 2026-11-08 (beta p1-lucia-I2): `checkin add` echoed only the fields just given, so a merged
  row looked erased. Layer: code review.
- 2026-11-08 (beta p1-lucia-I3/I4, p4-sara-I4/I5): medications `none` was stored as a medication,
  and /setup read as if `pregnant` were a profile field. Layer: skill dry run (docs/examples/setup.md).
- 2026-11-08 (beta p3-antonio-I6): `emergency_number` was listed as missing although the region
  supplies it. Layer: tests (PR #27 added the field without a region case).
- 2026-11-08 (beta p5-elena-I4): protein dropped 27 g between 84 and 85 kg because the basis
  switched at BMI 30. Layer: tests (no case either side of a boundary).
- 2026-11-08 (beta p2-marcus-I4/I5): a re-export in other units was counted as plain duplicates
  and `coach import` ignored `--today`. Layer: tests.
- 2026-11-08 (beta p2-marcus-I1): `strength progress` judged a 5-rep lifter against 8-12
  without asking. Layer: skill dry run (docs/examples/plan.md uses only 8-12 lifters).
- 2026-11-08 (beta p5-elena-I11): `coach foods search "pan integral"` (one quoted argument)
  found nothing; only separate words worked. Layer: tests (no case passed a phrase).
- 2026-11-08 (beta p4-sara-I6): `coach tastes rate` recorded a dish that was in no saved menu,
  no recipe and had no link. Layer: tests (the rate cases never named an unknown dish).
- 2026-11-08 (beta p4-sara-I8): menu PDF recipe cards said "1 ración" for meals cooked for
  several people, and breakfasts got only a one-line card. Layer: visual review of the PDF in
  PR #32.
- 2026-11-08 (beta p5-elena-I1/I2/I3/I7): "Minimum dietary fat", "Dietary fibre" and "Protein
  during fat loss" cited sources whose stored quotes did not state their numbers, and
  check_knowledge.py could not tell. Layer: check_knowledge.py (now `--claims`) and research
  verification.
- 2026-11-08 (audit, #46): `coach macros --kcal` kept a stored surplus while `no_training` held
  calories at maintenance. Layer: tests of the flags table (the surplus clamp had no
  `no_training` case).
- 2026-11-08 (audit, #46): `strength plan-sets` crashed with a traceback on `exercises: 5`.
  Layer: tests (input validation of the plan YAML).
- 2026-11-08 (audit, #28 and #46): `plan check` read `target_kcal: 2,100` as 2.1 kcal and took
  any `in_deficit` other than `true` as false. Layer: tests (no malformed header case).
- 2026-11-08 (audit, #46): a run log with a `notes` column matched no importer. Layer: tests
  (the fixtures had only the required and numeric columns).
- 2026-11-08 (audit, #46): re-sending the same check-in notes stored them twice. Layer: tests.
- 2026-11-08 (beta2 p1-lucia-I2): `coach plan export` printed a training PDF and `plan check`
  stayed ok after `no_training` stopped training. Layer: design review of docs/safety.md "What
  protects what" (the saved plan was not listed as something a stop must reach).
- 2026-11-08 (beta2 p6-james-I4, p3-antonio-I1): check-in notes missed "unusually tired" and
  `--symptoms chest_tightness` was refused. Layer: tests (the word list was never checked
  against every token in the rule's symptom list).
- 2026-11-08 (beta2 p2-marcus-I2, p7-nuevo-I4): Hevy names ("Hack Squat (Machine)"), dumbbell
  and goblet variants were unmapped, so weekly sets were undercounted. Layer: tests (no fixture
  used equipment-prefixed or Hevy names in plan-sets).
- 2026-11-08 (beta2 p1-lucia-I1, p2-marcus-I1, p6-james-I3): `coach plan export` silently dropped
  exercises with 5+ word names, a "(Barbell)" part or no load, and `plan check` stayed ok.
  Layer: tests (fixtures used only short, loaded Spanish names).
- 2026-11-08 (beta2 p5-elena-I3, p4-sara-I5): the protein note rounded 70.56 kg to "71 kg", so
  its figures did not reproduce, and the veg-and-fruit warning said "400 g of the 400 g". Layer:
  code review (note text was never checked against the numbers next to it).
- 2026-11-08 (beta2 p5-elena-I1): `mealplan check` computed `protein_max_g` but never compared a
  day with it, so a 202 g day read ok against a 155 g top. Layer: code review (a target computed
  and never read).
- 2026-11-08 (beta2 p4-sara-I6): rating a dish in another case renamed it. Layer: tests.
- 2026-11-08 (beta2 p6-james-I2): the taper reference was the single week before the taper, so
  it moved with the race date onto a spike week. Layer: tests (one race date only).
- 2026-11-08 (beta2, a panel opinion confirmed): printed HR zones left 1-2 bpm in no zone.
  Layer: tests (zone tops were checked one by one, never against the next floor).
- 2026-11-08 (beta2 p7-nuevo-I3): the README's install line ran `uv sync` without the pdf extra
  that /plan's export needs, and asked to clone a private copy before saying how to make one.
  Layer: skill dry run from a clean clone (no dry run started from the README alone).
- 2026-11-08 (beta2 p4-sara-I2): a catalogue product and the generic food it stands for got two
  shopping lines in different stores. Layer: tests (no fixture with a product and its generic food
  in one menu).
- 2026-11-08 (beta2 p2-marcus-I3): imports in pounds stored kg with 8 or more decimals.
  Layer: tests (lbs fixtures checked with approx, never the stored text).
