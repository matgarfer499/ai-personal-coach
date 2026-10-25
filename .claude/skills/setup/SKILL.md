---
name: setup
description: Use when a new client starts with the coach, when data/profile.yaml is missing or incomplete, or when the client wants to redo their profile or screening (/setup).
argument-hint: "[redo]"
---

# /setup

Builds the client's profile and screening, then gives starting targets. Every number comes from
the `coach` CLI.

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

- First contact, `data/profile.yaml` missing, or `coach profile show` lists missing fields.
- The client asks to redo screening or change basic data (then ask only what changes).

## Reads

- `coach profile show` (what is already there and what is missing).
- `docs/safety.md`: the medication and condition token table, the deferral line.
- `forms/parq-plus-es.pdf` or `forms/parq-plus.pdf`, when present: the official PAR-Q+ (step 4).

## Steps

Ask about one step per message. Store each answer as soon as you have it with
`coach profile set FIELD VALUE` (lists comma-separated, dates YYYY-MM-DD, true/false).

1. **Language and region.** Ask es or en (with nothing from the client yet, ask in one line in
   both languages); set `language` (the coach speaks only these two; say so if they ask for
   another). Ask the country. Set `region es` for Spain, including when they only name a Spanish
   city. For a country with no `regions/<code>/` folder (the CLI refuses it), leave the region
   unset and say: menus use the general food table and Open Food Facts products, and a region
   can be added (docs/adding-a-region.md). Then run `coach safety`: with no `emergency_number`,
   ask which number they call for an emergency where they live (112 across the EU, 911 in the
   US, Canada and Mexico, 999 in the UK, 000 in Australia) and store it with
   `coach profile set emergency_number N`. If they cannot say, use 112 in Europe and tell them
   to check it.
2. **Eating-disorder prompt, before any weight question.** Ask gently, in your own words, in one
   message, as a conversation and never a diagnosis: making yourself sick when uncomfortably full; worry about
   losing control over how much you eat; feeling fat when others say you are thin; food or weight
   dominating your thoughts or life; a recent large weight loss that worried you or others.
   Per `coach knowledge section nutrition "Eating-disorder screening: brief questions as a prompt"`:
   - A partial or unclear answer ("algo", "a veces", "no gran parte"): ask one short follow-up
     about how often and how much it bothers them, then count it as yes or no from what they say.
     For loss of control, ask whether they have episodes of eating a lot while feeling unable to
     stop. Do not count a partial answer as yes without asking.
   - Store the number of clear yes answers: `screening.scoff_yes_count N` (0 to 5). The CLI
     treats 2 or more as a positive screen; never apply the cut point yourself.
   - Also store `screening.scoff_positive true` for a warning sign, which is positive whatever the
     count (`coach knowledge section recovery-habits "Warning signs that warrant referral"`): a
     yes to making yourself sick, a recent weight loss that worried them or others, bingeing with
     loss of control, or compensating for food with vomiting, laxatives, diet pills or exercise.
     Otherwise store `false`.
   - Run `coach safety` and say the outcome in one line. With a single yes and no warning sign,
     say it is noted, that it is not a positive screen, and that the coach will keep an eye on it.
   - If the client disputes a positive outcome, listen once. If they correct what an answer
     meant, re-ask that question and store the new count. If the answers stand, say once that
     the screen is what it is and why, say they can redo it with `/setup redo` if things change
     or a professional reviews them, and move on. Do not argue twice.
3. **Basics.** `sex` (the equations exist only for female and male; if neither fits, explain
   that and ask which set to use, or skip calorie targets), `birth_date`, `height_cm`,
   `weight_kg`. Under 18 (from `birth_date`): stop here; say the coach is for adults, suggest a
   paediatrician, GP or paediatric dietitian, and give only general habits (no targets, no
   weighing), per `coach knowledge section nutrition "Under-18s"`. After a positive screen (`coach safety` shows `no_weight_targets`), ask whether they are happy to share an approximate
   weight for the estimates; never ask them to weigh themselves. If they decline, leave
   `weight_kg` unset and give no calorie or macro targets (say they are optional).
