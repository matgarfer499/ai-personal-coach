# /plan dry run: shoulder injury, with a professional (lift `paused`, load is a ceiling)

The client is synthetic ("Marco", invented for this run; no real data). Run date: 2026-11-02 (a Monday). `DATA` is a fresh folder made with `mktemp -d`; the real path printed by the CLI is shown as `DATA`. Four weeks of invented workouts (12 sessions, two alternating full-body sessions A and B, last logged session 2026-10-30) were imported with `coach import`, and the profile was set with `coach profile set` (english, muscle_gain, intermediate, no medication, every screen clear, no injury yet). The knowledge sections are shortened to heading, the start of the Rule line and Grade; the CLI prints more. Every other output is the CLI's, copied exactly.

The point of the run: the same shoulder as in `plan-injury-no-professional.md`, but a physiotherapist has assessed it, so `/plan` records it with `coach injury add shoulder --professional physiotherapist --exercises "Bench Press"`. The lift must come back `paused`, with `load_kg` as a ceiling, must not be progressed, and must be swapped or reduced within the limits the physiotherapist set. Because a professional manages it, `coach safety` does not set `refer_gp` for the injury, so there is no deferral line (see "What the replay shows").

## The run

**Client:** Can you write me a new plan for the next block?

**Coach:** Sure. First I look at your profile, your safety checks and your training history.

```
$ uv run python -m coach --data-dir DATA safety --json
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": false, "prescriber_owns_weight": false, "refer_gp": false, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": false, "review_before_vigorous": false, "no_all_out_sprints": false, "emergency_number": "112", "paused_exercises": {}, "reasons": []}

$ uv run python -m coach --data-dir DATA profile show --json
{"data_dir": "DATA", "profile": {"sex": "male", "birth_date": "1990-06-02", "height_cm": 178.0, "weight_kg": 82.0, "goal": "muscle_gain", "experience": "intermediate", "activity_level": "desk", "pal_override": null, "language": "en", "region": "es", "emergency_number": null, "medications": [], "conditions": [], "screening": {"scoff_yes_count": 0, "scoff_positive": false, "parq_any_yes": false, "parq_followup_yes": false, "cardiac_symptoms": false}, "injuries": [], "research_reminder_months": 6}, "missing": ["emergency_number"], "unrecognised": {"medications": [], "conditions": []}}

$ uv run python -m coach --data-dir DATA knowledge stale --json
{"months": 6, "stale": []}

$ uv run python -m coach --data-dir DATA energy --json
{"rmr": 1757.5, "tdee": 2548.38, "target": {"kcal": 2676, "maintenance": 2548.38, "deficit": -128, "clamped": false, "notes": ["nutrition.md: \"Recalibrate TDEE from the weight trend\": starting estimate, recalibrate after 2-4 weeks of weigh-ins"]}}

$ uv run python -m coach --data-dir DATA macros --kcal 2676 --json
{"in_deficit": false, "kcal": 2676.0, "protein_g": 131.2, "fat_g": 74.33, "fat_min_g": 59.47, "carbs_g": 370.55, "fibre_g": 25, "protein_g_per_kg": 1.6, "notes": ["nutrition.md: \"Daily protein target for people who lift\": 1.6 g/kg/day"]}

$ uv run python -m coach --data-dir DATA zones --json
{"method": "hrmax", "zones": [{"name": "light", "rpe": [9, 11], "talk_test": "can talk and sing", "bpm": [104, 115]}, {"name": "moderate", "rpe": [12, 13], "talk_test": "can talk, but not sing", "bpm": [117, 139]}, {"name": "vigorous", "rpe": [14, 17], "talk_test": "only a few words without pausing for breath", "bpm": [141, 174]}], "hr_max": 183, "hr_max_source": "tanaka", "hr_rest": null, "notes": ["cardio-health.md: \"ACSM intensity bands\": zones are approximate; check them against RPE and the talk test", "cardio-health.md: \"HRmax: formulas and setting the anchor\": HRmax from Tanaka is a rough start and can be off by 20+ bpm; use an observed all-out peak when you have one"]}

$ uv run python -m coach --data-dir DATA strength sets --json
{"week": {"start": "2026-10-24", "end": "2026-10-30"}, "sets": {"hamstrings": 6.0, "glutes": 4.5, "front_delts": 7.5, "triceps": 4.5, "back": 6.0, "biceps": 3.0, "rear_delts": 3.0, "quads": 3.0, "adductors": 1.5, "chest": 3.0}, "unmapped": ["Barbell Row"], "reference_sets_per_week": 10}

$ uv run python -m coach --data-dir DATA strength progress --json
{"lifts": {"Barbell Row": {"action": "add_reps", "load_kg": 62.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Bench Press": {"action": "increase_load", "load_kg": 69.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": every work set beat 12 reps, add 2.5% or the smallest practical jump"]}, "Lat Pulldown": {"action": "add_reps", "load_kg": 57.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Overhead Press": {"action": "add_reps", "load_kg": 40.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Romanian Deadlift": {"action": "add_reps", "load_kg": 77.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Squat": {"action": "add_reps", "load_kg": 87.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}}, "unmatched_rep_ranges": [], "rep_ranges_outside_lookback": []}

$ read the last logged session of each lift from DATA/sessions.csv
2026-10-28 Squat: 87.5 kg x 12, 12, 11
2026-10-28 Bench Press: 67.5 kg x 13, 13, 13
2026-10-28 Barbell Row: 62.5 kg x 12, 12, 11
2026-10-30 Romanian Deadlift: 77.5 kg x 12, 12, 11
2026-10-30 Overhead Press: 40.0 kg x 12, 12, 11
2026-10-30 Lat Pulldown: 57.5 kg x 12, 12, 11
```

