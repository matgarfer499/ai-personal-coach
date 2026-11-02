# /review dry run

> **What is not verbatim:** CLI outputs are as the CLI printed them, except where shortened with `...` (long `knowledge section` and `profile set` outputs, cut to the part that matters) and where the scratch data folder path is shown as `DATA`. Commands are normalised for reading: `--json` is left out and quoting is added where a shell needs it. The dialogue is a simulation of a model following the skill, not a recording of a real conversation.

The client is synthetic (tests/skills/review/client.md). Run date: 2026-11-02, reviewing the week ending 2026-10-18, with the current skill. DATA is a copy of `tests/skills/state/` plus the imported `workouts.csv`, used as `COACH_DATA_DIR`; the skill passes no `--data-dir`. There is no `plan.md`, so no `--rep-range` is passed.

**Cliente:** ¿Hacemos la revisión de la semana?

**Coach:** (lee los datos; como el fin de semana, 2026-10-18, es anterior a hoy, `trend`, `strength progress` y `energy` llevan `--today 2026-10-18`; `energy` solo se ejecuta si hay que proponer un cambio de calorías)

```
$ coach safety
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": true, "prescriber_owns_weight": false, "refer_gp": false, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": false, "review_before_vigorous": true, "no_all_out_sprints": true, "emergency_number": "112", "paused_exercises": {}, "reasons": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}

$ coach profile show
{"data_dir": "DATA", "profile": {"sex": "female", "birth_date": "1992-03-14", "height_cm": 168.0, "weight_kg": 66.0, "goal": "fat_loss", "experience": "intermediate", "activity_level": "desk", "pal_override": null, "language": "es", "region": "es", "emergency_number": null, "medications": ["beta_blocker"], "conditions": ["hypertension"], "screening": {"scoff_positive": false, "parq_any_yes": true, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal", "bp_systolic": 132, "bp_diastolic": 84}, "injuries": [], "research_reminder_months": 6}, "missing": ["emergency_number"], "unrecognised": {"medications": [], "conditions": []}}

$ coach knowledge stale
{"months": 6, "stale": []}

$ coach --today 2026-10-18 trend
{"status": "ok", "rate_kg_week": -0.42, "rate_pct_week": -0.65, "weight_kg": 64.59, "points": 28, "days": 28, "start": "2026-09-21", "end": "2026-10-18", "can_recalibrate": true, "notes": [], "recalibrated_tdee": 2049.52}

$ coach strength sets --week-ending 2026-10-18
{"week": {"start": "2026-10-12", "end": "2026-10-18"}, "sets": {"quads": 6.0, "glutes": 4.5, "adductors": 3.0, "chest": 6.0, "triceps": 4.5, "front_delts": 6.0, "back": 6.0, "biceps": 3.0, "rear_delts": 3.0, "hamstrings": 6.0}, "unmapped": [], "reference_sets_per_week": 10}

$ coach --today 2026-10-18 strength progress
{"lifts": {"Curl femoral": {"action": "add_reps", "load_kg": 30.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Jalón al pecho": {"action": "add_reps", "load_kg": 35.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Peso muerto rumano": {"action": "add_reps", "load_kg": 50.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Prensa de piernas": {"action": "add_reps", "load_kg": 100.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Press banca": {"action": "stalled", "load_kg": 40.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"When progress stalls\": no gain in load or reps for 3 sessions; check effort and weekly sets (10+), then add 10-20% more sets for this muscle"]}, "Press militar": {"action": "add_reps", "load_kg": 25.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Remo con barra": {"action": "add_reps", "load_kg": 40.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}, "Sentadilla": {"action": "add_reps", "load_kg": 60.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Double progression\": same load, add reps until every set beats 12"]}}, "unmatched_rep_ranges": [], "rep_ranges_outside_lookback": []}

$ cat DATA/checkins.csv        (rows of the week 2026-10-12 to 2026-10-18; sleep_hours column)
2026-10-12: sleep 7   2026-10-13: 7   2026-10-14: 7   2026-10-15: 7   2026-10-16: 6   2026-10-17: 7   2026-10-18: 7
(earlier rows also mostly 7, a few 6)

$ ls DATA            (no plan.md)
checkins.csv  profile.yaml  sessions.csv
```

Knowledge loaded (trimmed to the rule text the coach used):

