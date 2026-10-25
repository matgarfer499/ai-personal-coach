# Research log: power balance core agility

Date: 2026-10-24

## Topic

power balance core agility

## What was searched

Topic run with the saved workflow (`.claude/workflows/research.js`, run wf_7303e72a-4ef): 4 groups,
13 items, one searcher and one independent verifier per group (8 agents, no failed groups).
Sources were read through NCBI E-utilities (abstracts), PubMed Central (full text) and Crossref.

1. **Plyometrics and power** (strength-hypertrophy.md): plyometric dose and progression for
   adults; plyometrics alone and combined with resistance training (complex and contrast
   training); power and velocity-based loading; placement of power work in a session and
   recovery between sessions.
2. **Balance training** (strength-hypertrophy.md, recovery-habits.md): effects and dose in healthy
   adults aged 18-64; transfer to strength, power and sport; balance and neuromuscular training for
   ankle and knee injury prevention.
3. **Core training** (strength-hypertrophy.md, recovery-habits.md): planks, anti-rotation work and
   loaded carries for performance and trunk endurance; whether compound lifts train the trunk;
   management of and return to training after an abdominal wall muscle strain, including imaging
   and hernia red flags.
4. **Jump rope and agility** (cardio-health.md): jump rope training effects and intensity; agility
   and change-of-direction training in recreational adults; injury risk and volume progression for
   jumping.

Because this is a topic run covering only part of each file, no `Evidence checked on` date was
changed.

## New rules

strength-hypertrophy.md, new section "Power and plyometrics":
- **Plyometric dose** (moderate): [S830], [S831]
- **Plyometrics alone and combined with lifting** (emerging): [S832], [S833], [S834], [S835],
  [S836], [S837], [S838]
- **Loads for power and jumping** (moderate): [S839], [S840], [S841]

strength-hypertrophy.md, new section "Balance and trunk training":
- **Optional balance training for younger adults: dose** (emerging): [S842], [S396], [S843]
- **Balance gains are task specific** (emerging): [S844], [S845]
- **Trunk (core) training: an add-on for trunk endurance and balance** (moderate): [S849], [S850],
  [S851], [S852], [S853]
- **Compound free-weight lifts load the trunk** (emerging): [S854], [S855], [S856]

recovery-habits.md, section "Injury risk, pain and rehabilitation":
- **Abdominal wall strain: symptom-guided return** (emerging): [S857], [S858], [S859]. Contains
  referral triggers; see "Changed rules".
- **Balance work for ankle sprain prevention** (strong): [S846], [S847], [S848], [S600]

cardio-health.md, section "HIIT, SIT and moderate continuous training":
- **Jump rope as conditioning** (emerging): [S860], [S861], [S862], [S863]

34 new sources (S830 to S863): 24 meta-analyses, 5 systematic reviews, 3 narrative reviews, 2
other (lab studies). Reused: S396 (ACSM 2011, Files now also strength-hypertrophy) and S600
(Lauersen 2014). Summary counts in sources.md updated (825 to 859).

## Changed rules

- **Abdominal wall strain: symptom-guided return** (recovery-habits.md, new rule): needs a code
  and safety review. It adds referral triggers (abdominal pain after a direct blow that is not
  settling, especially on anticoagulants: possible rectus sheath hematoma; groin and lower
  abdominal pain reproduced by a resisted sit-up or forced cough or sneeze, or that keeps stopping
  training: possible athletic pubalgia). Nothing in `coach/` or `docs/safety.md` was changed; if
  these should become red flags in the safety table, that needs a separate, reviewed commit.

No existing rule was changed.

## Retired rules

None.

## Dropped claims

18 claims, appended to `docs/dropped-claims.md` as D230 to D247 (section "Research 2026-10-24:
power, balance, core and agility"). Main gaps:
- Session placement of plyometrics and recovery between sessions (D230), and foot-contact
  progressions (D231): no meta-analysis or position stand opened gives them.
- Plyometrics as a hypertrophy tool (D232): refuted by Deng 2024 (no lean mass effect).
- Abdominal wall strain imaging criteria, timelines, a growing lump as a validated hernia red flag
  and staged loading (D233, D243, D244, D245): only narrative reviews exist and they give none of
  these.
- Superiority of anti-rotation work or carries, and core training in untrained adults (D234,
  D235, D239).
- Verifier corrections to the core and trunk rules (D236 to D238, D240 to D242).
- Agility training effects in recreational adults (D246) and jump rope injury rates and volume
  progression for beginners (D247): no adult evidence found.

## Check output

`uv run python scripts/research.py check --worktree W --ids S830,...,S863`:

```
WARN  S857: no PubMed URL, title not checked online
859 sources, 459 rules (81 strong, 256 moderate, 122 emerging); 0 errors, 1 warnings
All checks passed!
366 passed, 1 skipped
```

The first run gave one error: PubMed 16529681 (Johnson 2006, S857) lists the retired DOI
10.1007/s11932-006-0038-8, which now redirects to an unrelated record (10.1007/BF00400429), while
Crossref resolves the paper to 10.1097/01.csmr.0000306528.74500.bf. The source keeps the correct
DOI and its URL now points to that DOI instead of PubMed, so the online check gives the warning
above instead of comparing DOIs. The PMID is kept in the Supports note. A maintainer may prefer to
teach the checker about retired PubMed DOIs instead.
