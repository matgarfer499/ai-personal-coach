# Research log: dropped claims

Date: 2026-10-24

## Topic

`/research dropped`: the 12 claims in `docs/dropped-claims.md` marked "Not retried in the gap
round (40-claim cap)": D045, D064, D066, D074, D077, D157, D165, D167, D177, D180, D202, D228.
Branch `research/2026-10-24-dropped-claims`.

## What was searched

The saved workflow `.claude/workflows/research.js` ran 4 groups, each with one low-effort
searcher (web search, PubMed E-utilities, Europe PMC, Crossref) and one high-effort verifier
that re-opened every source and tried to refute each candidate (8 agents, none failed):
- protein-energy: D064, D066, D157
- supplements: D074, D077, D167
- training-recovery: D045, D177, D228
- sleep-behaviour-screening: D165, D180, D202

Phase 1 rules applied: open it or drop it, source preference, one grading rubric
(`docs/research-methodology.md`).

## New rules

- nutrition.md "Supplement evidence tiers (ISSN 2018)" (moderate) [S326], [S821], [S822],
  [S823]: suggest category I supplements only; HMB is not suggested for muscle gain although
  the ISSN lists it in category I, because three independent meta-analyses found no fat-free
  mass benefit (D074).
- recovery-habits.md "Foam rolling before training: optional" (moderate) [S826], [S767],
  [S827], [S828]: an optional warm-up part with a range-of-motion gain like stretching and no
  meaningful performance cost; "keep it brief" is labelled a coaching convention (D177).

## Changed rules

No change touches a safety threshold (calorie floors, BP bands, red flags, screening, pregnancy,
medications); `coach/` and `docs/safety.md` are untouched.
- nutrition.md "Older adults: protein targets" (grade unchanged, moderate): the conflicts note
  now cites the NNR 2023 protein scoping review [S820] (1.2-1.5 g/kg/day from cohort studies,
  mostly observational) instead of the EU Knowledge4Policy summary, and drops the unconfirmed
  DGE 1.0 g/kg figure. Rule text unchanged (D066).
- nutrition.md "Vitamin D" (grade unchanged, strong): the rule adds "do not suggest vitamin D
  to improve strength, muscle mass or performance"; evidence adds two meta-analyses with no
  muscle benefit [S824], [S825]; conflicts note older positive findings in deficient or 65+
  people (D077). The muscle evidence on its own would be moderate; the strong grade rests on
  the existing [S252], [S253].
- recovery-habits.md "Self-monitoring tied to a goal and a review" (grade unchanged, moderate):
  adds NICE PH49 [S829]: agreed goals, planned reviews with feedback, if-then plans for lapses,
  and continued monitoring after a programme (D180).

## Retired rules

None.

## Dropped claims

Recorded in `docs/dropped-claims.md` under "Research 2026-10-24":
- D045 still dropped: no lift-specific novice 1RM percentages over 8-12 weeks found.
- D064 still dropped: no guideline or trial tests protein from goal weight or fat-free mass.
- D066 DGE part still dropped: no DGE document opened.
- D157 still dropped: no peer-reviewed net walking cost per kg per km.
- D165 still dropped: no adult benefit shown (blue-light glasses meta-analysis: no effect).
- D167 still dropped: melatonin evidence is in adults with diseases; nothing for healthy adults.
- D228 still dropped: Lilja 2023 studies the mechanisms behind the trial already cited as
  [S772]; it adds nothing to "NSAIDs are not for training soreness".
- D202 resolved with no change: already cited as [S656], abstract re-opened.

## Check output

`uv run python scripts/research.py check --worktree W --ids S820,...,S829` (index rebuilt):

```
WARN  S820: 1.2 from the Supports note is not in the abstract
WARN  S820: 1.5 from the Supports note is not in the abstract
WARN  S820: 1.2 from the Supports note is not in the abstract
WARN  S820: 1.0 from the Supports note is not in the abstract
WARN  S820: 1.2 from the Supports note is not in the abstract
WARN  S829: no PubMed URL, title not checked online
825 sources, 449 rules (80 strong, 253 moderate, 116 emerging); 0 errors, 6 warnings
```

- S820: the figures come from the full text, not the abstract. Confirmed by this session in the
  Europe PMC full text (PMC10770649): "a safe intake of up to 1.2-1.5 g protein/kg BW per day"
  and "1.0-1.2 g/kg BW per day for healthy older adults".
- S829 is a NICE guideline with no PubMed record; its recommendations page was opened by the
  searcher and the verifier.
- DOIs of the other eight new sources match PubMed.

## Corrections after the milestone review

An independent review of this branch (same day) led to a second commit:
- "Supplement evidence tiers (ISSN 2018)": the HMB exception is about muscle mass only; the
  conflicts note adds the modest function gains in older adults from [S823]; [S256] is cited.
- "Vitamin D": the conflicts note no longer says low-vitamin-D groups gained strength (the
  54-trial analysis [S824] found no benefit in them either).
- "Older adults: protein targets": the Dutch review is quoted as finding insufficient evidence
  of benefit, not "no added benefit".
- [S326] Supports note now records the ISSN Table 3 tiers the new rule relies on.
- D228 annotation reworded.

As in Phase 1, the claims were found by one agent and checked by an independent one; no human
expert has reviewed them. Review before merging.
