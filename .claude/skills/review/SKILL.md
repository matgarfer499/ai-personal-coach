---
name: review
description: Use when the client wants a weekly or periodic look back at progress (weight trend, training, adherence), asks whether to change calories or training, or types /review.
argument-hint: "[week ending YYYY-MM-DD]"
---

# /review

A weekly review: what the data says, and whether the plan should change.

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

- Weekly (or when the client asks how it is going). Use `/plan` to rewrite the plan itself.

## Reads

END is the last day of the week under review (default: today). When END is before today, run
`coach trend`, `coach strength progress` and `coach energy` with `--today END` (ground rules).
- `coach safety`, `coach profile show`, `coach knowledge stale`.
- `coach trend` (weight trend and, after 4 weeks, `recalibrated_tdee`).
- `coach strength sets --week-ending END` and `coach strength progress`, adding
  `--rep-range "LIFT=LOW-HIGH"` for each lift whose range in `data/plan.md` is not 8-12.
- `data/checkins.csv` rows of the week (sleep, notes), and `data/plan.md` if it exists.

Knowledge, by situation: run only the lines that apply.
- Always:
  - `coach knowledge section nutrition "Recalibrate TDEE from the weight trend"`
  - `coach knowledge section nutrition "Read the scale with weekly averages"`
  - `coach knowledge section strength-hypertrophy "When progress stalls"`
  - `coach knowledge section recovery-habits "Simple readiness monitoring"`
- Goal fat_loss: `coach knowledge section nutrition "Rate of loss for lean, trained clients"`
- Goal muscle_gain: `coach knowledge section nutrition "Surplus size for muscle gain"`
- Any recovery sign from step 1: `coach knowledge section strength-hypertrophy "Deloads"`

## Steps

1. Ask, in one message: how many planned sessions they did, how closely they ate to the target,
   and which of these held for 1-2 weeks: performance stall, joint aches, poor sleep, low
   motivation, performance falling even after rest days, low mood. A lift that
   `coach strength progress` reports as `stalled` counts as a performance stall too. When what
   they say differs
   from the check-ins (for example sleep), use both and mention the difference.
2. If `coach knowledge stale` lists files, add one reminder line suggesting `/research stale`.
3. Weight: report `status`. With `ok`, quote `rate_kg_week` and `rate_pct_week` (a loss prints
   negative) and say whether its size falls inside the rate the loaded rule gives for the goal;
   if the rule's population does not fit the client, say so. With `insufficient_data`, say
   what is missing; draw no conclusion. With `disabled`, say nothing about weight.
4. Calories: if `recalibrated_tdee` is a number, record it (step 8). Propose a calorie change
   only when the rate from step 3 is outside the goal's range (for `maintenance` and
   `recomposition` no rule gives a range, so propose none and say so); then run
   `coach energy --tdee VALUE --current-kcal CURRENT`, with VALUE as printed and CURRENT the
   `target_kcal:` line of `data/plan.md` (no plan: ask what they eat now). The CLI moves a cut one
   step at a time; quote its `kcal` and any note that adds something new.
5. Training: weekly sets per muscle next to `reference_sets_per_week` (a reference for muscle
   gain, not a minimum; with any goal other than muscle_gain fewer
   sets suffice), and each lift's `action` from
   `coach strength progress` with its reason in plain words. When planned sessions were missed,
   say the next session is the next one in the plan's rotation: no doubling up or catching up
   (the `/plan` convention; one missed session does not undo progress).
6. Recovery: pass the signs from step 1, comma-separated, to
   `coach strength deload --signs SIGNS` (`performance_stall`, `joint_aches`, `poor_sleep`,
   `low_motivation`, `drop_despite_rest`, `low_mood`) and quote the result, with `volume_cut`
   read as in the Deloads rule. With no sign, skip the call and say no deload is indicated.
   During a deload week, add no sets; any "add sets" advice from a stall waits until after it.
   An ache that persists after the deload week goes to a GP or physiotherapist.
7. Propose the changes (calories from step 4, a deload from step 6) and ask whether they agree.
8. Write `data/reviews/END.md` (create the folder if needed): `tdee_kcal: VALUE` when the trend
   gave one; when the client agreed to the calorie change from step 4, also `target_kcal: KCAL`
   and `in_deficit: true|false` from that `coach energy` output (`deficit` above 0), which
   `/plan` reads. These `name: value` lines keep the CLI's format (decimal point), whatever the
   client's language. Then the findings as in Output, then the agreed changes, or the proposals
   marked pending when the client has not decided.

## Writes

- `data/reviews/END.md`. Changes to the plan itself go through `/plan`.

## Output

In the profile language: any safety reason first (one line each), then three to six bullets
(adherence, weight, calories, training, recovery, next step) with every number quoted from the
CLI, then whether to rerun `/plan`: yes when the client agreed to a calorie or deload change.

## Safety

- Never judge progress on one weigh-in, and never mention weight when the trend is `disabled`.
- With `no_training`, give no training, load or deload advice: say training waits for a
  clinician's clearance. With `hold_progression`, loads stay as `coach strength progress` says.
- A lift `paused` by an injury is neither a stall nor a reason to add sets: quote its reason.
  Ask whether the professional has cleared the injury; if so, `coach injury clear AREA`. An
  injury nobody assessed is cleared only when the pain is gone and the paused lifts are
  pain-free.
- With `review_before_vigorous` or `no_all_out_sprints`, propose no vigorous work, intervals or
  sprints; give the reason and suggest the review if the client asks for them.
- If `coach safety` shows `refer_gp`, end with the deferral line from `docs/safety.md`, copied
  exactly.