**Coach:** (`no_training` is false, no flag is set, no stale knowledge. Loading the knowledge that applies: the always-rules and goal muscle_gain. Not novice, not 65+, no beta-blocker, no hypertension, not pregnant, no GLP-1. No injury is recorded yet; I ask about it below, and load the injury rules if there is one.)

```
$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Weekly sets per muscle (dose-response)"
### Weekly sets per muscle (dose-response)
**Rule:** For a client whose priority is muscle gain and who has time, move each major muscle toward roughly 10 or more hard weekly sets over time, split over 2 or more sessions, counting sets with the fractional rule (see "Default counting rule: direct 1, indirect 0.5"). Treat 10 as a better-than-lower reference point, not a ...
**Grade:** strong

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Frequency for hypertrophy"
### Frequency for hypertrophy
**Rule:** Choose how often to train each muscle by schedule, recovery and preference. Use frequency to fit in the weekly volume, not as a goal in itself. Splitting volume across 2 or more sessions is practical once one session would need too many sets for one muscle.
**Grade:** strong

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Full-body versus split"
### Full-body versus split
**Rule:** Let the client pick full-body, upper/lower or another split based on available days and enjoyment. For 2-3 days per week, full-body sessions are the simplest way to hit each muscle twice. Check that weekly sets per muscle are covered whichever split is chosen.
**Grade:** moderate

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Target reps in reserve"
### Target reps in reserve
**Rule:** Prescribe most working sets at about 1-3 RIR for hypertrophy and 1-4 RIR for strength-focused heavy sets. Warm-up and technique sets do not count as working sets. A set ended with 5+ RIR is probably too easy for hypertrophy.
**Grade:** moderate

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Double progression"
### Double progression
**Rule:** Use double progression. Pick a rep range (for example 8-12). When the client beats the top of the range by 1-2 reps on all work sets at the target RIR, add the smallest practical increment within about 2-10% (smaller jumps for upper-body and isolation lifts, larger for big lower-body lifts). Adding reps or sets at the ...
**Grade:** moderate

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Load range for hypertrophy"
### Load range for hypertrophy
**Rule:** For a hypertrophy or body-composition goal, let the client choose loads anywhere from about 6 to 30 reps per set based on preference, joint comfort and equipment. Default to moderate loads (about 6-15 reps). Light loads work only if the set ends close to failure.
**Grade:** strong

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Load range for maximal strength"
### Load range for maximal strength
**Rule:** If the client wants to get stronger, include regular heavier work in the 3-8 rep range (about 75-85%+ 1RM) on main lifts once technique is solid. Beginners make large gains with moderate loads at first; introduce heavier sets gradually as technique becomes consistent (a coaching choice, often after the first several ...
**Grade:** strong

$ uv run python -m coach --data-dir DATA knowledge section cardio-health "Weekly baseline dose"
### Weekly baseline dose
**Rule:** Default weekly health baseline for every client: 150-300 min of moderate cardio, or 75-150 min vigorous, or a mix (1 vigorous minute counts as about 2 moderate minutes), plus at least 2 full-body strength sessions. Use 150 moderate or 75 vigorous min as the minimum and push toward 300/150 when the client has time. Gym ...
**Grade:** strong

$ uv run python -m coach --data-dir DATA knowledge section nutrition "Surplus size for muscle gain"
### Surplus size for muscle gain
**Rule:** For muscle gain, use a modest surplus (about 5-20% above maintenance, not above about 20%) and aim for about 0.25-0.5% of body weight per week. Beginners and returning lifters can sit near the top, advanced lifters near the bottom; start at the lower end, because prescribed surpluses tend to drift upward. Expect a ...
**Grade:** emerging
```

