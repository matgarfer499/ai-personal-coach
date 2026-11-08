---
name: plan
description: Use when the client asks for a training and nutrition plan, a new block, or changes after a review, or types /plan.
argument-hint: "[what to change]"
---

# /plan

Writes the client's current plan to `data/plan.md`: a training week and daily nutrition targets.
The profile's `sport` decides the week: `lifting` (or unset) a lifting week, `running` a
running week, `both` the two together.

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
  "CLI notes" (same numbers), never quoting it in English. Rule names in brackets, wherever
  these steps ask for them, go in one short line at the end of the message, just before the deferral line when there is one
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

- After `/setup`, when a block ends, or when `/review` recommends a change.
- Not when `coach safety` shows `no_training`: say a doctor must review first and stop. With
  `clearance_before_exercise` (ACSM: inactive with a known disease) the stop covers training
  only: quote its `instruction`, give no exercise, and nutrition targets still follow
  `coach macros`.

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
     above 0. When its `notes` hold the `active` `no_training` note, ask whether the activity comes
     from the job or from exercise. Only when it was exercise that has stopped, run
     `coach profile set pal_override VALUE` with the value the note gives (never one you chose or
     computed) and rerun `coach energy`; the choice applies to every path while `no_training`
     holds. From the job, or a mix of both: store nothing, and say the coach cannot model a mix
     yet (they may tell a clinician). Tell them to keep training on hold until a clinician
     clears it; when the hold ends, run `coach profile set pal_override none`.
  Then `coach macros --kcal TARGET` (add `--in-deficit` when `in_deficit` is true): the CLI
  raises a stored target that the current flags no longer allow.
- `coach zones`.
- Runners (`sport` running or both): `coach runs week` (the last logged week by default) and
  `coach injury list`. Ask whether a goal race is coming; with a race date D, run
  `coach runs taper --race-date D`.
- A plan or routine the client already follows (a PDF, a note, a pasted list): ask whether they
  have one, unless `data/plan.md` exists. Read it where it is (never copy it) and build from it:
  keep the lifts, days and order that work, and change only what a rule or a safety flag
  requires, saying what changed and why.
- Agreed changes: when the newest file in `data/reviews/` is newer than `data/plan.md` and
  records an agreed deload, the training week is that deload week (the review's quoted
  `volume_cut`, `stop_rir` and `extra_rest_days` applied to the last logged week). Ignore
  anything the review marks pending.
