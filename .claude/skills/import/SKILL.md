---
name: import
description: Use when the client wants to add workouts from an app export or a CSV file (Hevy export, spreadsheet, generic CSV), or types /import.
argument-hint: "PATH to the export file"
---

# /import

Adds an exported workout log to `data/sessions.csv` without duplicates.

## Ground rules (same in every coach skill)

- `coach X` means `uv run python -m coach X --json`, run from the repo root. The CLI uses
  `$COACH_DATA_DIR` if set, else `data/`, so never pass `--data-dir` unless the person running you
  names another directory for the session (then add `--data-dir DIR` before every X). DATA is the
  `data_dir` that `coach profile show` prints (run it first): every `data/` path below lives in
  DATA. For a past date D, add `--today D` before X. (Knowledge sections print plain text either
  way.)
- Quote every number exactly as the CLI prints it. Never compute, round differently, adjust or
  estimate kcal, grams, loads or zones yourself. If a figure is missing, ask or run the CLI.
  Translate labels (muscle names, field names) into the client's language, and write the
  decimal separator it uses (64,59 in Spanish); never change the digits.
- Exit code 2 with `profile_incomplete` names a field: ask the client for it, set it with
  `coach profile set`, rerun.
- Speak to the client in the profile's `language` (es or en, from `coach profile show`); before
  it is set, in the language the client writes in. Keep it short and plain.
- Load knowledge only with `coach knowledge section FILE "HEADING"`; cite the rule when you give
  advice the CLI does not print. Never read `knowledge/sources.md` whole.
- Give each reason from `coach safety` once per conversation, in plain words with the rule name
  in brackets (one short line is enough for a reason unrelated to the task, such as heart-rate
  zones in /menu), then any CLI note that adds something new. Name the professional the reason
  names (prescriber, midwife or obstetrician, eating-disorder professional), else the GP. If
  `refer_gp` is set, end with the deferral line from `docs/safety.md`, copied exactly, in the
  profile language.

## When to use

- The client has a Hevy CSV export (Hevy: Settings, Export data) or a CSV with the generic
  columns (`date`, `exercise`, optional `weight_kg`, `reps`, `rir`, `rpe`, `set_type`...; see
  `docs/adding-an-importer.md`).
- Re-importing a newer full export is fine: sets already stored are skipped. They are kept as
  first imported, so a set corrected or deleted in the app afterwards is not updated here.

## Reads

- The file path the client gives, used where it is. Never copy the file anywhere.

## Steps

1. Run `coach safety`.
2. `coach import PATH`. If the importer cannot be detected, ask which app it came from and use
   `coach import PATH --importer hevy_csv` or `--importer generic_csv`; if neither fits, explain
   the generic columns and stop.
3. When `duplicates` is above 0, say once that sets already stored keep their first-imported
   values (a correction made in the app since then is not picked up).
   Report `read`, `added`, `duplicates`, `skipped_empty`, `first_day` and `last_day`, and every
   line of `warnings` (a session already logged from another source would be counted twice;
   sets with no reps, weight, duration or distance are template leftovers and are not stored).
4. Skip this step when `added` is 0 (nothing new to count). Otherwise
   `coach strength sets --week-ending LAST_DAY` (LAST_DAY is `last_day` from step 2): weekly
   hard sets per muscle for the 7 days ending that day; say the dates (`week` in the output).
   Indirect work counts as half a set, so values like 4.5 are expected. List `unmapped` exercises and say they do not count toward
   weekly sets until someone adds them to `coach/muscle_map.yaml`.

## Writes

- `data/sessions.csv` through `coach import`. Nothing else.

## Output

A short summary in the profile language: what was imported, any warnings, and the week's sets
per muscle (muscle names translated) next to `reference_sets_per_week` from the CLI. Per
`coach knowledge section strength-hypertrophy "Weekly sets per muscle (dose-response)"`, that
number is a reference for muscle gain, not a minimum: with any goal other than muscle_gain,
say fewer sets suffice.

## Safety

- An `ImporterError` names the bad line: show it and stop; never edit the client's export.
- With `no_training`, import as usual but say training waits for a clinician's clearance.
- If `coach safety` shows `refer_gp`, end with the deferral line from `docs/safety.md`, copied
  exactly.