**Coach:** That is what I need from your profile. To build the week: which days and how much time do you have, what equipment, which exercises do you like or dislike, and any injury or pain?

**Client:** Monday, Wednesday and Friday at 18:30, one hour, full gym. I walk on Tuesday, Thursday and Saturday. My right shoulder has hurt since Thursday last week, a dull ache when I press, mostly on the bench. I saw a physiotherapist on Friday.

**Coach:** Thanks for telling me. Does the overhead press or anything else bother it? What did the physiotherapist say, and did they set any limits?

**Client:** Only the bench. The overhead press feels fine. The physiotherapist says no barbell bench pressing for now, push-ups and pain-free work are fine, and they will tell me when I can press heavy again.

**Coach:** (Injuries are never delegated, so I record it. The logged name of the lift is "Bench Press". A physiotherapist assessed and manages it, so `--professional physiotherapist`. Then I rerun the reads that the injury changes.)

```
$ uv run python -m coach --data-dir DATA injury add shoulder --since 2026-10-29 --professional physiotherapist --exercises 'Bench Press' --json
{"injuries": [{"area": "shoulder", "status": "active", "since": "2026-10-29", "professional": "physiotherapist", "exercises": ["Bench Press"]}], "unmatched": []}

$ uv run python -m coach --data-dir DATA safety --json
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": false, "prescriber_owns_weight": false, "refer_gp": false, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": false, "review_before_vigorous": false, "no_all_out_sprints": false, "emergency_number": "112", "paused_exercises": {"Bench Press": {"reasons": ["recovery-habits.md: \"Some pain during exercise is acceptable in chronic, assessed pain\": shoulder injury, managed by physiotherapist: no progression; reduce or swap the lift within the limits physiotherapist set, who decides when it progresses"], "assessed": true}}, "reasons": ["recovery-habits.md: \"Some pain during exercise is acceptable in chronic, assessed pain\": shoulder injury, managed by physiotherapist: no progression; reduce or swap the lift within the limits physiotherapist set, who decides when it progresses"]}

$ uv run python -m coach --data-dir DATA strength progress --json
{"lifts": {"Barbell Row": {"action": "add_reps", "load_kg": 62.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Bench Press": {"action": "paused", "load_kg": 67.5, "rep_range": [8, 12], "reasons": ["recovery-habits.md: \"Some pain during exercise is acceptable in chronic, assessed pain\": shoulder injury, managed by physiotherapist: no progression; reduce or swap the lift within the limits physiotherapist set, who decides when it progresses"]}, "Lat Pulldown": {"action": "add_reps", "load_kg": 57.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Overhead Press": {"action": "add_reps", "load_kg": 40.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Romanian Deadlift": {"action": "add_reps", "load_kg": 77.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Squat": {"action": "add_reps", "load_kg": 87.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}}, "unmatched_rep_ranges": [], "rep_ranges_outside_lookback": []}

$ uv run python -m coach --data-dir DATA injury list --json
{"injuries": [{"area": "shoulder", "status": "active", "since": "2026-10-29", "professional": "physiotherapist", "exercises": ["Bench Press"]}], "unmatched": []}

$ uv run python -m coach --data-dir DATA energy --json
{"rmr": 1757.5, "tdee": 2548.38, "target": {"kcal": 2676, "maintenance": 2548.38, "deficit": -128, "clamped": false, "notes": ["nutrition.md: \"Recalibrate TDEE from the weight trend\": starting estimate, recalibrate after 2-4 weeks of weigh-ins", "recovery-habits.md: \"Some pain during exercise is acceptable in chronic, assessed pain\": shoulder injury, managed by physiotherapist: no progression; reduce or swap the lift within the limits physiotherapist set, who decides when it progresses"]}}

$ uv run python -m coach --data-dir DATA macros --kcal 2676 --json
{"in_deficit": false, "kcal": 2676.0, "protein_g": 131.2, "fat_g": 74.33, "fat_min_g": 59.47, "carbs_g": 370.55, "fibre_g": 25, "protein_g_per_kg": 1.6, "notes": ["nutrition.md: \"Daily protein target for people who lift\": 1.6 g/kg/day"]}
```