```
$ coach knowledge section nutrition "Recalibrate TDEE from the weight trend"
### Recalibrate TDEE from the weight trend
**Rule:** Start from equation × conservative multiplier. ... After 4 or more weeks, compute observed TDEE ... and replace the equation estimate with it. Adjust intake in steps of about 100-200 kcal/d and re-check after another 2-4 weeks. ...
**Grade:** moderate
...

$ coach knowledge section nutrition "Read the scale with weekly averages"
### Read the scale with weekly averages
**Rule:** Never adjust calories from one or two weigh-ins. ... compare weekly means across 2-4 weeks. ...
**Grade:** emerging
...

$ coach knowledge section strength-hypertrophy "When progress stalls"
### When progress stalls
**Rule:** Treat a lift as stalled when load or reps have not increased for about 3 consecutive sessions or weeks ... first check that work sets are genuinely hard ... and that the muscle gets at least 10 hard weekly sets, then try a modest increase of about 10-20% over current weekly sets ...
**Grade:** moderate
...

$ coach knowledge section recovery-habits "Simple readiness monitoring"
### Simple readiness monitoring
**Rule:** Default monitoring ... session-RPE ... a 4-5 item pre-session wellness check ... Compare each person against their own rolling baseline. ...
**Grade:** moderate
...

$ coach knowledge section nutrition "Rate of loss for lean, trained clients"
### Rate of loss for lean, trained clients
**Rule:** For lean, trained clients who want to keep muscle, aim for about 0.5-1% of body weight per week, moving toward the slower end as they get leaner. ...
**Grade:** emerging
**Applies to:** Lean, mostly young male competitors. Generalising to ordinary gym-goers is an extrapolation.
...
```

(Objetivo fat_loss: se cargó la regla de ritmo de pérdida. La regla "Deloads" se carga después, cuando haya alguna señal de recuperación.)

**Coach:** Vale, empecemos. Tres preguntas rápidas:
1. ¿Cuántas de las sesiones planificadas hiciste esta semana?
2. ¿Cómo de cerca comiste del objetivo?
3. ¿Cuáles de estas cosas llevan 1-2 semanas contigo? Estancamiento en el rendimiento, molestias en las articulaciones, sueño malo, poca motivación, rendimiento que baja aunque descanses, ánimo bajo.

**Cliente:** Hice las 3 sesiones y la comida la he cumplido casi todos los días. Desde hace unas dos semanas duermo peor, unas 6 horas, y me molestan un poco las rodillas al entrenar. La motivación está bien, el rendimiento no ha bajado tras descansar y el ánimo está bien.

(Señales: `joint_aches`, `poor_sleep`, y `performance_stall` porque `coach strength progress` marca el press banca como `stalled`. Diferencia con los registros: ella dice 6 horas, los registros de la semana muestran sobre todo 7 y un día de 6; se usan ambos y se menciona. `knowledge stale` no lista archivos, así que no hay recordatorio de `/research stale`. Con señales de recuperación se carga "Deloads".)

```
$ coach knowledge section strength-hypertrophy "Deloads"
### Deloads
**Rule:** Do not prescribe routine deloads as a way to boost gains. Offer a reactive deload of about 1 week when two or more of these persist together for 1-2 weeks: performance stalls or drops on several lifts, persistent joint aches or soreness, poor sleep, low motivation. Keep the main exercises and reduce stress rather than stopping: as a coaching convention, cut volume (sets) by about 30-50% for one week, keep the loads, and stop 3 or more reps short of failure. ...
**Grade:** emerging
...

$ coach strength deload --signs performance_stall,joint_aches,poor_sleep
{"deload": {"volume_cut": [0.3, 0.5], "stop_rir": 3, "extra_rest_days": [0, 0], "reasons": ["strength-hypertrophy.md: \"Deloads\": 3 signs together; one lighter week, keep the loads"]}}
```

(Peso en calorías: la tendencia es `ok` y el ritmo, -0,65 % a la semana, cae dentro de 0,5-1 %, así que no se propone cambio de calorías y no se ejecuta `coach energy`. Solo se registra `recalibrated_tdee`.)

**Coach:** Te propongo esto, ¿te parece bien?
- Una semana de descarga: mismos pesos, recortar las series en torno a un 30-50 % (volume_cut 0,3-0,5), parar al menos 3 repeticiones antes del fallo y sin días de descanso extra. Motivo: coinciden tres señales (press banca estancado, molestias en las rodillas, sueño peor) [Deloads].
- Calorías: sin cambios, tu ritmo de pérdida está dentro del rango.

**Cliente:** Sí, acepto la semana de descarga.

(El script añade "acepta el nuevo objetivo de calorías", pero el coach no propuso ningún cambio de calorías, así que no hay nada que aceptar y no se escriben `target_kcal` ni `in_deficit`.)

```
$ mkdir -p DATA/reviews
$ (write) DATA/reviews/2026-10-18.md      (contenido más abajo)
```

## Mensaje final del coach

Como tomas un betabloqueante, no uso zonas de pulso por fórmula: el esfuerzo se guía por RPE y la prueba del habla [Beta-blockers: no formula-based HR zones].

Con tu SÍ en el PAR-Q+ no propongo trabajo intenso ni máximo (HIIT, esprints a tope, pruebas de una repetición máxima) hasta que lo revise una persona cualificada en ejercicio o un médico [recovery-habits.md: "PAR-Q+ specific thresholds"].

