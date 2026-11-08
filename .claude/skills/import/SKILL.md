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
- Plain words: the first time the client meets a term listed in `docs/glossary.md` (RIR, RPE,
  bpm or ppm, talk test, zones, deficit, TDEE and the others), explain it in one plain sentence
  from the glossary, in the client's language; `talk_test` and the protein-basis note come in
  the profile language already; say any other CLI note with its wording in `docs/glossary.md`
  "CLI notes" (same numbers), never quoting it in English. Rule names in brackets, wherever these steps ask for them, go in one
  short line at the end of the message, just before the deferral line when there is one
  (`Fuentes: [...]`, en: `Rules used: [...]`), not inline, unless the client asks for them inline.
  Still cite every rule you use.
- Load knowledge only with `coach knowledge section FILE "HEADING"`; cite the rule when you give
  advice the CLI does not print. Never read `knowledge/sources.md` whole.
- Give each reason from `coach safety` once per conversation, in plain words with the rule name
  in brackets in the closing rules line (one short line is enough for a reason unrelated to the
  task, such as heart-rate zones in /menu), then any CLI note that adds something new. Name the
  professional the reason names (prescriber, midwife or obstetrician, eating-disorder
  professional), else the GP. If `refer_gp` is set, end with the `deferral_line` that
  `coach safety` prints, copied exactly. Give its `instruction` first: it is the most urgent reason. Never give the
  `superseded` lines as advice.

## When to use

- The client has a Hevy CSV export (Hevy: Settings, Export data) or a CSV with the generic
  columns (`date`, `exercise`, optional `weight_kg`, `reps`, `rir`, `rpe`, `set_type`...; see
  `docs/adding-an-importer.md`).
- The client has a run log as CSV with the columns `date`, `distance_km` or `distance_miles`,
  `duration_minutes` or `duration_seconds`, and optionally `avg_hr`, `max_hr`, `rpe` (Borg
  6-20) and `notes`. It goes to `data/runs.csv`, not the workout log. Strava, Garmin and Apple
  Health exports are not read directly (their formats could not be verified): the client copies the columns
  above into a CSV. Runs logged as sets in Hevy stay in the workout log and are not counted by
  `coach runs week`.
- Re-importing a newer full export is fine: sets already stored are skipped. They are kept as
  first imported, so a set corrected or deleted in the app afterwards is not updated here.

## Reads

- The file path the client gives, used where it is. Never copy the file anywhere.

## Steps

1. Run `coach safety`.
2. `coach import PATH`. If the importer cannot be detected, ask which app it came from and use
   `coach import PATH --importer hevy_csv`, `--importer generic_csv` or
   `--importer generic_runs_csv`; if none fits, explain the generic columns and stop.
   When the output says `"store": "runs.csv"` it was a run log: report `read`, `added`,
   `duplicates`, `skipped_future`, `first_day`, `last_day` and `warnings`, then run
   `coach runs week --week-ending LAST_DAY` and quote its `km`, `runs`, `longest_km`, `spikes`
   and `notes`; skip steps 3 to 5.
3. When `duplicates` is above 0, say once that sets already stored keep their first-imported
   values (a correction made in the app since then is not picked up).
   When `conflicts` is above 0, some of those sets differ in load or reps from the stored ones
   (an edit in the app, or an export in other units): say so and that the stored values were
   kept. `skipped_future`: sets dated after today were not stored.
   Report `read`, `added`, `duplicates`, `skipped_empty`, `first_day` and `last_day`, and every
   line of `warnings` (a session already logged from another source would be counted twice;
   sets with no reps, weight, duration or distance are template leftovers and are not stored).
4. Skip this step when `added` is 0 (nothing new to count). Otherwise
   `coach strength sets --week-ending LAST_DAY` (LAST_DAY is `last_day` from step 2): weekly
   hard sets per muscle for the 7 days ending that day; say the dates (`week` in the output).
   Indirect work counts as half a set, so values like 4.5 are expected.
   The import output's `unmapped` lists names the muscle map does not know: their sets count
   toward no muscle. For each, propose the closest lift the map knows in plain words (what it
   trains, e.g. "a kind of row: back and biceps") and ask the client to confirm; never guess a
   muscle they have not confirmed. Store each confirmed one with
   `coach strength alias add "LOGGED NAME" "MAP LIFT"` (it refuses a lift the map does not know,
   and a name the map already gives another lift: then that lift is what the name counts as),
   then rerun `coach strength sets`. A name with no close lift stays unmapped: say so.
5. Run `coach injury list`. If `unmatched` lists names, show the logged names from this import's
   lifts and ask which one each listed lift is. Then run `coach injury add AREA --exercises "..."`
   again with that logged name. A Spanish or English name the map knows needs no change.

## Writes

- `data/sessions.csv` (workouts) or `data/runs.csv` (runs) through `coach import`. Nothing else.

## Output

A short summary in the profile language: what was imported, any warnings, and the week's sets
per muscle (muscle names translated) next to `reference_sets_per_week` from the CLI. Per
`coach knowledge section strength-hypertrophy "Weekly sets per muscle (dose-response)"`, that
number is a reference for muscle gain, not a minimum: with any goal other than muscle_gain,
say fewer sets suffice.

## Safety

- An `ImporterError` names the bad line: show it and stop; never edit the client's export.
- With `no_training`, import as usual but say training waits for a clinician's clearance.
- If `coach safety` shows `refer_gp`, end with the `deferral_line` that `coach safety`
  prints (the line in `docs/safety.md`), copied exactly.
