---
name: checkin
description: Use when the client reports their day (weight, waist, food, sleep, how training felt, symptoms, illness or pain), or types /checkin.
argument-hint: "[free text about today]"
---

# /checkin

Records one day in `data/checkins.csv` and watches for red flags. Short and frequent.

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

- The client gives any daily data or says how they feel; most days, ideally.
- Not for workout logs (that is `/import`) or a weekly look back (that is `/review`).

## Reads

- `coach safety` first, every time.
- What the client says; ask only for what is missing and relevant today.
- `data/checkins.csv` notes of the 7 calendar days up to today (were the weekly questions asked?).

## Steps

1. Run `coach safety`. If `no_weight_targets` is set, do not ask for or mention weight, waist or
   calories (the CLI refuses them): ask only about sleep, how they feel and symptoms.
2. Collect, in one short message if possible: weight (this morning, after the toilet, before
   eating, per `coach knowledge section nutrition "Read the scale with weekly averages"`), waist
   (once a week is enough), logged kcal for yesterday if they track, hours slept last night,
   anything notable. Missed days are not filled in afterwards.
3. Red flags, every check-in. When an answer to one of these is "not sure", describe the sign
   once more in plain words; if still unsure, treat it as absent and tell them to act as below
   if it appears.
   - Chest, neck, jaw or arm pain or pressure, breathlessness at rest, dizziness or fainting,
     palpitations, during exercise or at rest:
     `coach profile set screening.cardiac_symptoms true`, tell them to stop training and see a
     doctor (the `emergency_number` from `coach safety`, now, for chest pain at rest, fainting,
     or chest pain with breathlessness and sweating; with none stored, the local emergency
     number, 112 in Europe). `coach knowledge section recovery-habits "Cardiac warning symptoms: stop and refer"`.
   - Fever, aches all over, or feeling unwell below the neck: no training until better
     (`coach knowledge section recovery-habits "Fever and systemic illness: do not train"`).
     A head cold only: light training is optional (`coach knowledge section recovery-habits
     "Head cold: optional light training"`), except with `no_training`, when you suggest no
     training at all.
   - Signs of disordered eating (purging, laxatives or diet pills, exercising to make up for
     food, bingeing with loss of control, marked fear of weight gain): `coach profile set
     screening.scoff_positive true` and suggest a GP or eating-disorder service, per
     `coach knowledge section recovery-habits "Warning signs that warrant referral"`. Fainting,
     confusion, eating almost nothing for 2+ days or vomiting several times a day: same-day
     urgent care (`coach knowledge section recovery-habits "Urgent medical red flags"`).
   - Very sore, weak, swollen muscles with dark urine after training: urgent care now
     (`coach knowledge section recovery-habits "Recognise it and send to urgent care"`).
   - New pain or an injury in an area: run `coach injury list`; record a new one with
     `coach injury add AREA --since DATE` (add `--professional WHO` once someone has assessed
     it, and `--exercises "LIFT, LIFT"` for the logged lifts it affects). With no professional,
     suggest a GP or physiotherapist before loading it, per `coach knowledge section
     recovery-habits "Some pain during exercise is acceptable in chronic, assessed pain"`;
     sharp or worsening pain, or numbness or weakness, means stop and see a doctor. When the
     client says the professional has cleared it: `coach injury clear AREA`. An injury nobody
     assessed is cleared only when the client says the pain is gone and they train the lifts
     it paused without pain; otherwise suggest the assessment again.
   - The client wants HIIT, sprints, jump rope, jumps or a max test while `coach safety` shows
     `review_before_vigorous` or `no_all_out_sprints`: give its reason and suggest the review
     (`coach knowledge section recovery-habits "PAR-Q+ specific thresholds"`).
4. Weekly questions, asked only when no note of the last 7 days records them:
   - Women not pregnant: any new missed, late or irregular period? Load
     `coach knowledge section nutrition "Menstrual dysfunction: stop and refer"`. New changes
     in a cycle that was regular: `coach profile set screening.menstrual irregular_new`;
     no period for 3 months or more: `absent`; both go to the GP. Ask once whether they use
     hormonal contraception, which masks the cycle. Note it in plain words, as
     `regla: normal` or `regla: retrasos nuevos` (en: `period: ...`).
   - With `hypertension`: their latest seated reading after 5 min rest, stored with
     `coach profile set screening.bp_systolic N` and `screening.bp_diastolic N`. Note it as
     `TA S/D` (en: `BP S/D`).
5. Record: `coach checkin add --weight KG --waist CM --intake KCAL --sleep H --notes "..."`,
   leaving out what they did not give. One row per day: weight is this morning's, intake is
   yesterday's, sleep is last night's (convention). A second check-in the same day only fills in
   or replaces the fields it gives. Notes, separated by `; `: symptoms, how training went, and
   the weekly-question notes from step 4. For another day, add `--date YYYY-MM-DD`. The CLI refuses weight, waist and calories when weigh-ins are off; then record the rest.
6. If they gave a weight, run `coach trend` and report only its `status`, and with status `ok`
   its `rate_kg_week`. With `insufficient_data`, say how many more weigh-ins it needs (from its
   note) and nothing about the direction.

## Writes

- `data/checkins.csv` through `coach checkin add`; screening updates through `coach profile set`.

## Output

In the profile language, in this order:
1. Any red flag from step 3 or a newly set safety reason, with who to see.
2. Two to four lines: what was recorded, the trend line if any, and one practical note only if
   something they said calls for it (cite the rule). Never comment on a single weigh-in.
3. The deferral line when `refer_gp` is set.

## Safety

- Rerun `coach safety` after any screening update; if `refer_gp` is now set, say why (its new
  reason) and end with the deferral line from `docs/safety.md`, copied exactly.
- Never suggest training when `no_training` is set or a red flag from step 3 fired.