- **Adherencia:** 3 de 3 sesiones y la comida casi todos los días. Sueño: dices que duermes peor (6 horas) desde hace unas dos semanas; en los registros de la semana hay sobre todo 7 horas y algún día de 6. Uso ambos datos.
- **Peso:** tendencia ok, 64,59 kg; -0,42 kg/semana (-0,65 %/semana) en 28 días. Cae dentro de 0,5-1 % por semana [Rate of loss for lean, trained clients], aunque esa regla viene de competidores jóvenes y magros, así que aplicarla a ti es una extrapolación. Estás contenta con el ritmo.
- **Calorías:** TDEE recalibrado 2049,52 kcal, guardado en la revisión. Como el ritmo está dentro del rango, no propongo cambiar calorías [Recalibrate TDEE from the weight trend].
- **Entrenamiento:** series semanales: cuádriceps 6,0; glúteos 4,5; aductores 3,0; pecho 6,0; tríceps 4,5; hombro anterior 6,0; espalda 6,0; bíceps 3,0; hombro posterior 3,0; isquios 6,0. La referencia es 10 por semana, pero es una referencia para ganar músculo, no un mínimo; con pérdida de grasa bastan menos. Curl femoral 30,0 kg, jalón al pecho 35,0 kg, peso muerto rumano 50,0 kg, prensa de piernas 100,0 kg, press militar 25,0 kg, remo con barra 40,0 kg y sentadilla 60,0 kg: mismo peso y más repeticiones hasta superar 12 en todas las series [Double progression]. Press banca 40,0 kg: estancado, sin mejora de peso ni repeticiones en 3 sesiones [When progress stalls]; añadir series espera a después de la descarga.
- **Recuperación:** semana de descarga acordada: mismos pesos, series recortadas en torno a un 30-50 % (volume_cut 0,3-0,5), parar 3 repeticiones antes del fallo, sin días de descanso extra, y no añadir series [Deloads]. Si las rodillas siguen molestando después de la descarga, ve al médico de cabecera o a un fisioterapeuta.
- **Siguiente paso:** repite `/plan` para que la semana de descarga entre en tu plan.

## Contenido de DATA/reviews/2026-10-18.md

```
tdee_kcal: 2049.52

# Revisión de la semana que termina el 2026-10-18

Como tomas un betabloqueante, no uso zonas de pulso por fórmula: el esfuerzo se guía por RPE y la prueba del habla [cardio-health.md: "Beta-blockers: no formula-based HR zones"].

Con tu SÍ en el PAR-Q+ no propongo trabajo intenso ni máximo hasta que lo revise una persona cualificada en ejercicio o un médico [recovery-habits.md: "PAR-Q+ specific thresholds"].

- Adherencia: 3 de 3 sesiones y la comida casi todos los días. Sueño: dices que duermes peor (6 horas) desde hace unas dos semanas; en los registros de la semana hay sobre todo 7 horas y algún día de 6. Usamos ambos datos.
- Peso: tendencia ok, 64,59 kg; -0,42 kg/semana (-0,65 %/semana) sobre 28 días (2026-09-21 a 2026-10-18). Cae dentro de 0,5-1 % por semana [nutrition.md: "Rate of loss for lean, trained clients"], aunque esa regla viene de competidores jóvenes y magros, así que es una extrapolación a ti. Estás contenta con el ritmo.
- Calorías: TDEE recalibrado 2049,52 kcal (guardado arriba). El ritmo está dentro del rango, así que no propongo cambiar calorías [nutrition.md: "Recalibrate TDEE from the weight trend"].
- Entrenamiento: series semanales cuádriceps 6,0; glúteos 4,5; aductores 3,0; pecho 6,0; tríceps 4,5; hombro anterior 6,0; espalda 6,0; bíceps 3,0; hombro posterior 3,0; isquios 6,0 (referencia 10 por semana: es una referencia para ganar músculo, no un mínimo; con pérdida de grasa bastan menos). Curl femoral 30,0 kg, jalón al pecho 35,0 kg, peso muerto rumano 50,0 kg, prensa de piernas 100,0 kg, press militar 25,0 kg, remo con barra 40,0 kg y sentadilla 60,0 kg: mismo peso y más repeticiones hasta superar 12 en todas las series [strength-hypertrophy.md: "Double progression"]. Press banca 40,0 kg: estancado (sin mejora de carga ni repeticiones en 3 sesiones) [strength-hypertrophy.md: "When progress stalls"]; añadir series espera a después de la descarga.
- Recuperación: tres señales juntas (estancamiento, molestias en las rodillas, sueño peor) [strength-hypertrophy.md: "Deloads"]. Descarga de 1 semana: volume_cut 0,3-0,5 (recortar series en torno a 30-50 %), mismos pesos, parar 3 repeticiones antes del fallo, sin días de descanso extra. No añadir series esta semana. Si las rodillas siguen molestando después, médico de cabecera o fisioterapeuta.
- Siguiente paso: repetir /plan para incluir la semana de descarga.

## Cambios acordados

- Semana de descarga: aceptada.
- Calorías: sin cambio propuesto.
```
