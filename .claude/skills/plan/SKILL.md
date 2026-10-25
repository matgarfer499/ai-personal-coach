---
name: plan
description: Use when the client asks for a training and nutrition plan, a new block, or changes after a review, or types /plan.
argument-hint: "[what to change]"
---

# /plan

Writes the client's current plan to `data/plan.md`: a training week and daily nutrition targets.

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

- After `/setup`, when a block ends, or when `/review` recommends a change.
- Not when `coach safety` shows `no_training`: say a doctor must review first and stop.

## Reads

Run these, all with the ground-rule flags:
- `coach safety`, `coach profile show`, `coach knowledge stale`.
- The calorie target, from the first of these that applies:
  1. The newest file in `data/reviews/` is newer than `data/plan.md` and has `target_kcal:` and
     `in_deficit:` lines (a change the client agreed at `/review`): use those.
  2. `data/plan.md` exists, the goal is the same and `coach safety` sets no new flag: use its
     `target_kcal:` and `in_deficit:` lines.
  3. Otherwise run `coach energy` (with `hold_deficit`, ask what they eat now and add
     `--current-kcal KCAL`); `target_kcal` is its `kcal`, `in_deficit` is whether `deficit` is
     above 0.
  Then `coach macros --kcal TARGET` (add `--in-deficit` when `in_deficit` is true): the CLI
  raises a stored target that the current flags no longer allow.
- `coach zones`.
- A plan or routine the client already follows (a PDF, a note, a pasted list): ask whether they
  have one, unless `data/plan.md` exists. Read it where it is (never copy it) and build from it:
  keep the lifts, days and order that work, and change only what a rule or a safety flag
  requires, saying what changed and why.
- Agreed changes: when the newest file in `data/reviews/` is newer than `data/plan.md` and
  records an agreed deload, the training week is that deload week (the review's quoted
  `volume_cut`, `stop_rir` and `extra_rest_days` applied to the last logged week). Ignore
  anything the review marks pending.
- If `data/sessions.csv` exists: `coach strength sets` (the last logged week by default) and
  `coach strength progress`, adding `--rep-range "LIFT=LOW-HIGH"` for each lift whose range in
  `data/plan.md` is not 8-12 (the default; the flag is ignored for a lift with no logged sets).

Knowledge, by situation: run only the lines that apply.
- Always:
  - `coach knowledge section strength-hypertrophy "Weekly sets per muscle (dose-response)"`
  - `coach knowledge section strength-hypertrophy "Frequency for hypertrophy"`
  - `coach knowledge section strength-hypertrophy "Full-body versus split"`
  - `coach knowledge section strength-hypertrophy "Target reps in reserve"`
  - `coach knowledge section strength-hypertrophy "Double progression"`
  - `coach knowledge section strength-hypertrophy "Load range for hypertrophy"`
  - `coach knowledge section strength-hypertrophy "Load range for maximal strength"`
  - `coach knowledge section cardio-health "Weekly baseline dose"`
- Novice: `coach knowledge section strength-hypertrophy "Starting point for novices"`
- Advanced: `coach knowledge section strength-hypertrophy "Trained lifters: 12-20 weekly sets"`
- Age 65+:
  - `coach knowledge section strength-hypertrophy "Core prescription for adults 65+"`
  - `coach knowledge section strength-hypertrophy "Weekly template for older adults"`
- Hypertension or a BP flag:
  - `coach knowledge section recovery-habits "Resting BP thresholds to defer or refer"`
  - `coach knowledge section strength-hypertrophy "Effort limits for older adults and cardiovascular risk"`
- Beta-blocker: `coach knowledge section cardio-health "RPE as the anchor under beta-blockade"`
- PAR-Q+ follow-up YES: `coach knowledge section recovery-habits "PAR-Q+ 2023 as the default entry screen"`
- `review_before_vigorous` or `no_all_out_sprints`: `coach knowledge section recovery-habits "PAR-Q+ specific thresholds"`
- An injury in `coach injury list`, or pain the client mentions:
  - `coach knowledge section recovery-habits "Some pain during exercise is acceptable in chronic, assessed pain"`
  - `coach knowledge section recovery-habits "Acute sprains and strains: protect briefly, then load"`
  - `coach knowledge section recovery-habits "Muscle strain: early pain-guided loading"`
