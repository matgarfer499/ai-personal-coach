# Research log: beta fixes running and citations

Date: 2026-11-08

## Topic

Beta tester fixes in two groups: (1) running: load progression, common injuries, tapering for a goal
race, protein for endurance runners, heart rate anchors and energy needs of recreational runners, an
upper limit on the rate of loss, and diet during a pending medical review; (2) citation fixes for four
nutrition rules whose numbers were not backed by a cited source's `Supports:` line ("Minimum dietary
fat", "Dietary fibre", "Protein during fat loss", "Deficit size for weight loss (overweight and
obesity)"), plus which body weight to use for protein targets in obesity. This is a topic run, so no
`Evidence checked on` date was changed.

## What was searched

The saved research workflow (`.claude/workflows/research.js`), with every passage checked as verbatim
by an independent agent. No failed groups.
- PubMed and Europe PMC (abstracts through E-utilities) for running injury and training load cohorts
  and reviews, tapering meta-analyses, protein requirements of endurance athletes, rate of weight loss
  and gallstones, deficit size in obesity guidelines, and body weight for protein prescription.
- Full texts: ISSN 2026 diets for body weight reduction (PMC13665703), EASO 2015 (PMC5644856),
  ISSN 2018 review (PMC6090881), ACSM/AND/DC 2016 (Dietitians of Canada reprint PDF), WHO 2023
  carbohydrate guideline (WHO IRIS PDF).
- Not reachable: NICE CG189 and NG246 pages for a kcal deficit (403 or bot page), NHLBI 1998
  (captcha), Obesity Canada 2020 full text (not found through E-utilities).

## New rules

- **Running load progression: cap single-run spikes, not just weekly totals** (cardio-health.md,
  "Weekly activity targets and patterns", emerging): [S870], [S871], [S872], [S873]
- **Taper before a goal race** (cardio-health.md, "Weekly activity targets and patterns",
  moderate): [S874], [S875], [S876]
- **Common running injuries and who is most at risk** (recovery-habits.md, "Injury risk, pain and
  rehabilitation", moderate): [S877], [S878]
- **Daily protein target for endurance runners** (nutrition.md, "Protein", moderate): [S185],
  [S879], [S880], [S881]
- **Upper limit on rate of loss: about 1.5 kg per week** (nutrition.md, "Weight change, deficits and
  surpluses", emerging): [S886]. A new safety-type ceiling with no code behind it yet: implementing it
  in `coach/` (and choosing the window as a `# convention:`) needs a code and safety review.

18 new sources (S870 to S887): 3 cohorts, 4 systematic reviews, 3 meta-analyses, 2 position stands,
2 guidelines, 1 narrative review, 3 other. Existing sources kept their IDs: S185 (ISSN 2017 protein),
S190 (Helms 2014), S325 (ACSM/AND/DC 2016) and S326 (ISSN 2018). The `Supports:` lines of S325 and
S326 were rewritten to keep their carbohydrate (and, for S326, supplement tier) quotes and add the fat
passages, plus the energy-restriction protein passage for S325.

## Changed rules

Rules that back code constants come first. Their Rule-line numbers did not change, so no code or
safety review is triggered by them:
- **Deficit size for weight loss (overweight and obesity)** (nutrition.md, strong): numbers unchanged
  (500-750 kcal/day). Added EASO 2015 [S885] as a second, concordant guideline (600 kcal/day deficit),
  so the strong grade no longer rests on one US guideline; also added to the key-rules line.
  Sources: [S167], [S885].
- **Daily protein target for people who lift** (nutrition.md, moderate): numbers unchanged (default
  1.6 g/kg/day, range 1.4-2.2). Added to conflicts that there is no consensus on which body weight to
  use; in hospital nutrition support ideal body weight is reported most often (73.2% of 41
  publications). The fat-free mass or goal weight choice stays a practical heuristic. Added [S887].

Citation fixes:
- **Protein during fat loss** (nutrition.md, moderate): Rule now gives 1.6-2.2 g/kg/day for ordinary
  lifters (ISSN 2026, [S883]); 1.8-2.2 g/kg/day is labelled a convention inside that range; lean,
  trained clients in a sustained deficit up to 1.9-3.2 g/kg/day ([S883]), with Helms 2014's
  2.3-3.1 g/kg of fat-free mass as the older figure ([S190]); overweight beginners 1.6-2.0 g/kg
  labelled a convention. Removed [S185] (its quote supports 1.4-2.0 for exercisers, not this rule) and
  the unconfirmed claim that ISSN 2017's 2.3-3.1 came from Helms. Added [S883], [S325], [S884].
  Code follow-up, not done here: `PROTEIN_DEFICIT = (1.8, 2.2)` in `coach/macros.py` is unchanged in
  value but is now a labelled convention, so its comment needs `# convention:` and an entry in
  `docs/conventions.md`.
- **Minimum dietary fat** (nutrition.md, strong): numbers unchanged (at least 20% of energy and
  0.5 g/kg/day; default 20-35%). Each number is now in a cited `Supports:` line: 20% and 20-35% in
  [S325], 0.5 g/kg in [S326], 20-35% in [S330]. "During a hard deficit" became "short-term".
- **Dietary fibre** (nutrition.md, strong): at least 25 g/day and 400 g/day of vegetables and fruit,
  largest benefit at 25-29 g/day, possible further benefit above 30 g/day. The unsupported "ideally
  25-35 g" was removed. Replaced [S205] (a news release about fats) with the WHO 2023 guideline itself
  [S882]; sources now [S882], [S206], [S795]. Code follow-up, not done here: the `FIBRE_MIN_G` comment
  in `coach/macros.py` still says "ideally 25-35"; the value 25 is unchanged.

## Retired rules

None.

## Dropped claims

9 claims, appended to `docs/dropped-claims.md` as D255 to D263: field HRmax and resting HR protocols
for runners (no review found); PAL for recreational runners (no opened source); running-specific pain
model, return-to-run and bone stress injury data (not in the reviews); ACSM/AND/DC 1.2-2.0 g/kg
protein (abstract has no number); NICE 600 kcal/day deficit (site blocked); Obesity Canada deficit
(full text not found); diet during a pending cardiac or blood pressure review (no guideline; existing
red-flag rule covers it); day-to-day weight fluctuation (no source beyond S290); a 0.5-1 kg/week
guideline rate (not confirmed; only the 1.5 kg/week ceiling was).

## Check output

`uv run python scripts/research.py check --worktree W --ids S870,...,S887`:

```
WARN  S882: no PubMed URL, title not checked online
WARN  S883: 2.5 from the Supports note is not in the abstract
WARN  S883: 4.2 from the Supports note is not in the abstract
WARN  S885: 0.5 from the Supports note is not in the abstract
883 sources, 466 rules (81 strong, 260 moderate, 125 emerging); 0 errors, 4 warnings
All checks passed!
895 passed, 1 skipped
```

Warnings resolved: S882 is the WHO guideline (ISBN, no PubMed record), opened as the WHO IRIS PDF.
S883's 2.5 and 4.2 ("2.5-4.2 g/kg FFM") and S885's 0.5 ("about 0.5 kg weekly") were confirmed in the
opened PMC full texts (PMC13665703 and PMC5644856) by re-fetching them.

## Limits

- The running rules rest on observational cohorts and on taper meta-analyses in trained athletes; no
  half-marathon or recreational-runner trials.
- The 1.5 kg/week ceiling comes from one 1995 analysis of five reports and one outcome (gallstones).
- The runner protein rule relies on position stands and two small tracer studies in 8 men each.
