# How the knowledge base was built

The coach's advice comes from four files in `knowledge/`. This document explains how they were produced, what was checked, and where the limits are, so anyone forking the template can judge how far to trust it and rebuild it if the evidence moves on.

Research ran on 2026-10-24 inside Claude Code, using a multi-agent workflow: many independent agents, each with a narrow job, coordinated by a script. The project was built in two phases: Phase 1 produced the evidence base, Phase 2 the commands (the skills) and the `coach` package; Phase 2 also added the few sources its code needed.

## Results in numbers

| | |
|---|---|
| Domains | 4: strength and hypertrophy, nutrition, cardio and health, recovery and habits |
| Research topics | 33 (13 planned + 20 gaps found by completeness critics) |
| Agents | 152 (1 probe, 33 researchers, 105 checkers, 4 critics, 4 writers, 1 cross-domain reviewer, 4 harmonisation editors) |
| Tool calls | about 2,450 (web searches, page fetches, PubMed API calls) |
| Wall-clock time | about 75 minutes for research, plus about 8 minutes for harmonisation |
| Claims discarded by researchers before checking | 225 (source could not be opened, or did not support the claim) |
| Claims sent to independent checkers | 481 |
| Checker verdicts | 118 kept as written, 359 corrected, 0 rejected outright (4 more lost to malformed checker output and dropped) |
| Final rules in the knowledge files | 433 (after merging duplicates) |
| Final grades | 74 strong, 248 moderate, 111 emerging |
| Unique sources | 775 (258 meta-analyses, 81 systematic reviews, 15 umbrella reviews, 35 position stands, 74 guidelines, 92 RCTs, 85 cohort studies, 39 narrative reviews, 96 other) |

The most telling number is that independent checkers corrected three out of four claims. Most corrections were small (a confidence interval, a sample size, a population caveat, a grade one step too high), and that is exactly the kind of error that turns into confident nonsense in a coaching app if nobody checks.

The weak spot is the other side of that number: checkers rejected no claim outright, although they were told to reject when in doubt. They preferred fixing a claim (removing a source, lowering a grade, narrowing the population) to rejecting it. The real filter was earlier: researchers discarded 225 claims they could not back with an opened source. The independent number check below is what gives confidence that the corrected claims match their sources.

## The pipeline

```
                 4 domains x 2-4 subtopics (13)
                              |
                              v
  +-------------------------------------------------------+
  | RESEARCH   one agent per subtopic                      |
  |  - web search + PubMed E-utilities                     |
  |  - must open every source; claims it cannot confirm   |
  |    go to a "dropped" list                              |
  +-------------------------------------------------------+
                              |  8-16 graded claims each
                              v
  +-------------------------------------------------------+
  | VERIFY     independent checkers, 5 claims per batch    |
  |  - re-open every source themselves                     |
  |  - try to refute: numbers, population, grade           |
  |  - verdict: keep / revise / drop (default: drop)       |
  +-------------------------------------------------------+
                              |
                              v
  +-------------------------------------------------------+
  | GAPS       one completeness critic per domain          |
  |  - compares verified claims to a required checklist    |
  |  - each gap -> new research + verify round             |
  +-------------------------------------------------------+
                              |
                              v
        source de-duplication across domains (script)
                              |
                              v
  +-------------------------------------------------------+
  | WRITE      one writer per domain file                  |
  |  - may only use verified claims and their source IDs   |
  +-------------------------------------------------------+
                              |
                              v
  +-------------------------------------------------------+
  | REVIEW     one cross-domain reviewer                   |
  |  - contradictions between files, overgrading, safety   |
  +-------------------------------------------------------+
                              |
                              v
  +-------------------------------------------------------+
  | HARMONISE  one editor per file, same decision list     |
  |  - one answer per question across all four files       |
  +-------------------------------------------------------+
                              |
                              v
        mechanical checks + spot-checks (scripts)
```

## Rules every agent followed

**Population.** Ordinary adults who want a lasting change in body and health: beginners, returning lifters and recreational gym-goers. Not elite athletes. When evidence came from young trained men, the rule says so.

**Source preference.** Position stands and guidelines (WHO, ACSM, ISSN, EFSA, NSCA, AESAN and others), umbrella reviews, meta-analyses and systematic reviews first. Single trials and narrative reviews only as support. No blogs, news or commercial sites.

**Open it or drop it.** A claim needed a source the agent had actually opened, abstract or full text, and that text had to support the claim and its numbers. Citing from memory was not allowed. Anything that could not be confirmed was dropped, not softened.

**One grading rubric.**

| Grade | Meaning |
|---|---|
| strong | Position stand or guideline, and/or several concordant meta-analyses or an umbrella review |
| moderate | One good meta-analysis, several consistent RCTs, or a position stand resting on limited data |
| emerging | Few trials, mostly observational or mechanistic data, or meta-analyses that disagree |

**Conflicts are stated.** Each rule has a field for where the evidence conflicts or depends on the person. Popular advice that outruns the evidence is written down as such (for example, the "fat-burning zone" or fasted cardio).

