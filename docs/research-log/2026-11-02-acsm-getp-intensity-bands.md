# Research log: acsm getp intensity bands

Date: 2026-11-02

## Topic

ACSM GETP 11th and 12th edition intensity bands (issue: verify the ACSM intensity bands against
the newer editions). Two groups: the GETP 11th and 12th edition intensity table, and other
ACSM or official statements from 2018 to 2026 that restate the %HRR, %HRmax and RPE classes.

## What was searched

Web and PubMed/PMC searches for the GETP 11th (2021) and 12th (2025) edition intensity tables,
the ACSM 11th-to-12th crosswalk, the ACSM/ESSA joint statement on intensity terminology (2025),
the 2018 Physical Activity Guidelines Advisory Committee report, and open-access papers that
reproduce the ACSM table. Each claim was re-opened by an independent verifier.

## New rules

None.

## Changed rules

None. "ACSM intensity bands" (cardio-health.md) stays as it is: the 2011 position-stand bands as
the reference, with the GETP 10th edition values and the 84% HRR cap recorded as a convention.

## Retired rules

None.

## Dropped claims

Seven claims, D255 to D261 in docs/dropped-claims.md. The newest editions could not be opened
from an acceptable source:
- GETP 11th edition: only an adapted table in a Frontiers in Stroke paper, with %HRmax and RPE
  cut-offs equal to the 2011 bands and no %HRR column (D255).
- GETP 12th edition: the ACSM crosswalk lists no change to the aerobic intensity table but has
  no numbers; the free sample was not reachable (D256).
- The vigorous/near-maximal %HRR boundary (84/85 or 89/90) has no source in either edition (D257).
- The ACSM/ESSA 2025 statement (Bishop 2025) proposes five intensity labels; only the abstract
  could be opened, so it could neither confirm nor change any number (D258). It is the one to
  open by another route (library access), since it may change how zones are named.
- Three secondary papers restate the 2011 bands but are not ACSM adult documents (D259, D260),
  and no PAGAC 2018 band table was found (D261).

So the vigorous upper limit (capped at 84% HRR in `coach/zones.py`, a convention that fits both
2011 and GETP 10) stays unchecked against the current guideline. Retry if the 12th edition sample,
an open paper reproducing its table, or the ACSM/ESSA full text becomes openable.

## Check output

`scripts/research.py check`: 865 sources, 461 rules (81 strong, 257 moderate, 123 emerging); 0 errors, 0 warnings; ruff clean; 895 passed, 1 skipped. No new source IDs, so no online source check applied.
