# Research log: beta2 screening running strength food

Date: 2026-11-08

## Topic

Topic run for the second simulated beta (plan "Research needed"), branch
`research/2026-11-08-beta2-screening-running-strength-food`. Four groups:
- Preparticipation screening and waiting for clearance: did ACSM GETP 11 or 12 change the 2015
  algorithm; ESC 2020 sports cardiology screening before leisure exercise; activity and diet
  while waiting for clearance; antihypertensive drug classes and exercise.
- Recreational running: half-marathon build-up and the taper's reference volume.
- Resistance training: 1RM prediction accuracy; what counts as vigorous or near-maximal lifting.
- Food yields and household portions: cooking yield factors; energy reference values by age.

## What was searched

The saved workflow `.claude/workflows/research.js` ran the 4 groups (one searcher and one
verifier each; 7 agents, none failed). Sources: web search, PubMed E-utilities, Crossref,
academic.oup.com (ESC 2020 full text), eshonline.org (EAPC 2018 PDF), ars.usda.gov (USDA cooking
yields xlsx and PDF). Rules applied: open it or drop it, source preference, one grading rubric
(docs/research-methodology.md).

## New rules

- cardio-health.md "Blood pressure medicines and exercise" (moderate) [S888], [S746]: never
  change or question a BP medicine; ACE inhibitors, ARBs and calcium channel blockers are the
  preferred drugs in exercising people; beta-blockers can lower aerobic capacity (intensity by
  the existing beta-blocker rules); anti-doping notes for competitors. **Touches medications:
  needs a code and safety review** before `coach/` uses it (planned `bp_medication` token, PR 2).
- cardio-health.md "Keep most running easy: pyramidal or polarized intensity" (emerging)
  [S889], [S890], [S891], [S892], [S893]: about 70% or more of volume easy, 30% or less at
  threshold or harder; no distribution clearly best.
- nutrition.md "Raw to cooked weight for meat and poultry: USDA cooking yields" (strong) [S894]:
  raw = cooked / (yield / 100) for chicken pieces with skin and ground beef.

## Changed rules

None. No safety threshold changed. Screening outcome: no opened source shows that GETP 11 or 12
changed the ACSM 2015 preparticipation algorithm (D264), and the ESC 2020 class and level for
screening before leisure exercise could not be read (D265), so "ACSM 2015 screening algorithm"
stands as is. S746 gains a Supports passage on drug classes and lists cardio-health.

## Retired rules

None.

## Dropped claims

12, recorded as D264 to D275 in docs/dropped-claims.md (EFSA energy values twice, D274 and D275): GETP 11/12 screening changes (no
source states a change); ESC 2020 screening class and level (table is an image); activity and
diet while waiting for clearance (no guideline opened); class-specific post-exercise
hypotension and heat (not in the opened text); half-marathon build-up parameters (no review
found); pre-taper reference volume definition (not stated in Bosquet 2007 or Wang 2023);
"avoid threshold plans" (contradicted by newer network meta-analyses); 1RM equation accuracy by
reps (no systematic review found); resistance-training intensity bands and heavy-lifting advice
in hypertension (not in the opened abstract); yields for rice, pasta, legumes, fish, eggs and
skinless breast (not in the USDA meat table); EFSA energy reference values by age (full text
blocked, twice).

## Check output

`scripts/research.py check --ids S888,...,S894`: 890 sources, 469 rules (82 strong, 261
moderate, 126 emerging); 0 errors, 1 warning (S894: no PubMed URL, title not checked online; it
is a USDA data table). ruff: all checks passed. pytest: 1067 passed, 1 skipped.
`check_knowledge.py --claims`: no warning on the three new rules (51 pre-existing warnings).
