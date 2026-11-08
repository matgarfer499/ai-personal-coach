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
