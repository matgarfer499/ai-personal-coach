# Research log: beta3 yields running pace return

Date: 2026-11-08

## Topic

Three generic questions for the third beta round: cooking yield factors for grains, pasta,
legumes and vegetables (retry of D273); half-marathon pacing and training volume for
recreational runners (retry of D268 from another angle); return to running after a lower-limb
injury.

## What was searched

The saved research workflow (3 groups, 9 items, 6 agents, no failed groups). Group 1 opened the
FAO-hosted Bognar 2002 yield tables (BFE-R--02-03); USDA Handbook 102 returned an HTML page.
Group 2 searched PubMed E-utilities for race-time prediction (Riegel) in recreational runners,
easy-run pace guidance and half-marathon training predictors. Group 3 searched PubMed for
return-to-running criteria, walk-run programmes and consensus statements.

## New rules

- nutrition.md "Dry or raw to cooked weight for grains, pasta, legumes and vegetables: Bognar
  yield factors" (moderate, S895).
- cardio-health.md "Half-marathon goal pace from a recent race" (emerging, S896).
- cardio-health.md "Training volume and half-marathon performance" (emerging, S896, S897, S898).
- recovery-habits.md "Return to running after a lower-limb injury: criteria to start"
  (emerging, S899, S900, S901).
- recovery-habits.md "Return to running after a lower-limb injury: graded walk-run" (emerging,
  S901, S902).

## Changed rules

None. No safety threshold changed.

## Retired rules

None.

## Dropped claims

- D276: chickpea and canned versus dry yields (no row in Bognar 2002; USDA AH102 not opened).
- D277: easy or long-run pace as a set range slower than race pace (no guideline, position stand
  or review found).
- D278: restarting at a set fraction of pre-injury weekly distance or long run (no review or
  consensus gives one).

## Check output

`scripts/research.py check --ids S895..S902`: ok; 898 sources, 474 rules (82 strong, 262
moderate, 130 emerging); 0 errors, 8 warnings (no PubMed URL, title not checked online, for the
eight new IDs). `check_knowledge.py --claims`: 0 errors, 51 warnings, all on rules that existed
before this run (no new strong rule).