- The client missed sessions of the last plan, or is back from a break:
  - `coach knowledge section recovery-habits "How long habits take"`
  - `coach knowledge section strength-hypertrophy "Short breaks cost little"`
- Any cardio modality you are about to prescribe: its rule from `knowledge/index.md` (search
  the modality's name), e.g. `coach knowledge section cardio-health "Jump rope as conditioning"`
  or `coach knowledge section strength-hypertrophy "HIIT and sprint intervals with lifting"`.
- Pregnant:
  - `coach knowledge section recovery-habits "Default is to be active"`
  - `coach knowledge section recovery-habits "Warning signs to stop exercise"`
- GLP-1: `coach knowledge section nutrition "GLP-1 users: protein, training and red flags"`
- Goal fat_loss:
  - `coach knowledge section nutrition "Deficit size when keeping or building muscle"`
  - `coach knowledge section nutrition "Resistance training during any diet, especially for older adults"`
- Goal muscle_gain: `coach knowledge section nutrition "Surplus size for muscle gain"`
- Goal recomposition: `coach knowledge section nutrition "Body recomposition"`

## Steps

1. If `coach knowledge stale` lists files, plan normally and add one reminder line suggesting
   `/research stale`.
2. Ask what is missing (not what their routine or earlier answers already show): days and time
   available, equipment, exercises they like or dislike, and any injury or pain. When the client
   delegates a choice ("you decide": days, split, exercises, which days for cardio), propose it
   directly from their availability and the rules above, say it can be changed, and do not ask
   again. Injuries and pain are never delegated: always ask. Record each injury with
   `coach injury add AREA --since DATE
   --professional WHO --exercises "LIFT, LIFT"` (who assessed it and manages it; the logged
   names of the lifts it affects), so `coach strength progress` pauses those lifts; if it
   prints `unmatched` names, ask the client which logged lift each one is and add it again with
   that name. With no professional yet, a GP or physiotherapist assesses it before it is loaded. Plan around an
   active injury: swap or reduce the lifts that provoke it, keep the rest of the body training
   (per "Acute sprains and strains: protect briefly, then load"), and follow any limits the
   professional set.
   Training week: sessions per week from the client's availability (at least 2 full-body
   sessions, per "Weekly baseline dose": each with a leg, a push and a pull exercise); exercises the client has access to and likes. Use the
   client's logged names when they exist so `/review` can count them.
   - Rotation and missed sessions: when the week has different sessions (A, B), write their
     order as a rotation (for example A, B, A, B). When the client did not do every planned
     session, ask which session they did last (or read the last `session_title` in
     `data/sessions.csv`) and continue the rotation from the next one: never double up or add
     sessions to catch up, and an incomplete week is not a failure ("How long habits take": one
     missed session does not undo progress, get back on track at the next opportunity). Convention
     (listed in `docs/conventions.md`): no rule gives the order, so it continues where they left
     off. Loads come from `coach strength progress`, which restarts lower after a break ("Short
     breaks cost little").
   - Volume: keep each muscle near its weekly sets in `coach strength sets`. With goal
     muscle_gain and recovery holding, add sets gradually toward `reference_sets_per_week`.
     With no log, 2-3 working sets per exercise (convention).
   - Rep range per lift: 8-12 by default ("Double progression", "Starting point for novices");
     main lifts of a client who wants strength move to heavier work in 3-8 reps once technique is
     solid, within Safety below ("Load range for maximal strength"); a hypertrophy client may
     use anything from about 6 to 30 reps ("Load range for hypertrophy"). Keep the range the
     client already uses, from `data/plan.md` or their log, unless they ask for a change. Write
     each lift as `LIFT: LOW-HIGH reps` in the training week, with the logged name, so `/review`
     can pass it to `coach strength progress --rep-range`; after changing a lift's range, rerun
     that command for it before quoting a load.
   - Reps and effort: from the rules loaded above; with `hold_progression`, no harder than the
     last logged sessions. When two rules give different RIR, the more
     conservative one wins (more reps in reserve). The RPE caps from `coach zones` are for cardio;
     lifting effort is set by RIR.
   - Loads: from `coach strength progress` per lift (quote `load_kg` and `action`, and say why
     in plain words from its reason, citing the rule it names; `hold` means the same load and reps until a clinician
     reviews); for new lifts, "a weight you could lift 2-3 more times",
     never a number you invent.
3. Cardio: before prescribing a modality, load its rule (Reads) and use the intensity class the
   rule gives it, not a guess: jump rope, HIIT, sprints and plyometric jumps are vigorous work,
   never "moderate cardio". Start at the minimum of "Weekly baseline dose" (or what they already do, if more),
   split evenly over the days they offered (ask which, when it is unclear and the client has not delegated it; with only one
   day, add short walks on days they choose); intensity only as the zones `coach zones` printed (RPE and
   talk test, and bpm only if it printed them).
4. Nutrition: the calorie target, protein, fat, carbohydrate and fibre exactly as `coach macros`
   printed them.
5. Write `data/plan.md` in the profile language. Its first three lines, with nothing before
   them: `Fecha: YYYY-MM-DD` (en: `Date:`), `target_kcal: KCAL` and `in_deficit: true|false`
   (`kcal` and `in_deficit` as `coach macros` printed them; `/menu` reads these lines, so
   they keep the CLI's decimal point). When the client has given their training days, a fourth
   line follows: `training_schedule: mon 18:30; wed 18:30; sat` (English day tokens mon tue wed
   thu fri sat sun in any profile language, an optional 24 h start time after each; leave the
   line out when the days are not known; `/menu` places pre- and post-workout meals with it).
   Then the sections Semana de entrenamiento, Cardio, Nutrición, Notas de seguridad, Fuentes (en:
   Training week, Cardio, Nutrition, Safety notes, Rules used). Rule names stay as the knowledge
   headings, in brackets. Then a line on when to run `/review`, and the deferral line last
   when `refer_gp` is set.

## Writes

- `data/plan.md` (replace the previous plan; keep the date at the top).

## Output

The plan in the profile language, as written to `data/plan.md`, then one line on when to review
(`/review` weekly).

## Safety

- `hold_progression`: no added load, reps, sets or intensity, even if the client asks; say
  a clinician's review comes first.
- `cap_moderate` or `review_before_vigorous`: no vigorous or maximal work (HIIT, 1RM tests,
  all-out sprints, jump rope, plyometric jumps, near-maximal lifts). With
  `review_before_vigorous`, say a qualified exercise professional or clinician reviews it first
  if the client wants it; record that review with `coach profile set
  screening.vigorous_reviewed true` only when the client says it happened.
  `no_all_out_sprints`: no SIT or REHIT at all. Even without it, SIT or REHIT only for a client
  with every PAR-Q+ answer NO and 4+ weeks of regular moderate cardio without symptoms, never
  for a sedentary beginner ("PAR-Q+ specific thresholds").
- `paused` in `coach strength progress`: the lift does not progress. With no `load_kg`, it is not
  loaded until a GP or physiotherapist has assessed the injury; otherwise `load_kg` is a ceiling:
  reduce or swap the lift within the professional's limits. Clear it with `coach injury clear
  AREA` only when the professional has cleared it.
- `use_rpe_not_hr`: no heart-rate numbers. `prescriber_owns_weight` or `no_deficit`: no deficit language; the CLI targets already
  reflect it.
- If `coach safety` shows `refer_gp`, say what the professional should review first and end
  with the deferral line from `docs/safety.md`, copied exactly.