## Getting past paywalls and bot walls

The first probe showed that PubMed's web pages return a cookie wall to automated fetchers. Agents therefore read abstracts through NCBI's E-utilities API, confirmed DOIs through the Crossref API, and used PubMed Central for open-access full text. Publisher pages that block bots (HTTP 403) were handled the same way: the DOI was confirmed through Crossref and the content read from PubMed. Guideline documents (WHO, EFSA, AESAN, NICE, Spanish Ministry of Health) were read directly.

## Checks after writing

- **Every PubMed ID resolves to the cited paper.** All 715 sources with a PubMed ID were looked up in one batch and their titles compared with the citations: 715 of 715 matched.
- **Every other source is reachable.** The 60 sources without a PubMed ID were checked through Crossref (DOI exists) and a direct request. Pages that block automated requests had their DOI confirmed through Crossref.
- **Numbers match the papers.** For 40 randomly chosen sources, every decimal figure recorded as supporting evidence (effect sizes, confidence intervals, percentages) was searched for in the full PubMed abstract: 204 of 204 figures found (one paper writes decimals as "3·08", which needed a manual check). This checks that the recorded evidence matches the paper; it does not re-judge whether each rule draws the right conclusion from it.
- **Cross-references.** Every source ID cited in a knowledge file exists in `sources.md`, and every source there is cited at least once.
- **Template.** Every rule has exactly one grade from the rubric.

## Harmonisation: one answer per question

Written separately, the four files disagreed in about twenty places, for example:
- protein targets for older adults
- when medical clearance is needed
- how often to weigh
- whether beginners may do all-out sprints
- blood-pressure thresholds
- caffeine doses

A single decision list fixed one answer for each, grounded in the cited sources and erring on the safe side. All four files were then edited against it. The reviewer also caught arithmetic slips (a percentage that did not match its own numbers, inconsistent "standard drink" conversions) and grades one step too high; these were fixed or the number removed.

## Gap round

A second, smaller round on 2026-10-24 closed four gaps left by Phase 1: anchor numbers needed by the Phase 2 tools, four weak sources, bone health, and the dropped-claims list.

| | |
|---|---|
| Agents | 8: 4 researchers (Sonnet, medium effort) and 4 verifiers (Opus, high effort), each verifier starting as soon as its researcher finished |
| Researcher topics | anchors; bone health plus weak sources; dropped-claim retries batch A (14 entries); batch B (14 entries) |
| Tool calls | 388, about 24 minutes wall-clock |
| Dropped claims triaged (by hand, no agents) | 229: 30 refuted or myth, 147 low value for an ordinary-adult coach, 52 useful but unconfirmed |
| Retried | 40 entries: 23 recovered, 2 partly recovered, 1 resolved as a negative finding, 14 still dropped |
| Claims sent to verifiers | 34 (13 more discarded by researchers before verification) |
| Verifier verdicts | 16 kept, 17 revised, 1 dropped |
| New rules | 14 (5 strong, 5 moderate, 4 emerging); 2 existing grades changed (one up, one down) |
| Sources | 43 added (S776-S818); 4 weak sources retired (S182, S204, S663, S678; their IDs are not reused) |
| Totals after the round | 447 rules (80 strong, 251 moderate, 116 emerging); 814 sources |

**What changed in the method.** Verifiers had to return a verbatim passage from the text they opened that contains the claim's numbers, and were told that a claim whose numbers are not in the opened text is a drop, not a revise. Revisions fell from three in four claims to one in two. Most of the 17 revisions fixed a population description, an attribution or a grade while the numbers stood. There was still only one outright drop. Most filtering again happened earlier: researchers discarded 13 claims they could not confirm. Retried claims were also told why they failed in Phase 1 and to try a different route (PMC full text, the issuing body's own site, an institutional repository, or a peer-reviewed paper that reproduces the table).

**Anchors for Phase 2.**
- ACSM aerobic intensity bands: confirmed. A full-text copy of Garber 2011 (Table 5) was opened. A PMC-open paper reproduces the GETP 10th edition table, which caps vigorous at 84% HRR instead of 89%. The 11th and 12th editions could not be opened.
- ACSM resting-BP contraindication: confirmed only through peer-reviewed secondary sources quoting GETP 9th edition (2013). No GETP text was opened.
- Lally 2010 66-day median: confirmed through the full text of a 2024 systematic review that states it. The Lally paper itself was not opened.

**Bone health.** Five rules, built on a UK consensus statement, an ESSA position statement, a Cochrane review, five meta-analyses and the LIFTMOR trial.

**Weak sources.**
- The two EFSA press releases were replaced by EFSA's 2017 Dietary Reference Values summary report.
- The NSCA textbook excerpt was replaced by two peer-reviewed Australian surveys. No professional-body scope-of-practice statement was found, so the rule dropped from moderate to emerging.
- The eating-disorder charity page was replaced by NICE NG69 and a coach-education study. The conversation format is now labelled a coaching convention.

