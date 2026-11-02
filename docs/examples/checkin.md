# /checkin dry run

> **What is not verbatim:** CLI outputs are as the CLI printed them, except where shortened with `...` (long `knowledge section` and `profile set` outputs, cut to the part that matters) and where the scratch data folder path is shown as `DATA`. Commands are normalised for reading: `--json` is left out and quoting is added where a shell needs it. The dialogue is a simulation of a model following the skill, not a recording of a real conversation.

The client is synthetic (tests/skills/checkin/client.md); the run was done on 2026-11-02 with the current skill. DATA stands for the data directory (a copy of `tests/skills/state/`, used as `COACH_DATA_DIR`; the skill passes no `--data-dir`). The last check-in in the start state was 2026-10-18; the days in between are not filled in.

**Cliente:** Hola, check-in de hoy: 64,3 kg esta mañana, cintura 74 cm, ayer comí unas 1.750 kcal según la app y dormí 6 horas y media. Tengo un catarro, solo mocos, sin fiebre.

Step 1: safety first, every time.

```
$ coach safety
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": true, "prescriber_owns_weight": false, "refer_gp": false, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": false, "review_before_vigorous": true, "no_all_out_sprints": true, "emergency_number": "112", "paused_exercises": {}, "reasons": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}
```

```
$ coach profile show
{"data_dir": "DATA", "profile": {"sex": "female", "birth_date": "1992-03-14", "height_cm": 168.0, "weight_kg": 66.0, "goal": "fat_loss", "experience": "intermediate", "activity_level": "desk", "pal_override": null, "language": "es", "region": "es", "emergency_number": null, "medications": ["beta_blocker"], "conditions": ["hypertension"], "screening": {"scoff_positive": false, "parq_any_yes": true, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal", "bp_systolic": 132, "bp_diastolic": 84}, "injuries": [], "research_reminder_months": 6}, "missing": ["emergency_number"], "unrecognised": {"medications": [], "conditions": []}}
```

`no_weight_targets` is not set, so weight can be asked for and recorded. The profile language is es. The `notes` column of the last 7 days (2026-10-27 to 2026-11-02: no rows in that window, the last row is 2026-10-18) is empty, so the weekly questions have not been asked: period (she is a woman, not pregnant) and blood pressure (`hypertension`). Knowledge loaded for what follows:

```
$ coach knowledge section nutrition "Read the scale with weekly averages"
### Read the scale with weekly averages
**Rule:** Never adjust calories from one or two weigh-ins. Daily weighing is optional; weekly is acceptable. Weigh under standard conditions (morning, after the toilet, before eating), use 7-day rolling averages ... or same-weekday comparisons, and compare weekly means across 2-4 weeks. ...
**Grade:** emerging
...
```

```
$ coach knowledge section nutrition "Menstrual dysfunction: stop and refer"
### Menstrual dysfunction: stop and refer
**Rule:** Ask women who diet or train hard about their cycle at the start and regularly, and about hormonal contraception, which masks it. Any new missed or irregular period during dieting or heavy training: ask about intake, recommend a GP visit and stop increasing the deficit. Periods absent for 3 months or more, or fewer than 6 a year: stop the deficit, move to maintenance or a small surplus ... and refer to a physician or gynaecologist/endocrinologist. ...
**Grade:** moderate
...
```

```
$ coach knowledge section recovery-habits "Resting BP thresholds to defer or refer"
### Resting BP thresholds to defer or refer
**Rule:** ... A band applies when either number reaches it. At 200 systolic or higher, or 110 diastolic or higher: no exercise ... At 180-199 systolic: no training until reviewed by a GP. At 160-179 systolic or 90-109 diastolic, or with BP unknown in someone with known or suspected hypertension: GP review before starting a programme or progressing an existing one ... At 140-159 systolic with diastolic below 90: train at moderate intensity and recommend a GP check.
**Grade:** emerging
...
```

```
$ coach knowledge section recovery-habits "Head cold: optional light training"
### Head cold: optional light training
**Rule:** With head-cold symptoms only (runny or blocked nose, mild sore throat) and no fever, allow optional light-to-moderate training (RPE 5 or less, shorter session, no maximal efforts or PRs). Stop if the person feels worse. Avoid the gym if contagious, out of courtesy. Any below-the-neck or systemic symptom (fever, chills, body aches, chest tightness, productive cough, diarrhoea, marked fatigue) means rest (next rule).
**Grade:** emerging
...
```

Weight, waist, kcal and sleep are already given, so nothing is missing for step 2. Step 3 and step 4 need answers.

**Coach:** Gracias, Lucía, ya tengo peso, cintura, kcal y sueño. Para cerrar el check-in de hoy me faltan unas preguntas de control, todas con sí o no salvo la tensión y la regla:

1. Aparte de los mocos, ¿tienes fiebre, escalofríos, dolores musculares por todo el cuerpo o malestar general por debajo del cuello?
2. ¿Has notado dolor o presión en el pecho, cuello, mandíbula o brazo, falta de aire en reposo, mareos, desmayos o palpitaciones?
3. ¿Después de entrenar, músculos muy doloridos, débiles o hinchados, o la orina muy oscura (color té o cola)?
4. Con la hipertensión: ¿cuál fue tu última tensión, sentada y tras 5 minutos de reposo?
5. ¿Algún cambio nuevo en la regla (retraso, falta o irregularidad)?
6. ¿Cómo fue el entrenamiento de ayer?

