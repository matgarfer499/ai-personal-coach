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

- First contact, `data/profile.yaml` missing, or `coach profile show` lists missing fields. When
  `missing` lists only some fields, ask only for those fields (a profile saved before a field
  was required, for example, lists just `emergency_number`); do not redo the other steps.
- The client asks to redo screening or change basic data (then ask only what changes).

## Reads

- `coach profile show` (what is already there and what is missing).
- `docs/safety.md`: the medication and condition token table, the deferral line.

## Steps

Ask about one step per message. Store each answer as soon as you have it with
`coach profile set FIELD VALUE` (lists comma-separated, dates YYYY-MM-DD, true/false).

1. **Language and region.** Ask es or en (with nothing from the client yet, ask in one line in
   both languages); set `language` (the coach speaks only these two; say so if they ask for
   another). Ask the country. Set `region es` for Spain, including when they only name a Spanish
   city. For a country with no `regions/<code>/` folder (the CLI refuses it), set `region none`
   and say: menus use the general food table and Open Food Facts products, and a region can be
   added (docs/adding-a-region.md).
   Then run `coach profile show` and look only for `emergency_number` in `missing` (the other
   fields are asked in later steps, in order); when it is there, ask which number they call for
   an emergency where they live (112 across the EU, 911 in the US, Canada and Mexico, 999 in the
   UK, 000 in Australia) and store it with `coach profile set emergency_number N`. If they
   cannot say and the region is a real one (not `none`), tell them you are storing their
   region's number (`coach safety` shows it) and that they should check it, then store that
   number with the same command. If they cannot or do not want to give one, store
   `coach profile set emergency_number none` (it counts as set, so `missing` clears and they are
   not asked again); `coach safety` then prints no number of its own, and a red flag gets
   the local emergency number for their country (112 across the EU, 911 in the US, Canada and
   Mexico, 999 in the UK, 000 in Australia; ask where they live if unknown), said on a separate
   line before the deferral line, which stays copied exactly.
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
4. **PAR-Q+.** The PAR-Q+ Collaboration's terms forbid putting the form's questions into a
   chat or app, translating or rewording them without written permission
   (`coach knowledge section recovery-habits "PAR-Q+ 2023 as the default entry screen"`;
   docs/safety.md, Screening). So never read, quote, paraphrase or translate its questions.
   - If they have already filled it in, go to the two questions below.
   - Otherwise send one link in their language and say in one plain line what it is (a short
     official health questionnaire, about 5 minutes, on paper or screen) and that you will ask
     two questions about it afterwards. Spanish: "PAR-Q+ en español"
     (https://eparmedx.com/wp-content/uploads/2023/12/Spanish.pdf; the listing page
     https://eparmedx.com/print-versions-of-par-q/languages/ in case the file moves). English:
     https://eparmedx.com/print-versions-of-par-q/. Then wait.
   - Then ask the two outcome questions, one per message, in their language and in your own
     words, never the form's: first whether they answered YES to any of the questions on the
     first page (the general health questions); only if yes, whether they answered YES to any
     of the follow-up questions. A filled-in PDF they send: read only those two outcomes, ask
     them to confirm, never store the file or copy its contents, name or path anywhere.
   - If they will not open the form, store nothing and say in one line that the coach then
     keeps to light-to-moderate work and no sprints until they do (the CLI applies it).
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
   fainting, or chest pain with breathlessness and sweating; with none stored, the local
   emergency number for their country, 112 across the EU, 911 in the US, Canada and Mexico, 999 in
   the UK, 000 in Australia).