4. **PAR-Q+.** The form says "NO changes are permitted", so its questions are never reworded,
   shortened or translated
   (`coach knowledge section recovery-habits "PAR-Q+ 2023 as the default entry screen"`).
   If they have already filled it in, ask the two questions at the end of this step. Otherwise, if `forms/parq-plus-es.pdf` (Spanish clients) or `forms/parq-plus.pdf`
   exists, read it and ask the questions yourself:
   - First message: the form's title and introduction, then the 7 GENERAL HEALTH QUESTIONS,
     copied exactly with their numbers and notes, asking YES or NO to each. If the form is not in
     the profile language, say once that the official form must be asked as printed; when the
     client asks what a word means, explain it in their language after the question, without
     replacing it.
   - All NO: quote the form's text for that case. Any YES: ask each follow-up condition question
     (1 to 10) exactly as printed and, for each YES, its lettered questions; follow the form's
     "If NO go to question N". Then quote the form's text for the result.
   - Quote the form's "Delay becoming more active if" list once.
   - With no PDF in `forms/`, send the official form (https://eparmedx.com, "PAR-Q+") and ask the
     two questions below.
   Any YES on the 7 questions? Any YES on the follow-up questions? Store
   `screening.parq_any_yes` and `screening.parq_followup_yes`. With any YES, or over 45, ask
   whether a qualified exercise professional or clinician has reviewed vigorous or maximal
   work for them (`coach knowledge section recovery-habits "PAR-Q+ specific thresholds"`); only
   a clear yes is stored as `screening.vigorous_reviewed true`. At a redo, store the PAR-Q+
   answers first: when one changes, the CLI drops the old review, so ask again.
5. **Warning symptoms.** Ask about chest, neck, jaw or arm pain or pressure, breathlessness at
   rest or with mild effort, dizziness or fainting, palpitations, ankle swelling, calf pain on
   walking (`coach knowledge section recovery-habits "Cardiac warning symptoms: stop and refer"`).
   Store `screening.cardiac_symptoms true` for a symptom they report; a "none" to the whole list
   is `false`. For "not sure",
   describe it once more; if still unsure, store `false` and tell them to stop and see a doctor
   if it appears. If any are happening now or at rest, stop the setup and
   tell them to seek care (the `emergency_number` from `coach safety` for chest pain at rest,
   fainting, or chest pain with breathlessness and sweating).
6. **Medications and conditions.** Ask what they take and any diagnoses. Map to tokens with the
   table in `docs/safety.md` and store them as `medications` and `conditions`, each list in one
   `coach profile set` (it replaces the list, so give every item, comma-separated). Store unknown
   names as given and say the coach cannot classify them. Women: pregnant or planning? (`pregnant`, `planning_pregnancy`; no token means no). With
   `hypertension`, or if they know their blood pressure: latest seated reading after 5 min rest,
   stored as `screening.bp_systolic` and `screening.bp_diastolic`. With hypertension and no
   reading (also when they only say it is "controlled"), store nothing: the CLI then applies the
   BP-unknown band. Ask them to take one and give it at their next `/checkin`.
7. **Cycle (women).** Regular, new irregular periods, or absent 3+ months (or fewer than 6 a
   year)? Store `screening.menstrual` as `normal`, `irregular_new`, `absent` or
   `not_applicable`. Ask whether they use hormonal contraception; if so, say it masks the cycle, so they should
   report low energy, low libido or stress fractures at `/checkin` (not stored).
8. **Goal and training.** `goal`: fat_loss (including "lose fat and keep strength"),
   maintenance, muscle_gain, or recomposition (eat around maintenance while training; for
   beginners, returning lifters and higher body fat, per `coach knowledge section nutrition
   "Body recomposition"`).
   `experience` (convention, listed in `docs/conventions.md`; no rule defines the levels): ask
   how many months they have trained consistently (about 2 or more sessions a week), then store
   `novice` for under 12 months; `intermediate` for 12 months or more while they still add load
   or reps most months; `advanced` for 12 months or more once progress has slowed to a plateau.
   The 12 months come from "Novice strength gains and plateau" and "Trained lifters: 12-20
   weekly sets". After a long break, ask what they could lift before and choose the level they
   can load at today.
   Injuries: any current injury or pain in an area? Record each with `coach injury add AREA
   --since DATE`, adding `--professional WHO` when someone has assessed it and
   `--exercises "LIFT, LIFT"` for the lifts it affects.
   `activity_level`, per `coach knowledge section nutrition "Activity multipliers (PAL)"`:
   `desk` = desk job with little exercise or a few sessions a week; `desk_training` = desk job and
   about 1 h of training on 4 or more days (convention: "most days" read as 4+); `active` =
   physical job, or daily moderate-to-vigorous exercise plus lots of daily movement.
9. **Check.** `coach profile show`: `missing` must be empty; mention any `unrecognised` items.
10. **Targets.** Run `coach safety`, then `coach energy`, `coach macros` and `coach zones`.
    Only when `use_rpe_not_hr` is false, ask for a morning resting pulse (`--hr-rest N`) and an
    observed all-out peak (`--hr-max N`); skip either if unknown.
11. **Reminder.** Say the coach will suggest refreshing its evidence every 6 months
    (`research_reminder_months`); set another number only if they ask.

## Writes

- `data/profile.yaml`, only through `coach profile set`. Nothing else.

## Output

One message in the profile language:
1. What you stored, in one short list (no screening answers repeated back, only outcomes).
2. Starting targets quoted from the CLI: calorie target (and, unless `no_weight_targets` is set,
   that it is a starting estimate to be corrected from their trend after 2-4 weeks), protein, fat, carbohydrate and fibre, and the
   intensity zones with their talk-test cues.
3. Every reason from `coach safety` and every note from `coach energy` that changes what they
   should do, in plain words, keeping the rule name in brackets.
4. Next steps: `/checkin` on most days, `/import` for workout exports, `/plan` for the plan.
   With `no_training`, offer `/plan` only after a doctor has reviewed them; with `refer_gp`
   alone, offer it and say the professional's review comes first.

## Safety

- If `coach safety` shows `refer_gp`, give the targets the CLI printed but say that the
  professional's review comes first for whatever its reasons name, and end with the deferral
  line from `docs/safety.md`, copied exactly, in the profile language.
- `no_training`: give no training targets; say why and that a doctor must review first.
- Never set a deficit, weight target or weigh-in schedule after a positive eating-disorder
  screen; the CLI already refuses, so quote what it prints.