**Coach:** (Bench Press is `paused` with `load_kg` 67.5: no progression, and 67.5 is a ceiling, not a target. The physiotherapist said no barbell bench for now, so I swap the lift rather than reduce it; the CLI prints no reduced load and I do not invent one. The other lifts keep their `add_reps` loads. `refer_gp` is false, so no deferral line; the professional is the physiotherapist. Loading the injury rules.)

```
$ uv run python -m coach --data-dir DATA knowledge section recovery-habits "Some pain during exercise is acceptable in chronic, assessed pain"
### Some pain during exercise is acceptable in chronic, assessed pain
**Rule:** With chronic, stable musculoskeletal pain (more than 3 months, no red flags, already assessed), the goal is not zero pain. Allow mild, tolerable pain during exercise as long as it settles fairly quickly and does not progressively worsen across sessions. If pain flares and stays elevated, reduce load or volume; keep ...
**Grade:** moderate

$ uv run python -m coach --data-dir DATA knowledge section recovery-habits "Acute sprains and strains: protect briefly, then load"
### Acute sprains and strains: protect briefly, then load
**Rule:** For a sprain or strain with no red flags: protect it for 1-3 days (reduce load, no long immobilisation), compress and elevate, and explain the expected recovery. Then reintroduce pain-guided loading and keep cardio going with other body parts. Do not forbid ice if it relieves pain, but do not present it as a healing ...
**Grade:** moderate

$ uv run python -m coach --data-dir DATA knowledge section recovery-habits "Muscle strain: early pain-guided loading"
### Muscle strain: early pain-guided loading
**Rule:** After a mild-moderate muscle strain with no red flags, start gentle pain-guided loading within the first days (isometrics, then light ranges) rather than resting for weeks. Allow mild discomfort that settles quickly and progress when the previous step is tolerated. Return to heavy or explosive lifting of that muscle ...
**Grade:** emerging
```

**Coach:** (The bench is swapped for push-ups, the one press they allowed, which is bodyweight so there is no load to invent, and the rest of the body keeps training [Acute sprains and strains: protect briefly, then load]. Cardio starts at the 150-minute minimum, split evenly over the three walking days. Writing `DATA/plan.md`.)

```
$ cat > DATA/plan.md   (file written; content identical to the final message below, including the review line)
```

**Coach (final message):**

Date: 2026-11-02
target_kcal: 2676.0
in_deficit: false
training_schedule: mon 18:30; wed 18:30; fri 18:30

## Training week

Three full-body sessions of one hour at the gym, Monday, Wednesday and Friday at 18:30, as a rotation A, B, A, B, A, B [Weekly baseline dose] [Full-body versus split]. Your last session was B, so Monday is A. If you miss one, carry on with the next one in the rotation; do not double up.

**The barbell bench press is out of the plan for now.** Your right shoulder has hurt on it since 2026-10-29. Your physiotherapist manages it and said no barbell bench for now, so it does not progress and I do not load it; they decide when it comes back [Some pain during exercise is acceptable in chronic, assessed pain]. The rest of your body keeps training [Acute sprains and strains: protect briefly, then load].