**Cliente:**
1. No tengo fiebre, ni dolores musculares, ni malestar por debajo del cuello.
2. No, nada de dolor en el pecho, mareos, desmayos, falta de aire en reposo ni palpitaciones.
3. No lo sé.
4. Me la tomé ayer, sentada tras 5 minutos de reposo: 138/86.
5. Este mes me vino 12 días tarde y el anterior también se retrasó; antes era muy regular. Es nuevo para mí.
6. Ayer piernas, bien.

Answer 3 is "not sure": the skill says to describe the sign once more in plain words.

**Coach:** Te lo explico de otra forma: a veces, tras un entrenamiento fuerte, los músculos se ponen tan hinchados, duros y doloridos que cuesta estirar bien una pierna, y la orina sale del color del té fuerte o de la cola. Eso es distinto de las agujetas normales. ¿Te ha pasado algo así tras las piernas de ayer?

**Cliente:** No lo sé.

Still unsure after the second description, so the sign is treated as absent and the coach will tell her what to do if it appears.

Her blood pressure (138/86, seated after 5 minutes) is below every band in the rule (needs 140 systolic or 90 diastolic), so it is stored. Then the safety flags are rerun:

```
$ coach profile set screening.bp_systolic 138
... "screening": {"scoff_positive": false, "parq_any_yes": true, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal", "bp_diastolic": 84, "bp_systolic": 138} ... "missing": ["emergency_number"], "unrecognised": {"medications": [], "conditions": []}}
$ coach profile set screening.bp_diastolic 86
... "screening": {"scoff_positive": false, "parq_any_yes": true, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal", "bp_systolic": 138, "bp_diastolic": 86} ... "missing": ["emergency_number"], "unrecognised": {"medications": [], "conditions": []}}
$ coach safety
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": true, "prescriber_owns_weight": false, "refer_gp": false, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": false, "review_before_vigorous": true, "no_all_out_sprints": true, "emergency_number": "112", "paused_exercises": {}, "reasons": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}
```

The period is new in a cycle that was regular: `irregular_new`.

```
$ coach profile set screening.menstrual irregular_new
... "screening": {"scoff_positive": false, "parq_any_yes": true, "parq_followup_yes": false, "cardiac_symptoms": false, "bp_systolic": 138, "bp_diastolic": 86, "menstrual": "irregular_new"} ... "missing": ["emergency_number"], "unrecognised": {"medications": [], "conditions": []}}
$ coach safety
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": true, "use_rpe_not_hr": true, "prescriber_owns_weight": false, "refer_gp": true, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": false, "review_before_vigorous": true, "no_all_out_sprints": true, "emergency_number": "112", "paused_exercises": {}, "reasons": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "nutrition.md: \"Menstrual dysfunction: stop and refer\": new irregular periods, stop increasing the deficit", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}
```

`refer_gp` is now set (new reason: menstrual dysfunction), so the answer ends with the deferral line. No step 3 red flag fired; it is a head cold only and `no_training` is not set, so light training is optional. Record the day (weight, waist, yesterday's kcal, last night's sleep, notes from step 3 and 4), then the trend:

```
$ coach checkin add --weight 64.3 --waist 74 --intake 1750 --sleep 6.5 --notes "catarro sin fiebre; ayer piernas, bien; regla: retrasos nuevos; TA 138/86"
{"date": "2026-11-02", "weight_kg": 64.3, "waist_cm": 74.0, "intake_kcal": 1750.0, "sleep_hours": 6.5, "notes": "catarro sin fiebre; ayer piernas, bien; regla: retrasos nuevos; TA 138/86"}
```

```
$ coach trend
{"status": "ok", "rate_kg_week": -0.19, "rate_pct_week": -0.29, "weight_kg": 64.3, "points": 14, "days": 28, "start": "2026-10-06", "end": "2026-11-02", "can_recalibrate": true, "notes": [], "recalibrated_tdee": 1804.82}
```

Only `status` and `rate_kg_week` are reported.

**Coach (final message):**

Regla nueva: este mes y el anterior se te ha retrasado, y antes era muy regular. Eso es un cambio nuevo que conviene que vea tu médico de cabecera o tu ginecólogo/a, y mientras tanto no vamos a aumentar el déficit (nutrition.md: "Menstrual dysfunction: stop and refer"). Si más adelante aparece dolor o presión en el pecho, falta de aire en reposo, desmayo, orina oscura tras entrenar o músculos muy hinchados y doloridos, para de entrenar y pide atención médica el mismo día (112 si es dolor de pecho en reposo o desmayo).

- Registrado hoy: 64,3 kg, cintura 74 cm, 1750 kcal de ayer, 6,5 h de sueño, catarro sin fiebre, tensión 138/86 y el cambio en la regla.
- Tendencia del peso: estado `ok`, -0,19 kg por semana.
- Con solo mocos y sin fiebre, entrenar suave es opcional: esfuerzo 5 o menos, sesión más corta, sin esfuerzos máximos, y para si te encuentras peor (recovery-habits.md: "Head cold: optional light training"). Con betabloqueante, el esfuerzo se mide por sensaciones y prueba del habla, no por pulsaciones (cardio-health.md: "Beta-blockers: no formula-based HR zones"). Y, como dijiste SÍ en el PAR-Q+, nada de esfuerzos máximos ni intensos (HIIT, esprints a tope) hasta que los revise una persona cualificada en ejercicio o un médico (recovery-habits.md: "PAR-Q+ specific thresholds").

Esto es orientación general de un entrenador automatizado, no consejo médico. Por lo que me has contado, habla con tu médico (o con el profesional que te indico arriba) antes de ponerlo en práctica.