6. **Medications and conditions.** Ask what they take and any diagnoses. Map to tokens with the
   table in `docs/safety.md` and store them as `medications` and `conditions`, each list in one
   `coach profile set` (it replaces the list, so give every item, comma-separated). Store unknown
   names as given; `coach profile show` lists them under `unrecognised`: say they are recorded
   and no calculation depends on them (a blood-pressure medicine such as enalapril also means
   asking whether they have `hypertension`). No medications or no diagnoses: store `none`
   (an empty list). Women: pregnant or planning? Add `pregnant` or `planning_pregnancy` to the
   `conditions` list (they are condition tokens, not fields); neither means no. With
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
   `sport`: what they train for: `lifting`, `running` or `both` (store it with
   `coach profile set sport VALUE`; unset behaves as lifting). It picks the protein rule
   (`coach macros` uses "Daily protein target for endurance runners" for `running`; `both`
   follows the lifter rule, as that rule says) and what /plan builds.
   Runners (`running` or `both`): ask their usual weekly km and runs per week, and their longest
   recent run. These are not profile fields: suggest logging their recent runs (`/import` with a
   run CSV, or one `coach runs add --date D --km K --minutes M` per run they remember with
   figures) so `coach runs week` has the baseline the single-run spike rule needs. Their runs per
   week count as training days for `activity_level` below.
   `experience` (convention, listed in `docs/conventions.md`; no rule defines the levels): the
   levels describe lifting only, also for runners; a runner who does not lift is `novice`, and
   their running experience is the weekly km and runs above, not this field. Ask
   how many months they have trained consistently (about 2 or more sessions a week), then store
   `novice` for under 12 months; `intermediate` for 12 months or more while they still add load
   or reps most months; `advanced` for 12 months or more once progress has slowed to a plateau.
   The 12 months come from "Novice strength gains and plateau" and "Trained lifters: 12-20
   weekly sets". Ask first "¿Entrenas ahora o lo dejaste? ¿Desde cuándo?". For any loads they
   give, ask whether they are from now or from before the break. Choose the level from what they
   lift today; loads from before the break are history, and /plan restarts lower per
   `coach knowledge section strength-hypertrophy "Short breaks cost little"` (breaks of weeks),
   `"Longer detraining"` and `"Returning lifters and \"muscle memory\""` (breaks of months).
   Injuries: any current injury or pain in an area? Record each with `coach injury add AREA
   --since DATE`, adding `--professional WHO` when someone has assessed it and
   `--exercises "LIFT, LIFT"` for the lifts it affects: ask for them in the client's own words,
   in Spanish or English, never for English app names; aliases map common names. Before any
   import, `coach injury add` prints every name under `unmatched`: say that is expected
   only while no sessions are imported yet, and that /import re-checks it; once sessions exist,
   an unmatched name needs the client to say which logged lift it is.
   `activity_level`, per `coach knowledge section nutrition "Activity multipliers (PAL)"`:
   `desk` = desk job with little exercise or a few sessions a week; `desk_training` = desk job and
   about 1 h of training on 4 or more days (convention: "most days" read as 4+); `active` =
   physical job, or daily moderate-to-vigorous exercise plus lots of daily movement. Ask the
   training days in a usual week as one number (convention: a range such as "3-4" takes the
   lower number). 3-4 days: `desk`; 4 days in most weeks: `desk_training`; if unsure which,
   `desk`, per `coach knowledge section nutrition "Self-reported activity is noisy"` ("choose
   the lower plausible multiplier when unsure"). Say so in one line: the weight trend corrects
   it after 2-4 weeks.
9. **Check.** `coach profile show`: `missing` must be empty. Ask as in step 1 only if
   `emergency_number` is listed (it is not when the region supplies one); if the client declines, store `none` and do not ask again. Go on
   to step 10 when `missing` is empty. Mention any `unrecognised` items.
10. **Targets.** Run `coach safety`, then `coach energy` and `coach macros`. Only when
    `use_rpe_not_hr` is false, ask every client (lifters too) for a resting pulse taken seated
    in the morning, averaged over a few days, and an observed all-out peak if they have one
    (a well-fitted chest strap in a hard interval or race), per `coach knowledge section
    cardio-health "HRmax: formulas and setting the anchor"`; store them with
    `coach profile set hr_rest N` and `coach profile set hr_max N` (skip either if unknown; the
    CLI then uses the formula, and says so). With `use_rpe_not_hr`, store neither: zones are RPE
    only. Then run `coach zones`, which reads the stored values.
    When the `coach energy` `notes` hold the `active` `no_training` note, ask whether the activity
    comes from the job or from exercise. Only when it was exercise that has stopped, run
    `coach profile set pal_override VALUE` with the value the note gives (never one you chose or
    computed), then rerun `coach energy` and `coach macros`: the choice applies to every path
    while `no_training` holds and is ignored once it clears. From the job, or a mix of both:
    store nothing, and say the coach cannot model a mix yet (they may tell a clinician). Tell
    them to keep training on hold until a clinician clears it. When the hold ends, run
    `coach profile set pal_override none`.
11. **Reminder.** Say the coach will suggest refreshing its evidence every 6 months
    (`research_reminder_months`); set another number only if they ask.

## Writes

- `data/profile.yaml`, only through `coach profile set`. Nothing else.

## Output

One message in the profile language:
1. What you stored, in one short list (no screening answers repeated back, only outcomes).
2. Starting targets quoted from the CLI (say the estimate's spread once: `coach energy` prints
   `tdee_range`): calorie target (and, unless `no_weight_targets` is set,
   that it is a starting estimate to be corrected from their trend after 2-4 weeks), protein, fat, carbohydrate and fibre, and the
   intensity zones `coach zones` printed (up to five, very light to near-maximal) with their
   talk-test cues; never mention a zone it did not print.
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
