---
name: research
description: Use when someone asks to refresh or extend the coach's evidence base (/research), when `coach knowledge stale` lists files past their reminder, or to retry claims dropped in earlier research.
argument-hint: "topic | <file>.md | stale | dropped"
---

# /research

Updates `knowledge/` from new evidence on a separate branch, `research/<YYYY-MM-DD>-<slug>`, for
a person to review and merge. It never merges and never changes the coach's code.

## When to use

- `/research stale`: the knowledge files `coach knowledge stale` lists (the 4 oldest; say which
  wait for the next run).
- `/research nutrition.md`: one knowledge file.
- `/research "creatine for older adults"`: a topic.
- `/research dropped`: claims in `docs/dropped-claims.md` marked "Not retried".
- It can run in the middle of coaching, but research branches are pushed: never put personal or
  client data (names, health details, measurements, goals, injuries) in a topic, a slug, a branch
  name, a search query, the log or a commit message. Turn the question into a generic one ("creatine
  for older adults", not "creatine for my client's knee"). If the topic cannot be asked without
  that data, ask a general version or do not run it.
- Not to change a safety threshold in code.

## Reads

- `knowledge/index.md` for files, sections and rule headings; a rule's text with
  `uv run python -m coach knowledge section FILE "HEADING"`.
- `knowledge/sources.md` only by ID: `grep -n -A6 '^### S123$' knowledge/sources.md`. Never whole.
- `docs/research-methodology.md`, "Rules every agent followed": the rules the workflow applies.
- For `dropped`: `docs/dropped-claims.md` entries, found with grep.

## Steps

1. **Scope.** Turn the argument into 1 to 4 groups, each `{label, brief, items}`:
   - `stale` or a file: one group per file (a file with many sections may split into two);
     brief "evidence newer than the file's Evidence checked on date (DATE) that would add,
     change or retire a rule: new guidelines, position stands, meta-analyses"; items are the
     file's `##` sections from the index.
   - a topic: one or two groups; brief from the request; items are the questions to answer.
   - `dropped`: the entries marked "Not retried", at most 4 per group; each item is
     `Dxxx: <claim> (dropped because: <reason>)`.
2. **Branch.** `uv run python scripts/research.py start "SLUG TEXT" --worktree-root WT_ROOT`
   (WT_ROOT: a folder outside the repo, such as the session scratchpad). It prints `branch`,
   `worktree` (W below) and `log`. Run every command from the repo root; edit files only
   inside W.
3. **Search and verify.** Run the saved workflow: Workflow tool with
   `scriptPath: "<repo>/.claude/workflows/research.js"` (absolute path) and
   `args: {"today": "YYYY-MM-DD", "groups": [...]}`. It returns `verified` claims (each with
   sources and verbatim passages, checked by an independent agent) and `dropped` ones.
4. **Integrate** each verified claim in W:
   - Sources: one new entry per new source at the end of `knowledge/sources.md`, with the ID from
     `uv run python scripts/research.py next-id --knowledge-dir W/knowledge` (then the next
     number), laid out like
     the last entry (citation; Type, DOI, Files; URL; Opened; Supports with the verbatim
     passage: only the sentences that carry the claim's numbers, at most about 500 characters,
     since it is quoted from a copyrighted text). Update the counts in its Summary. A source already listed keeps its ID.
   - `new_rule`: a `### Heading` in the right section, with the same fields as its neighbours
     (Rule, Evidence, Grade, Applies to, Individual variation / conflicts, Sources).
   - `change_rule`: edit the rule; keep its heading unless the meaning changed.
   - `retire_rule`: remove it, and any line in the file's key-rules list that points to it.
   - Files covered by a `stale` or file run: set the header's `Evidence checked on` to today.
     A topic or `dropped` run checks only part of a file, so it leaves the date alone.
   - `failed_groups` from the workflow: say so in the log; those items stay as they were.
   - Dropped: for `dropped`, add `**Research YYYY-MM-DD: recovered**` or `**...: still dropped**`
     with the reason to each entry; otherwise append new entries to `docs/dropped-claims.md`.
5. **Check.** `uv run python scripts/research.py check --worktree W --ids NEW_IDS` rebuilds the
   index and runs the offline checks plus the online ones for the new IDs. Fix every error. For
   each warning (a decimal not in the abstract), confirm the number is in the full text you
   opened, or remove it.
6. **Log.** Fill every section of W's log file: what was searched; new, changed and retired
   rules with grades and IDs; dropped claims and why; the check output.
7. **Finish.** `uv run python scripts/research.py finish --worktree W --message
   "docs(knowledge): research SLUG"`. It refuses a missing or unfilled log, any change outside
   the paths under Writes, and failing checks (knowledge checks, online checks for every new
   source ID it finds, ruff and pytest); then it commits on the research branch and pushes it. Then stop: never merge, never open a
   pull request unless asked.

## Writes

- Only inside the worktree: `knowledge/*.md`, `knowledge/index.md`, `docs/dropped-claims.md`,
  `docs/research-log/YYYY-MM-DD-SLUG.md`, and the rule and source counts line of `README.md`
  (the index build rewrites it; never edit it by hand). One commit on `research/YYYY-MM-DD-SLUG`, pushed.

## Output

The branch name, how many rules were added, changed and retired, how many claims were dropped,
the check summary line, the log path, and a reminder that a person reviews and merges it.

## Safety

- A change to a rule behind a safety threshold (calorie floors, BP bands, red flags, screening,
  pregnancy, medications, the flags in `docs/safety.md`) goes first in the log under "Changed
  rules", marked "needs a code and safety review": `coach/` and `docs/safety.md` change only in a
  separate, reviewed commit, never in a research run.
- Open it or drop it: no claim, number or source from memory.
