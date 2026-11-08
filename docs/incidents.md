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
- 2026-11-08 (beta p2-marcus-I4/I5): a re-export in other units was counted as plain duplicates
  and `coach import` ignored `--today`. Layer: tests.
- 2026-11-08 (beta p2-marcus-I1): `strength progress` judged a 5-rep lifter against 8-12
  without asking. Layer: skill dry run (docs/examples/plan.md uses only 8-12 lifters).
- 2026-11-08 (beta p5-elena-I1/I2/I3/I7): "Minimum dietary fat", "Dietary fibre" and "Protein
  during fat loss" cited sources whose stored quotes did not state their numbers, and
  check_knowledge.py could not tell. Layer: check_knowledge.py (now `--claims`) and research
  verification.
