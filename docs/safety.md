# Safety

The coach is a training and nutrition guide for healthy adults. It hands over to a professional
whenever the knowledge rules say so. Where an override can be computed, it lives in the `coach`
package (`coach/safety.py` and the calculators), not only in skill text, so a skill cannot talk
its way past it. The last section says which protections are code and which are instructions to
the model.

## What the coach is not

- Not a doctor: it does not diagnose, treat, or start, stop or change medication.
- Not a dietitian: no clinical diets or medical nutrition therapy, and nothing below the calorie
  floors (1,200 kcal women, 1,500 kcal men), which need clinical supervision.
- Not a therapist: it does not assess or treat eating disorders; a positive screen means a
  referral, not a plan.
- Not for under-18s (`coach` refuses calorie targets for them and /setup refers them to a
  paediatric professional), and not an emergency service: in an emergency it tells the client
  to call the local emergency number first. `coach safety` prints it as `emergency_number`: the
  client's own (`coach profile set emergency_number N`), else their region's (`emergency_number`
  in `region.yaml`: 112 for Spain), else none, and then the skills ask which number to call
  where the client lives (112 across the EU, 911 in the US, Canada and Mexico, 999 in the UK,
  000 in Australia) and store it. A client who cannot give a number stores
  `coach profile set emergency_number none` (counts as set; `coach safety` then prints the
  region's number if there is one, else none); the skills fall back to the local emergency
  number of their country when a red flag fires.
- Not a medical device: its numbers are estimates from equations and logs, and every rule is
  general guidance from the knowledge files.

## The deferral line

When any flag below sets `refer_gp`, the skill's answer ends with this line, copied exactly, in
the profile's language:

- **es:** `Esto es orientación general de un entrenador automatizado, no consejo médico. Por lo que me has contado, habla con tu médico (o con el profesional que te indico arriba) antes de ponerlo en práctica.`
- **en:** `This is general guidance from an automated coach, not medical advice. Because of what you told me, talk to your doctor (or the professional named above) before acting on it.`

Above it, the skill names the professional the reason names (prescriber, midwife or
obstetrician, eating-disorder professional), else the GP.

## Screening

Asked at /setup; answers are stored as outcomes in `data/profile.yaml` under `screening`, never
as question text. `coach profile set screening.KEY none` clears an answer (an old BP reading).

| Screen | How | Stored as | Rule | Asked again |
|---|---|---|---|---|
| ACSM 2015 preparticipation screen (the default) | Three questions in the coach's own words, one per message: regular exercise (30+ min of planned moderate exercise, 3+ days a week, for the last 3 months), a doctor's diagnosis of cardiovascular, metabolic (type 1 or 2 diabetes) or renal disease, and the warning symptoms. It is a published method, not a form, so it can be asked in the chat; the PAR-Q+ cannot (below) | `regular_exercise`, `known_disease` (list of `cardiovascular`, `metabolic`, `renal`; `no` stores none), `symptoms` (list of the symptom tokens; `no` stores none), `medically_cleared` | recovery-habits.md "ACSM 2015 screening algorithm", "Cardiac warning symptoms: stop and refer" | at /setup redo; `coach profile set` drops `medically_cleared` whenever `known_disease` changes |
| PAR-Q+ 2023 (optional) | Offered by link, never required. The client fills in the official form (eparmedx.com) in their language; the coach then asks only the two outcomes, in its own words. The form's terms forbid putting its questions into a chat or app, translating them or redistributing them without written permission from the PAR-Q+ Collaboration, so the coach never quotes them | `parq_any_yes`, `parq_followup_yes` | recovery-habits.md "PAR-Q+ 2023 as an optional extra screen", "PAR-Q+ specific thresholds" | at /setup redo, e.g. after a new diagnosis, medication or pregnancy |
| Review before vigorous work | Asked when `review_before_vigorous` is set and the client wants vigorous or maximal work: has a qualified exercise professional or clinician reviewed it? | `vigorous_reviewed` | recovery-habits.md "PAR-Q+ specific thresholds" | at /setup redo; `coach profile set` drops it whenever `parq_any_yes` or `parq_followup_yes` changes, since the review covered the old answers |
| Injuries | Any current injury or pain in an area: where, since when, who assessed it, which logged exercises it affects | `injuries` (not under `screening`; set with `coach injury add` and `coach injury clear`) | recovery-habits.md "Some pain during exercise is acceptable in chronic, assessed pain" | at /setup, /plan, and whenever the client reports pain or a clearance at /checkin |
| Eating-disorder prompt | The five SCOFF-style questions in the coach's own words, as a prompt for a conversation, never a diagnosis; one follow-up for a partial answer | `scoff_yes_count` (clear yes answers, 0 to 5), `scoff_positive` (a warning sign) | nutrition.md "Eating-disorder screening: brief questions as a prompt" | set again if warning signs appear (Red flags) |
| Cardiac warning symptoms | Part of the ACSM screen at /setup (`symptoms`); at /checkin `checkin add --symptoms` | `symptoms`, `cardiac_symptoms` | recovery-habits.md "Cardiac warning symptoms: stop and refer" | every /checkin |
| Menstrual cycle (women) | Regular, new irregular, or absent | `menstrual` | nutrition.md "Menstrual dysfunction: stop and refer" | weekly at /checkin |
| Resting blood pressure | Latest seated reading after 5 min rest; asked of anyone with hypertension | `bp_systolic`, `bp_diastolic` | recovery-habits.md "Resting BP thresholds to defer or refer" | weekly at /checkin |
| Medications and conditions | Mapped to tokens (table below) | `medications`, `conditions` | see the flags table | at /setup redo |

Until `scoff_yes_count` or `scoff_positive` is answered, the calculators refuse to compute a deficit. A stored
calorie target passed with `--kcal` is clamped both ways: raised when the flags block a deficit,
lowered to maintenance when they block a surplus (positive screen, GLP-1, pregnancy,
training stopped).

## Medication and condition tokens

Only these tokens change what the calculators do. Map the client's words to them; when unsure,
store the name as given and tell the client the coach cannot classify it.

| Token | Client may say | Rule |
|---|---|---|
| `beta_blocker` | bisoprolol, atenolol, metoprolol, propranolol, nebivolol, carvedilol, "a beta-blocker" | cardio-health.md "Beta-blockers: no formula-based HR zones" |
| `glp1` | semaglutide (Ozempic, Wegovy, Rybelsus), liraglutide (Saxenda, Victoza), dulaglutide (Trulicity), tirzepatide (Mounjaro) | nutrition.md "GLP-1 users: protein, training and red flags" |
| `pregnant` | pregnant | nutrition.md "Pregnancy"; recovery-habits.md "Default is to be active" |
| `planning_pregnancy` | trying to conceive | nutrition.md "Pregnancy" |
| `hypertension` | high blood pressure, on BP medication | recovery-habits.md "Resting BP thresholds to defer or refer" |
| `heart_disease` | diagnosed heart condition | cardio-health.md "ACSM intensity bands" (cardiac team sets zones) |
| `weight_related_condition` | type 2 diabetes, sleep apnoea, fatty liver, or another condition a doctor links to weight | nutrition.md "Resistance training during any diet, especially for older adults" |

## Flags and what they change

Computed by `coach safety` from the profile; the calculators obey them.

| Trigger | Flags | Effect in the calculators |
|---|---|---|
| Under 18 (from `birth_date`) | `no_calorie_targets`, `no_deficit`, `no_weight_targets`, `refer_gp` | no calorie or macro targets at all (nutrition.md "Under-18s"); no weigh-ins, waist or calorie logs; paediatrician, GP or paediatric dietitian |
| Positive eating-disorder screen: `scoff_yes_count` 2 or more (the SCOFF cut point), or `scoff_positive` | `no_deficit`, `no_weight_targets`, `refer_gp` | maintenance calories, no surplus, no weigh-ins, no weight trend; `checkin add` also refuses waist and calorie logs; `mealplan` refuses a free meal (nutrition.md "Refeeds and cheat meals") |
| GLP-1 or tirzepatide | `no_deficit`, `prescriber_owns_weight` | maintenance calories; protein 1.2-1.6 g/kg; low-intake note |
| GLP-1 user pregnant or planning pregnancy | `refer_gp` | contact the prescriber promptly |
| Beta-blocker | `use_rpe_not_hr` | RPE zones only, capped at RPE 13 |
| Pregnancy | `no_deficit`, `no_weight_targets`, `prescriber_owns_weight`, `use_rpe_not_hr`, `refer_gp` | no weigh-ins in the coach (weight is the midwife's); RPE zones with moderate 13-14, never RPE 18 (recovery-habits.md "Gauge intensity by talk test and RPE, not a heart-rate cap") |
| New irregular periods | `hold_deficit`, `refer_gp` | no new or deeper deficit |
| Periods absent 3+ months (or fewer than 6 a year) | `no_deficit`, `refer_gp` | maintenance calories |
| ACSM: not exercising regularly, known disease, no symptoms, not cleared | `clearance_before_exercise`, `no_training`, `hold_progression`, `refer_gp` | no programme until a clinician clears exercise: no zones, no loads; calories follow the normal rules (no `no_deficit`). Once `medically_cleared`: start light-to-moderate (`review_before_vigorous` until `vigorous_reviewed`) |
| ACSM: exercising regularly, known disease, no symptoms, not cleared | `review_before_vigorous`, `refer_gp` | continue moderate work; no vigorous or near-maximal work before medical clearance (`medically_cleared`) |
| ACSM: no known disease and no symptoms (either activity level) | none | no clearance needed; a sedentary client starts light-to-moderate and builds up (skill text, recovery-habits.md "Acute cardiac risk is concentrated in the unaccustomed") |
| PAR-Q+ follow-up YES | `refer_gp`, `hold_progression` | `strength progress` says `hold`: same load and reps |
| No entry screen answered (neither a complete ACSM screen nor the PAR-Q+); or any PAR-Q+ YES (a follow-up YES counts), or aged 45 or more (from `birth_date`), until `vigorous_reviewed` is true | `review_before_vigorous` | no vigorous or near-maximal zone (the zones note says why, even when the zones are RPE only); the skills prescribe no vigorous or maximal work (HIIT, 1RM tests, all-out sprints, jump rope, plyometric jumps) until a qualified exercise professional or clinician has reviewed it. It does not set `refer_gp`: the plan itself needs no review, so the skills name the professional when vigorous work comes up instead of ending every answer with the deferral line |
| Any PAR-Q+ YES, reviewed or not, or PAR-Q+ not answered | `no_all_out_sprints` | no SIT or REHIT: they need every PAR-Q+ answer NO. With every answer NO, /plan also requires 4+ weeks of regular moderate cardio without symptoms and never gives them to sedentary beginners (skill text) |
| Active injury with `exercises` listed | `paused_exercises` (exercise: its reasons and whether a professional assessed it) | `strength progress` says `paused`: no progression, no stall, no added sets. Unassessed: no load at all. Assessed: at most the last load, or the lower restart load after a break; the professional's limits decide the rest. Names match logged lifts by case, accents, "(Equipment)" and muscle-map aliases; `coach injury add` lists names that match no logged lift as `unmatched`. A new injury in a cleared area starts unassessed. Sessions up to its `cleared_on` never count as a stall afterwards |
| Active injury with no `professional` | `refer_gp` | a GP or physiotherapist assesses it before it is loaded; sharp or worsening pain: stop and refer |
| Cardiac warning symptoms (`symptoms` at /setup or `cardiac_symptoms`; the ACSM symptom cells, either activity level) | `no_training`, `hold_progression`, `refer_gp`, `no_deficit` | stop exercising until a clinician clears it: no zones, no loads, calories at maintenance (energy: see "`no_training` and the energy estimate"); `emergency_line` says when to call the number now |
| Resting BP 180+ systolic or 110+ diastolic | `no_training`, `hold_progression`, `refer_gp`, `no_deficit` | no zones, no training until a doctor reviews it (200/110+: no exercise, see a doctor promptly) (energy: see "`no_training` and the energy estimate") |
| Resting BP 160-179 systolic or 90-109 diastolic, or hypertension with BP unknown | `cap_moderate`, `hold_progression`, `refer_gp` | no vigorous or near-maximal zone; GP review before starting or progressing |
| Resting BP 140-159 systolic with diastolic below 90 | `cap_moderate`, `refer_gp` | moderate intensity; GP check |
| Age 65+ without obesity and a weight-related condition | (calculator rule) | no deficit |
| Heart disease | (calculator rule) | no zones; the cardiac team sets them |
| Calories below 1,200 (women) / 1,500 (men) | (calculator rule) | raised to the floor and flagged |

### One instruction, and the lines the skills quote

`coach safety` lists `reasons` most urgent first (stop training, out-of-scope and
eating-disorder blocks, medical hand-offs, referrals, then intensity caps); `instruction` is the
first one, the thing to do above all else. With `no_training`, the intensity caps (PAR-Q+
"light-to-moderate work only", the BP light-to-moderate band) contradict the stop, so they move to
`superseded`: kept for the record, never given as advice. `deferral_line` (with `refer_gp`) is
the line above in the profile language, and `emergency_line` (with cardiac symptoms) says when to
call `emergency_number` now; skills quote both fields instead of copying text.

`no_training` from cardiac symptoms or a very high BP also sets `no_deficit` (convention, `safety.NO_TRAINING_NO_DEFICIT` in
docs/conventions.md): no rule covers dieting while symptoms or a very high BP await a
clinician, so calories stay at maintenance until training is cleared. `refer_gp` alone (a PAR-Q+
follow-up YES, an unassessed injury) keeps the deficit, and so does the ACSM
"clearance before any exercise" stop (`clearance_before_exercise`): a known, stable diagnosis is
not a symptom awaiting a clinician.

### Symptoms at check-in

`coach checkin add --symptoms TOKENS` records cardiac warning symptoms as tokens (`chest_pain`,
`neck_jaw_arm_pain`, `breathless`, `dizzy`, `faint`, `palpitations`, `ankle_swelling`, `calf_pain`,
`unusual_fatigue`, from recovery-habits.md "Cardiac warning symptoms: stop and refer"); any one
sets `screening.cardiac_symptoms true`. Free-text `--notes` are scanned for symptom words in
Spanish and English (`safety.SYMPTOM_WORDS`); hits come back as `possible_red_flags`, a prompt
for the skill to ask, never a flag on their own.

### `no_training` and the energy estimate

`energy.tdee` (run by `coach energy`) stops counting planned training when `no_training` is set:
- `desk_training` uses the `desk` PAL band (nutrition.md "Activity multipliers (PAL)": desk work
  with little exercise).
- Only `active` is kept, with a note, because it may come from the job: its text is in
  `energy.calorie_target`. It tells the client that if the activity comes from exercise (stopped
  while training is on hold) to store the desk midpoint (`energy.DESK_PAL`) with
  `coach profile set pal_override`, that if it comes from the job nothing changes, and that the
  coach cannot model a mix of both yet. It is skipped when `--pal`, `--tdee` or a stored
  `pal_override` applies.
- `profile.pal_override` applies only while `no_training` is set and the level is `active`
  (every path: `coach energy`, `coach macros`, menus); once the flag clears it is ignored. Each
  use is announced by a note ("using stored pal_override ...") and `coach profile set` warns when
  it has no effect or is inactive. `check_pal` (profile.py) is the one 1.4-2.0 range check. An explicit `--pal` or `--tdee`
  still wins.

## Red flags

Signs the client may report at any time, each with the rule that defines it. The rows marked
"code" are stored with `coach profile set` and then enforced by the flags above; the others are
skill instructions backed by the named rule, which the model loads with
`coach knowledge section`.

| Sign | Rule | What the coach does | Enforced by |
|---|---|---|---|
| Chest, neck, jaw or arm pain or pressure, breathlessness, dizziness or fainting, palpitations | recovery-habits.md "Cardiac warning symptoms: stop and refer" | stop exercising and see a doctor; the emergency number now for chest pain at rest, fainting, or chest pain with breathlessness and sweating | code (`cardiac_symptoms`) |
| A resting BP reading in a band | recovery-habits.md "Resting BP thresholds to defer or refer" | the band's limits; at 200/110 or more, re-measure and see a doctor promptly, urgently with headache, chest pain, visual change, neurological symptoms or breathlessness | code (`bp_systolic`, `bp_diastolic`) |
| New missed or irregular periods, or periods gone | nutrition.md "Menstrual dysfunction: stop and refer" | hold or stop the deficit; GP | code (`menstrual`) |
| A positive eating-disorder screen (2 or more yes answers) | nutrition.md "Eating-disorder screening: brief questions as a prompt" | no deficit, weight targets or weigh-ins; GP or eating-disorder professional | code (`scoff_yes_count`, `scoff_positive`) |
| Vomiting, laxatives, diuretics or diet pills to control weight; exercise to compensate for food; rigid food rules; bingeing with loss of control; missed periods; fainting, dizziness or palpitations; rapid weight change; marked fear of weight gain | recovery-habits.md "Warning signs that warrant referral" | the same as a positive screen (/checkin sets `scoff_positive true`); GP or eating-disorder service | code once stored |
| Fainting or near-fainting, chest pain or palpitations, confusion, eating under about 500 kcal/day for 2+ days, vomiting several times a day, resting HR under 40, losing 1 kg or more a week while already thin | recovery-habits.md "Urgent medical red flags" | same-day urgent care; stop the plan until medically cleared | skill text |
| Low energy availability signs: lost or irregular periods, low libido, recurrent stress fractures, frequent illness, persistent fatigue, falling performance, obsessive food or weight concerns | nutrition.md "REDs: red flags and referral" | stop increasing the deficit or training load; sports-medicine physician | skill text |
| Fever, aches all over, unwell below the neck | recovery-habits.md "Fever and systemic illness: do not train" | no training until well (a head cold only: "Head cold: optional light training") | skill text |
| Very sore, weak, swollen muscles with dark urine after training | recovery-habits.md "Recognise it and send to urgent care" | urgent care now | skill text |
| In pregnancy: bleeding, fluid leakage, contractions, headache, dizziness, chest pain, calf pain or swelling, unusual breathlessness at rest, the baby moving less | recovery-habits.md "Warning signs to stop exercise" | end the session; midwife or obstetrician the same day; urgent care for bleeding, fluid gushing, chest pain, regular painful contractions or a swollen, painful calf | skill text |
| After birth: calf pain or swelling, chest pain, breathlessness or fainting; other postpartum red flags | recovery-habits.md "Postpartum red flags" | urgent care for the first group; otherwise pause moderate-to-vigorous training until a primary-care provider clears it | skill text |
| GLP-1 user with persistent vomiting, very low intake, dizziness, signs of restrictive eating, very rapid weight loss or pregnancy plans | nutrition.md "GLP-1 users: protein, training and red flags" | refer back to the prescriber; never advise on doses | skill text (pregnancy plans: code) |
| Back or leg pain with saddle, genital or anal numbness, new bladder or bowel problems, new sexual dysfunction, or numbness or weakness in both legs | recovery-habits.md "Cauda equina red flags: emergency" | emergency care the same day, no training | skill text |
| A sudden snap at the back of the heel with weak push-off; an acute ankle or knee injury | recovery-habits.md "Suspected Achilles rupture", "Ankle roll: Ottawa ankle rules", "Knee injury: Ottawa knee rule" | stop; same-day assessment, or imaging as the rule says | skill text |
| Daytime sleepiness with at least two of loud snoring, witnessed breathing pauses or gasping, diagnosed high BP | recovery-habits.md "Possible sleep apnoea: suggest a doctor" | suggest a doctor | skill text |

Chest pain at rest, fainting, or chest pain with breathlessness and sweating: tell the client to
call emergency services now (`emergency_number` from `coach safety`), before anything else.

## What protects what

- **Code:** the calorie floors, every deficit and surplus block, the weigh-in and body-log
  refusal, zone methods and caps (the vigorous and near-maximal zones held back by the same
  caps, including until the review; `coach runs week` still reports minutes logged in them, with
  the cap's reason, so a review can see them), the
  progression hold, the injury pause and the no-training stop. `mealplan check` and `save` also
  flag menu items that match a recorded allergy or intolerance and refuse to save them, but the
  match is by name only (no synonyms or hidden ingredients), so it is a safety net, not a
  guarantee: the skill still asks about allergies and reads labels. Tests in
  `tests/coach/` cover each row of the flags table, and the dry runs in `docs/examples/` show
  three end to end (positive screen, cardiac symptoms, PAR-Q+ follow-up YES).
- **Skill text:** asking the screening questions, recognising red flags in conversation, naming
  the professional and the deferral line, recording injuries the client mentions, and keeping
  vigorous modalities (HIIT, sprints, jump rope, plyometrics) out of a plan while
  `review_before_vigorous` or `no_all_out_sprints` says so: the code knows the flags but not
  which modality a plan prescribes. These depend on the model following the skill; the
  dry runs check them, but code does not guarantee them.