**Session A (Monday, then Friday on alternate weeks)**
- Squat: 87.5 kg, 3 sets of 8-12 reps
- Push Up (in place of the bench press, as your physiotherapist allowed): 3 sets of 8-12 reps, stopping 2-3 reps before you would fail. Stop if it brings the shoulder pain on, and tell me.
- Barbell Row: 62.5 kg, 3 sets of 8-12 reps

**Session B (Wednesday)**
- Romanian Deadlift: 77.5 kg, 3 sets of 8-12 reps
- Overhead Press: 40.0 kg, 3 sets of 8-12 reps. This one feels fine for you today. If it starts to hurt the shoulder, stop it and tell me so I can record it too.
- Lat Pulldown: 57.5 kg, 3 sets of 8-12 reps

Loads for the lifts that stay are the ones the command gives: same load, add reps until every set beats 12, then I raise it [Double progression]. 2-3 reps in reserve (RIR) on working sets, never to failure [Target reps in reserve]. Your sets per muscle stay near what you log now [Weekly sets per muscle (dose-response)].

## Cardio

Minimum 150 minutes of moderate cardio a week [Weekly baseline dose]: brisk walks on Tuesday, Thursday and Saturday, 50 minutes each. Intensity: perceived effort (RPE) 12-13, you can talk but not sing; about 117-139 bpm, a rough guide because the maximum heart rate behind it (183) is a formula estimate. Walking should not provoke the shoulder.

## Nutrition

Daily target (muscle-gain phase):
- Calories: 2676 kcal
- Protein: 131.2 g
- Fat: 74.33 g
- Carbohydrates: 370.55 g
- Fibre: 25 g

That is a surplus of 128 kcal over your estimated maintenance (2548.38 kcal) [Surplus size for muscle gain]. It is a starting estimate; weigh in and we recalibrate after 2-4 weeks [Recalibrate TDEE from the weight trend]. Protein: 1.6 g/kg/day [Daily protein target for people who lift].

## Safety notes

- Shoulder: follow your physiotherapist's limits. When they say the bench can come back, tell me what they allow (a load, a range, a date) and I will update the plan; I clear the injury only when they say it is cleared. Sharp or worsening pain, pain at rest or pins and needles: stop and go back to them [Some pain during exercise is acceptable in chronic, assessed pain].

## Rules used

[Weekly baseline dose], [Full-body versus split], [Weekly sets per muscle (dose-response)], [Target reps in reserve], [Double progression], [Some pain during exercise is acceptable in chronic, assessed pain], [Acute sprains and strains: protect briefly, then load], [Surplus size for muscle gain], [Recalibrate TDEE from the weight trend], [Daily protein target for people who lift].

Review the plan with /review every week.

## What the replay shows

Result: correct. With `--professional physiotherapist`, `coach strength progress` returned `"action": "paused"` for Bench Press with `load_kg` 67.5 (a ceiling, not a target), so the lift is not progressed; the plan swaps it for push-ups within the limits the client reported from the physiotherapist. `coach safety` lists it under `paused_exercises` with `assessed: true` and does not set `refer_gp` (the safety table: only an injury with no `professional` sets it), so there is no deferral line and the plan names the physiotherapist. The other lifts keep their `add_reps` loads.

Skill problems found (not fixed here; this PR changes no skill, code or test):

1. Same as in `plan-injury-no-professional.md`: the skill does not say to rerun `coach safety` and `coach strength progress` after `coach injury add`; the replay did.
2. "Reduce or swap the lift within the professional's limits" has no number source for a reduction: `load_kg` is only a ceiling and the skill forbids inventing loads, so a model that wants to keep the bench with a lighter load has nothing from the CLI to quote except "at or below 67.5 kg". The replay swapped to a bodyweight lift to avoid inventing a number. The professional's limits are also only what the client reports; nothing in the profile records them.
3. Nothing in the profile records what the physiotherapist said beyond the name in `professional`, so the next `/plan` or `/review` cannot see that the bench was swapped for push-ups because of a "no barbell bench" limit; the plan text is the only trace.