**Checks.** Scripts implementing the same checks as Phase 1 were run on the whole base:
- Every cited ID exists and every source is cited (814 of 814).
- Every rule has exactly one grade (447 of 447).
- The files contain no en or em dashes.
- For the 41 new sources with a PubMed ID, the PubMed title matches the citation (41 of 41). 66 of 73 decimal figures in their "Supports" notes appear in the abstract. The other 7 are full-text figures: 5 were found in the opened PMC full text by script, and 2 (ESPEN 1.6 L and 2.0 L) in the opened guideline PDF by hand.

**Limitations of this round.**
- Two verifiers read a page through a web-fetch tool that returns a model summary rather than raw text: the EAPC 2022 table and the Brubaker review. Those numbers match the Phase 1 checks but were not read verbatim this time.
- Errata for LIFTMOR 2018, Kelley 2013 and Whittaker 2021, and the correction to the INTERLIVE meta-analysis, could not be opened.

## Borg alignment (Phase 2, 2026-10-24)

The knowledge files used a coach convention for Borg 6-20 zones (moderate 12-14, vigorous 15-17) that overlapped the ACSM 2011 bands (moderate 12-13, vigorous 14-17) at RPE 14. With the user's agreement, every coach-convention aerobic Borg band now follows ACSM 2011 ("ACSM intensity bands", [S396], [S776]):
- cardio-health.md: the key-rules line and "0-10 effort scale and talk-test anchors" use 12-13 / 14-17; the two beta-blocker rules use 12-13 for moderate and set the ceiling at "no sustained vigorous work (RPE 14 or more) without medical clearance" instead of "about 14-15"; the conflicts note under "ACSM intensity bands" no longer describes an overlap.
- recovery-habits.md: the elevated-BP rule keeps the ACSM T2D figure (RPE 10-12) but its ceiling is now the ACSM moderate band of 12-13 instead of the convention's 12-14.
- Left as written, because they are not aerobic zone bands or are a source's own numbers: the RIR-to-Borg mapping for lifting (2-3 RIR, about 13-15) in strength-hypertrophy.md and recovery-habits.md, a labelled convention that now spans the top of moderate and the start of vigorous; pregnancy RPE 13-14 (recovery-habits.md, from the pregnancy guidelines); RPE 10-12 for elevated BP (recovery-habits.md, from the ACSM 2022 T2D consensus); ICFSR's aerobic Borg 12-14 and resistance Borg 15-18 (strength-hypertrophy.md, quoted as evidence); and the CR10 equivalents.
- No grade changed and no "Evidence checked on" date moved: this was a convention change, not a new evidence check.

## Phase 2 source additions

Phase 2 code needs some equations' coefficients, and every constant in `coach/` must come from a knowledge rule. Where a rule named an equation but did not spell it out, the original paper was opened and the equation added to the rule:
- [S819] Mifflin 1990 (PubMed abstract, opened 2026-10-24): the sex-specific Mifflin-St Jeor coefficients, now in nutrition.md "Default RMR equation: Mifflin-St Jeor". Checked with `scripts/check_knowledge.py --online --ids S819` (DOI and every decimal match). Unlike Phase 1 sources, it was opened by one session, not also by an independent checker.

## Limitations

- **Abstracts, not always full text.** For paywalled papers, agents judged claims on the abstract. Numbers that appear only in the full text were left out where possible.
- **Skewed evidence base.** Much resistance-training research comes from young men, much weight-loss research from people with obesity, and much cardio research from short supervised trials. Rules note this where it matters.
- **Some anchor numbers rest on secondary sources.** Phase 1 dropped figures whose primary source is a book or a paywalled guideline rather than cite them from memory. The gap round recovered the ACSM intensity bands from the full position stand. It also recovered the 66-day habit median and the ACSM resting-BP wording, but only through peer-reviewed papers that quote them. The current GETP editions and the Lally paper itself were not opened. See `docs/dropped-claims.md`.
- **AI agents check AI agents.** Independent checkers and a reviewer reduce errors but do not replace a human expert's review. Corrections from qualified professionals are welcome.
- **Some numbers are conventions, not evidence.** Every such case is labelled in the rule text ("coaching convention", "heuristic", "product policy"), about 40 rules in total.
- **Some rules are product choices.** A few thresholds (for example, four weeks of moderate cardio before sprint intervals) are conservative product decisions built on the cited guidance, and the rule text says so.
- **Rate limits shaped the run.** About fifteen agents shared one IP address against NCBI's limit of three requests per second, which slowed some topics considerably.
- **Snapshot in time.** Evidence was checked on 2026-10-24. New meta-analyses and position stands will change some rules.

## Rebuilding or extending it

The research prompts, grading rubric and verification rules are summarised above. To update a domain:
1. Rerun research and verification for the topics that changed.
2. Keep source IDs stable and add new ones at the end of `sources.md`.
3. Rerun the cross-domain review before merging.

For a run of this size, cap the gap round at about two topics per domain and verify claims in batches of about eight. That roughly halves the cost of the gap phase with little loss of coverage.
