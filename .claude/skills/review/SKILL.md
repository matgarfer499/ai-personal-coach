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
- Plain words: the first time the client meets a term listed in `docs/glossary.md` (RIR, RPE,
  bpm or ppm, talk test, zones, deficit, TDEE and the others), explain it in one plain sentence
  from the glossary, in the client's language; translate CLI text such as `talk_test` rather
  than quoting it in English. Rule names in brackets, wherever these steps ask for them, go in one
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

- Weekly (or when the client asks how it is going). Use `/plan` to rewrite the plan itself.

## Reads

END is the last day of the week under review (default: today). When END is before today, run
`coach trend`, `coach strength progress` and `coach energy` with `--today END` (ground rules).
While `no_training` holds and the `coach energy` notes give the `pal_override` value, ask
whether the `active` level comes from the job or from exercise. Only when it was exercise that
has stopped, run `coach profile set pal_override VALUE` with that value. From the job, or a mix
of both: store nothing, and say the coach cannot model a mix yet (they may tell a clinician).
When the training hold has ended, run `coach profile set pal_override none`; the energy notes
say when a stored value is in use.
- `coach safety`, `coach profile show`, `coach knowledge stale`.
- `coach trend` (weight trend and, after 4 weeks, `recalibrated_tdee`).
- `coach strength sets --week-ending END` and `coach strength progress`, adding
  `--rep-range "*=LOW-HIGH"` from the `rep_range:` line of `data/plan.md` (none when missing) and
  one `--rep-range "LIFT=LOW-HIGH"` per lift whose `LIFT: LOW-HIGH reps` line differs. The
  output is `lifts` plus `unmatched_rep_ranges`: names that match no logged lift were not
  applied: a name the client says is new (never logged) is simply left; ask which logged lift it
  is only when they say they logged it under another name, then rerun with that name. Names in
  `rep_ranges_outside_lookback` match only a lift logged before the lookback window: just note
  that their range was not applied.
  `rep_range_notes`: the log sits outside 8-12 with no range given; ask the client's range and
  rerun before quoting a load.
- `data/checkins.csv` rows of the week (sleep, notes), and `data/plan.md` if it exists.
- Runners (`sport` running or both in `coach profile show`): `coach runs week --week-ending END`
  and `coach injury list`.

Knowledge, by situation: run only the lines that apply.
- Always:
  - `coach knowledge section nutrition "Recalibrate TDEE from the weight trend"`
  - `coach knowledge section nutrition "Read the scale with weekly averages"`
  - `coach knowledge section strength-hypertrophy "When progress stalls"`
  - `coach knowledge section recovery-habits "Simple readiness monitoring"`
- Goal fat_loss: `coach knowledge section nutrition "Rate of loss for lean, trained clients"`
- Goal muscle_gain: `coach knowledge section nutrition "Surplus size for muscle gain"`
- Any recovery sign from step 1: `coach knowledge section strength-hypertrophy "Deloads"`
- Runners:
  - `coach knowledge section cardio-health "Running load progression: cap single-run spikes, not just weekly totals"`
  - Pain or an injury: `coach knowledge section recovery-habits "Common running injuries and who is most at risk"`
  - Tendon pain: `coach knowledge section recovery-habits "Pain-monitoring traffic light for tendon problems"`

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
   if the rule's population does not fit the client, say so, and relay every trend `notes`
   line (the fast-loss note). With `insufficient_data`, say
   what is missing; draw no conclusion. With `disabled`, say nothing about weight.
4. Calories: if `recalibrated_tdee` is a number, record it (step 9). Propose a calorie change
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
6. Running (runners only): quote from `coach runs week` the week's `km`, `runs` and
   `longest_km` next to `previous_week` and `change_pct` (the weekly trend), every run in
   `spikes` with its `longest_previous_km` and `cap_km` ("Running load progression": a single run
   more than about 10% longer than the longest of the previous 30 days raised injury rates; the
   10% weekly rule is only a convention), and `long_run_cap_km` for the next long run (with `paused`, quote the injury's reason; null when nobody has assessed it). The
   intensity mix is `zone_minutes` (minutes per zone, from each run's average HR); relay every
   `notes` line, including minutes in zones a cap holds back and a higher logged peak to store
   as `hr_max`. With `zone_minutes` null, say why from its notes. Pain or an injury: ask about
   knee, shin, Achilles, heel and ankle pain; record it with `coach injury add AREA --since
   DATE` (with `--professional WHO` once assessed), refer an unassessed one to a GP or
   physiotherapist before that running is loaded, use the tendon traffic light for an assessed
   tendon problem, and stop and refer for sharp or worsening pain. The coach has no other
   running volume cut (the research found none). A goal race within 3 weeks: suggest
   `/plan`, which runs `coach runs taper`. There is no generic runner deload week (none found
   in the research); step 7 is for lifting.
7. Recovery: pass the signs from step 1, comma-separated, to
   `coach strength deload --signs SIGNS` (`performance_stall`, `joint_aches`, `poor_sleep`,
   `low_motivation`, `drop_despite_rest`, `low_mood`) and quote the result, with `volume_cut`
   read as in the Deloads rule. With no sign, skip the call and say no deload is indicated.
   During a deload week, add no sets; any "add sets" advice from a stall waits until after it.
   An ache that persists after the deload week goes to a GP or physiotherapist.
8. Propose the changes (calories from step 4, a deload from step 7) and ask whether they agree.
9. Write `data/reviews/END.md` (create the folder if needed): `tdee_kcal: VALUE` when the trend
   gave one; when the client agreed to the calorie change from step 4, also `target_kcal: KCAL`
   and `in_deficit: true|false` from that `coach energy` output (`deficit` above 0), which
   `/plan` reads. These `name: value` lines keep the CLI's format (decimal point), whatever the
   client's language. Then the findings as in Output, then the agreed changes, or the proposals
   marked pending when the client has not decided.

## Writes

- `data/reviews/END.md`. Changes to the plan itself go through `/plan`.

## Output

In the profile language: any safety reason first (one line each), then three to six bullets
(adherence, weight, calories, training, running for runners, recovery, next step) with every number quoted from the
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
- If `coach safety` shows `refer_gp`, end with the `deferral_line` that `coach safety`
  prints (the line in `docs/safety.md`), copied exactly.