- If `data/sessions.csv` exists: `coach strength sets` (the last logged week by default) and
  `coach strength progress`, adding `--rep-range "*=LOW-HIGH"` from the `rep_range:` line of
  `data/plan.md` (the client's usual range; leave it out when the line is missing, 8-12 applies)
  and one `--rep-range "LIFT=LOW-HIGH"` per lift whose `LIFT: LOW-HIGH reps` line differs (the
  flag is ignored for a lift with no logged sets). The output is `lifts` plus
  `unmatched_rep_ranges`: names given with `--rep-range` that match no logged lift (so they were
  not applied). A name the client says is new (never logged) is simply left. Ask which logged
  lift it is only when the client says they logged it under another name, then rerun with that
  name. `rep_ranges_outside_lookback` lists names that match a lift logged only before the
  lookback window (absent from `lifts`): ask whether that lift is back in the plan.
  `rep_range_notes` names lifts whose logged reps sit outside the default 8-12 while no range
  was given: ask the client's usual range for each, then rerun with `--rep-range`. Never judge a
  heavy lift against 8-12 because the range was not asked.

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
- An ACSM cell in `reasons` (`clearance_before_exercise`, or clearance before vigorous work):
  `coach knowledge section recovery-habits "ACSM 2015 screening algorithm"`
- PAR-Q+ follow-up YES: `coach knowledge section recovery-habits "PAR-Q+ 2023 as an optional extra screen"`
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
  - Heavy bag, boxing: `coach knowledge section cardio-health "Heavy-bag boxing as conditioning"`
  - Functional training, CrossFit-style circuits: `coach knowledge section cardio-health "Functional training circuits"`
- Pregnant:
  - `coach knowledge section recovery-habits "Default is to be active"`
  - `coach knowledge section recovery-habits "Warning signs to stop exercise"`
- GLP-1: `coach knowledge section nutrition "GLP-1 users: protein, training and red flags"`
- Goal fat_loss:
  - `coach knowledge section nutrition "Deficit size when keeping or building muscle"`
  - `coach knowledge section nutrition "Resistance training during any diet, especially for older adults"`
- Goal muscle_gain: `coach knowledge section nutrition "Surplus size for muscle gain"`
- Goal recomposition: `coach knowledge section nutrition "Body recomposition"`
- Runners (`sport` running or both):
  - `coach knowledge section cardio-health "Running load progression: cap single-run spikes, not just weekly totals"`
  - `coach knowledge section cardio-health "ACSM intensity bands"`
  - `coach knowledge section recovery-habits "Common running injuries and who is most at risk"`
  - A goal race: `coach knowledge section cardio-health "Taper before a goal race"`
  - Tendon pain: `coach knowledge section recovery-habits "Pain-monitoring traffic light for tendon problems"`

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
     Before writing the plan, write the training week as YAML (`sessions:`, each with `name`
     and `exercises:` of `{exercise: NAME, sets: N}`, one entry per session in the week) to
     `data/plan-week.yaml` and run `coach strength plan-sets plan-week.yaml`: say which muscles
     fall in `below_reference` and either add sets or say why not ("Weekly sets per muscle");
     handle `unmapped` names as /import does: propose the closest known lift, and after the
     client confirms store it with `coach strength alias add "NAME" "MAP LIFT"`; or use a
     name the map knows in the plan.
   - Rep range per lift: 8-12 by default ("Double progression", "Starting point for novices");
     main lifts of a client who wants strength move to heavier work in 3-8 reps once technique is
     solid, within Safety below ("Load range for maximal strength"); a hypertrophy client may
     use anything from about 6 to 30 reps ("Load range for hypertrophy"). Keep the range the
     client already uses, from `data/plan.md` or their log, unless they ask for a change. Write
     the client's usual range once as the `rep_range:` header line (step 6) and each lift with
     another range as `LIFT: LOW-HIGH reps` in the training week, with the logged name, so
     `/review` can pass them to `coach strength progress --rep-range`; after changing a lift's range, rerun
     that command for it before quoting a load.
   - Reps and effort: from the rules loaded above; with `hold_progression`, no harder than the
     last logged sessions. When two rules give different RIR, the more
     conservative one wins (more reps in reserve). The RPE caps from `coach zones` are for cardio;
     lifting effort is set by RIR.
   - Loads: from `coach strength progress` per lift (quote `load_kg` and `action`, and say why
     in plain words from its reason, citing the rule it names; `hold` means the same load and reps until a clinician
     reviews); for new lifts, "a weight you could lift 2-3 more times",
     never a number you invent.
3. Running week (`sport` running or both). For `running`, step 2's lifting week shrinks to the
   2 full-body strength sessions "Weekly baseline dose" asks of every client (the client may
   decline; say what it covers). Runs per week from the client's
   availability and what `coach runs week` shows they do now. Write each run as minutes in a
   zone `coach zones` printed (its name, RPE and talk test, and bpm only if it printed them),
   most of them in the easier zones; never a zone it did not print (the caps hide vigorous and
   near-maximal). Distance, per "Running load progression": the long run stays at or below
   `long_run_cap_km` from `coach runs week` (quote it; with no logged runs, ask their longest run
   of the last 30 days and log it with `coach runs add` before planning a longer one); with `paused` set, quote the injury's reason: unassessed, `long_run_cap_km` is null and `coach runs taper` refuses, so no runs; managed by a professional, the cap holds at the longest run within their limits); weekly km
   stay near the last logged week's `km`, built gradually; novices (the highest-risk group per
   "Common running injuries") keep weekly increases under 30% per week over 2 weeks, and the
   "10% weekly rule" is a convention, not a threshold. Quote km figures from the CLI only; when a
   figure you need is not printed, plan that run in minutes instead.
   Taper: when `coach runs taper` says `in_window`, the last `weeks` before the race follow it:
   weekly km cut progressively down to `taper_week_km` (quote it), keeping the intensity of key
   sessions and the runs per week. Outside the window, say when it starts (`starts_on`). There is
   no generic runner deload week: the research found no evidence for routine deloads in runners
   ("Taper before a goal race"), so `coach strength deload` stays for lifting.
   Pain or an injury (`coach injury list`, or what the client says): think first of the common
   running injuries; with no professional yet, a GP or physiotherapist assesses it before the
   painful run or movement is loaded; for an assessed tendon problem use the traffic light (red:
   cut that run's volume at the next session, refer after 2 weeks of red). The coach has no
   running-specific volume cut beyond that rule (the research found none), so follow the
   professional's limits.
   Race plans beyond the taper, a field test for HRmax and a runner PAL are not part of the
   coach: say so if asked.
4. Cardio: before prescribing a modality, load its rule (Reads) and use the intensity class the
   rule gives it, not a guess: jump rope, HIIT, sprints and plyometric jumps are vigorous work,
   never "moderate cardio". Start at the minimum of "Weekly baseline dose" (or what they already do, if more),
   split evenly over the days they offered (ask which, when it is unclear and the client has not delegated it; with only one
   day, add short walks on days they choose); intensity only as the zones `coach zones` printed (RPE and
   talk test, and bpm only if it printed them).
   For an activity with no rule of its own, use the rule of the closest modality by intensity; if
   the intensity is unclear, use the vigorous (HIIT) rule. Say which rule you used and suggest
   `/research`. When the vigorous (HIIT) rule applies, its screening gate and safety flags come
   before the activity is written into the plan and win over "start at the minimum of Weekly
   baseline dose" for that activity.
5. Nutrition: the calorie target, protein, fat, carbohydrate and fibre exactly as `coach macros`
   printed them.
6. Write `data/plan.md` in the profile language. Its first three lines, with nothing before
   them: `Fecha: YYYY-MM-DD` (en: `Date:`), `target_kcal: KCAL` and `in_deficit: true|false`
   (`kcal` and `in_deficit` as `coach macros` printed them; `/menu` reads these lines, so
   they keep the CLI's decimal point). When the client has given their training days,
   `training_schedule` is the fourth header line:
   `training_schedule: mon 18:30; wed 18:30; sat` (English day tokens mon tue wed thu fri sat
   sun in any profile language, an optional 24 h start time after each; leave the
   line out when the days are not known; `/menu` places pre- and post-workout meals with it).
   When the client trains on one of two days ("viernes o sábado"), write both with `|`:
   `fri|sat 10:00`.
   An optional line `rep_range: 6-8`, the client's usual rep range (leave it out when they use
   8-12), comes directly after the `training_schedule:` line, or directly after the third
   header line when `training_schedule:` is absent, with no blank line or heading between.
   Then the sections Semana de entrenamiento (runners: the running week, with the taper when it
   applies), Cardio, Nutrición, Notas de seguridad, Fuentes (en: Training week, Cardio,
   Nutrition, Safety notes, Rules used). In the training week, each session is one bullet:
   `- A (lunes): Sentadilla 3x8 51,0 kg; Press banca 3x10 34,0 kg` (label, a colon, then the
   lifts separated by `;`, each with its sets x reps and, when there is one, its load, so the
   printout shows the sets); one bullet per session in the week, the same sessions as
   `plan-week.yaml`; `coach plan export` finds the exercises there. Rule names stay
   as the knowledge headings, in brackets, listed in Fuentes (Rules used). Then a line on when
   to run `/review`, and the deferral line last when `refer_gp` is set.
7. Run `coach plan check` (with the same `--pal`, `--tdee` or `--current-kcal` you gave
   `coach energy`). If `ok` is false, fix each line in `problems` and run it again: `unread`
   lists session parts the export cannot read as lifts (rewrite them as `Name 3x8 40 kg`), and
   a session count that differs from `plan-week.yaml` means the two files describe different
   weeks. A line in
   `notes` (the target differs from a fresh estimate) needs no change when the target was agreed
   at /review or kept from the previous plan; never replace an agreed target because of it.

## Writes

- `data/plan.md`, and `data/plan-week.yaml` for `coach strength plan-sets` (replace the previous plan; keep the date at the top).

## Output

The plan in the profile language, as written to `data/plan.md`, then one line on when to review
(`/review` weekly). Offer a printable copy: `coach plan export` writes `data/plan.pdf` (or
`--out FILE`), the plan with a video search link and QR code per exercise for checking
technique (`--no-qr` leaves the codes out). A long plan may run past one page. If it fails
saying the `pdf` extra is missing, tell the client to run `uv sync --extra pdf`.

## Safety

- `hold_progression`: no added load, reps, sets or intensity, even if the client asks; say
  a clinician's review comes first.
- `cap_moderate` or `review_before_vigorous`: no vigorous or maximal work (HIIT, 1RM tests,
  all-out sprints, jump rope, plyometric jumps, near-maximal lifts, runs in a vigorous or
  near-maximal zone, race efforts). With
  `review_before_vigorous`, say a qualified exercise professional or clinician reviews it first
  if the client wants it; record that review with `coach profile set
  screening.vigorous_reviewed true` only when the client says it happened.
  `no_all_out_sprints`: no SIT or REHIT at all. Even without it, SIT or REHIT only for a client
  with every PAR-Q+ answer NO and 4+ weeks of regular moderate cardio without symptoms, never
  for a sedentary beginner ("PAR-Q+ specific thresholds").
- `screening.regular_exercise` not `true` and no ACSM reason in `coach safety`: start at
  light-to-moderate intensity and build up over the block
  (`coach knowledge section recovery-habits "ACSM 2015 screening algorithm"`).
- `paused` in `coach strength progress`: the lift does not progress. With no `load_kg`, it is not
  loaded until a GP or physiotherapist has assessed the injury; otherwise `load_kg` is a ceiling:
  reduce or swap the lift within the professional's limits. Clear it with `coach injury clear
  AREA` only when the professional has cleared it.
- `use_rpe_not_hr`: no heart-rate numbers. `prescriber_owns_weight` or `no_deficit`: no deficit language; the CLI targets already
  reflect it.
- If `coach safety` shows `refer_gp`, say what the professional should review first and end
  with the `deferral_line` from `coach safety` (the line in `docs/safety.md`), copied exactly.
