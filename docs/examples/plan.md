# /plan dry run

> **What is not verbatim:** CLI outputs are as the CLI printed them, except where shortened with `...` (long `knowledge section` and `profile set` outputs, cut to the part that matters) and where the scratch data folder path is shown as `DATA`. Commands are normalised for reading: `--json` is left out and quoting is added where a shell needs it. The dialogue is a simulation of a model following the skill, not a recording of a real conversation.

El cliente es sintético (tests/skills/plan/client.md, "Lucía"; sin datos reales). Fecha de la ejecución: 2026-11-02, con la skill actual. DATA es una copia del estado inicial (profile.yaml, checkins.csv y sessions.csv ya importado; sin `plan.md` ni `reviews/`) usada como `COACH_DATA_DIR`; la skill no pasa `--data-dir`. Las salidas de `knowledge section` se recortan con `...` (solo fragmentos literales).

**Cliente:** ¿Me haces un plan para las próximas semanas?

**Coach:** Claro. Primero miro tu perfil, las comprobaciones de seguridad y tu historial de entrenamientos.

```
$ coach safety
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": true, "prescriber_owns_weight": false, "refer_gp": false, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": false, "review_before_vigorous": true, "no_all_out_sprints": true, "emergency_number": "112", "paused_exercises": {}, "reasons": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}

$ coach profile show
{"data_dir": "DATA", "profile": {"sex": "female", "birth_date": "1992-03-14", "height_cm": 168.0, "weight_kg": 66.0, "goal": "fat_loss", "experience": "intermediate", "activity_level": "desk", "pal_override": null, "language": "es", "region": "es", "emergency_number": null, "medications": ["beta_blocker"], "conditions": ["hypertension"], "screening": {"scoff_positive": false, "parq_any_yes": true, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal", "bp_systolic": 132, "bp_diastolic": 84}, "injuries": [], "research_reminder_months": 6}, "missing": ["emergency_number"], "unrecognised": {"medications": [], "conditions": []}}

$ coach knowledge stale
{"months": 6, "stale": []}
```

(No hay `data/reviews/` ni `data/plan.md`, así que el objetivo calórico sale de `coach energy`. `hold_deficit` es false, así que no hace falta `--current-kcal`. Sus notas no incluyen la nota `active` de `no_training`, así que no se pregunta por `pal_override`.)

```
$ coach energy
{"rmr": 1379.0, "tdee": 1999.55, "target": {"kcal": 1500, "maintenance": 1999.55, "deficit": 500, "clamped": false, "notes": ["nutrition.md: \"Recalibrate TDEE from the weight trend\": starting estimate, recalibrate after 2-4 weeks of weigh-ins", "cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}}

$ coach macros --kcal 1500 --in-deficit
{"in_deficit": true, "kcal": 1500.0, "protein_g": 132.0, "fat_g": 41.67, "fat_min_g": 33.33, "carbs_g": 149.25, "fibre_g": 25, "protein_g_per_kg": 2.0, "notes": ["nutrition.md: \"Protein during fat loss\": 2 g/kg/day"]}

$ coach zones
{"method": "rpe", "zones": [{"name": "light", "rpe": [9, 11], "talk_test": "can talk and sing", "bpm": null}, {"name": "moderate", "rpe": [12, 13], "talk_test": "can talk, but not sing", "bpm": null}], "hr_max": null, "hr_max_source": null, "hr_rest": null, "notes": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "cardio-health.md: \"RPE as the anchor under beta-blockade\": no sustained vigorous work (RPE 14 or more) without medical clearance; start at the low end of moderate", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}

$ coach strength sets
{"week": {"start": "2026-10-10", "end": "2026-10-16"}, "sets": {"quads": 6.0, "glutes": 4.5, "adductors": 3.0, "chest": 6.0, "triceps": 4.5, "front_delts": 6.0, "back": 6.0, "biceps": 3.0, "rear_delts": 3.0, "hamstrings": 6.0}, "unmapped": [], "reference_sets_per_week": 10}

$ coach strength progress
{"lifts": {"Curl femoral": {"action": "restart", "load_kg": 25.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 17 days off, restart at 85% of the last working load"]}, "Jalón al pecho": {"action": "restart", "load_kg": 30.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 19 days off, restart at 85% of the last working load"]}, "Peso muerto rumano": {"action": "restart", "load_kg": 42.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 19 days off, restart at 85% of the last working load"]}, "Prensa de piernas": {"action": "restart", "load_kg": 85.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 17 days off, restart at 85% of the last working load"]}, "Press banca": {"action": "restart", "load_kg": 34.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 17 days off, restart at 85% of the last working load"]}, "Press militar": {"action": "restart", "load_kg": 21.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 19 days off, restart at 85% of the last working load"]}, "Remo con barra": {"action": "restart", "load_kg": 34.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 21 days off, restart at 85% of the last working load"]}, "Sentadilla": {"action": "restart", "load_kg": 51.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 21 days off, restart at 85% of the last working load"]}}, "unmatched_rep_ranges": [], "rep_ranges_outside_lookback": []}

$ coach injury list
{"injuries": [], "unmatched": []}
```

(No hay `plan.md`, así que no se pasa `--rep-range`: se aplica 8-12, que es lo que devuelve cada ejercicio. `unmatched_rep_ranges` y `rep_ranges_outside_lookback` salen vacíos.)

Ahora cargo las reglas que aplican: las de siempre, hipertensión, betabloqueante, el PAR-Q+ (hay `review_before_vigorous`), la vuelta tras un descanso y el objetivo de pérdida de grasa (no es principiante, no tiene 65 o más, no está embarazada, no usa GLP-1).

```
$ coach knowledge section strength-hypertrophy "Weekly sets per muscle (dose-response)"
### Weekly sets per muscle (dose-response)
**Rule:** For a client whose priority is muscle gain and who has time, move each major muscle toward roughly 10 or more hard weekly sets over time, ... Treat 10 as a better-than-lower reference point, not a hard minimum; fewer sets still work. ...
**Grade:** strong
...

$ coach knowledge section strength-hypertrophy "Frequency for hypertrophy"
### Frequency for hypertrophy
**Rule:** Choose how often to train each muscle by schedule, recovery and preference. Use frequency to fit in the weekly volume, not as a goal in itself. ...
**Grade:** strong
...

$ coach knowledge section strength-hypertrophy "Full-body versus split"
### Full-body versus split
**Rule:** Let the client pick full-body, upper/lower or another split based on available days and enjoyment. For 2-3 days per week, full-body sessions are the simplest way to hit each muscle twice. ...
**Grade:** moderate
...

$ coach knowledge section strength-hypertrophy "Target reps in reserve"
### Target reps in reserve
**Rule:** Prescribe most working sets at about 1-3 RIR for hypertrophy and 1-4 RIR for strength-focused heavy sets. Warm-up and technique sets do not count as working sets. A set ended with 5+ RIR is probably too easy for hypertrophy.
**Grade:** moderate
...

$ coach knowledge section strength-hypertrophy "Double progression"
### Double progression
**Rule:** Use double progression. Pick a rep range (for example 8-12). When the client beats the top of the range by 1-2 reps on all work sets at the target RIR, add the smallest practical increment within about 2-10% ...
**Grade:** moderate
...

$ coach knowledge section strength-hypertrophy "Load range for hypertrophy"
### Load range for hypertrophy
**Rule:** For a hypertrophy or body-composition goal, let the client choose loads anywhere from about 6 to 30 reps per set based on preference, joint comfort and equipment. Default to moderate loads (about 6-15 reps). ...
**Grade:** strong
...

$ coach knowledge section strength-hypertrophy "Load range for maximal strength"
### Load range for maximal strength
**Rule:** If the client wants to get stronger, include regular heavier work in the 3-8 rep range (about 75-85%+ 1RM) on main lifts once technique is solid. ...
**Grade:** strong
...

$ coach knowledge section cardio-health "Weekly baseline dose"
### Weekly baseline dose
**Rule:** Default weekly health baseline for every client: 150-300 min of moderate cardio, or 75-150 min vigorous, or a mix (1 vigorous minute counts as about 2 moderate minutes), plus at least 2 full-body strength sessions. Use 150 moderate or 75 vigorous min as the minimum and push toward 300/150 when the client has time. ...
**Grade:** strong
...

$ coach knowledge section recovery-habits "Resting BP thresholds to defer or refer"
### Resting BP thresholds to defer or refer
**Rule:** ... Clients with known or suspected hypertension take a seated reading after 5 min rest (properly measured, not a single rushed reading) before sessions while BP is not yet controlled. A band applies when either number reaches it. ...
**Grade:** emerging
...

$ coach knowledge section strength-hypertrophy "Effort limits for older adults and cardiovascular risk"
### Effort limits for older adults and cardiovascular risk
**Rule:** For older beginners (over about 60) and anyone with hypertension or cardiovascular risk, start at about 2-3 RIR (about 13-15 on the Borg 6-20 scale), avoid training to failure, stop a set when form breaks down, and avoid breath-holding (Valsalva). ...
**Grade:** moderate
...

$ coach knowledge section cardio-health "RPE as the anchor under beta-blockade"
### RPE as the anchor under beta-blockade
**Rule:** For clients on beta-blockers, use RPE as the main intensity anchor: Borg 12-13 (CR10 about 5-6) for moderate work, ... with the talk test as a check. Set a ceiling: no sustained vigorous work (RPE 14 or more, ACSM's vigorous band) without medical clearance. ...
**Grade:** emerging
...

$ coach knowledge section recovery-habits "PAR-Q+ specific thresholds"
### PAR-Q+ specific thresholds
**Rule:** Anyone over 45, or with any PAR-Q+ YES, gets a qualified exercise professional or clinician review before vigorous or maximal work (HIIT, 1RM testing, all-out sprints). All-out sprint formats (SIT, REHIT) also require all PAR-Q+ answers NO and at least 4 weeks of regular moderate cardio without symptoms; ...
**Grade:** moderate
...

$ coach knowledge section recovery-habits "How long habits take"
### How long habits take
**Rule:** ... One missed session does not undo progress; get back on track at the next opportunity ("never miss twice" is a practical heuristic, not a tested finding). Never promise "21 days".
**Grade:** emerging
...

$ coach knowledge section strength-hypertrophy "Short breaks cost little"
### Short breaks cost little
**Rule:** Reassure users that a holiday or illness break of a few weeks is not a meaningful setback. As a heuristic, after under about 2 weeks off restart at about 90% of previous working loads; after longer breaks start 10-20% below previous working loads and rebuild over 1-3 weeks ... Expect to regain previous levels within a few weeks. ...
**Grade:** emerging
...

$ coach knowledge section nutrition "Deficit size when keeping or building muscle"
### Deficit size when keeping or building muscle
**Rule:** For clients who want to keep or build muscle while losing fat, keep the deficit at or below about 500 kcal/day, with high protein and resistance training throughout. Tell them strength usually keeps rising in a moderate deficit even when muscle gain stalls. ...
**Grade:** moderate
...

$ coach knowledge section nutrition "Resistance training during any diet, especially for older adults"
### Resistance training during any diet, especially for older adults
**Rule:** Any client in a deficit should do resistance training at least 2-3 times a week throughout the diet; older adults start at 2 days a week and progress to 3 if recovery allows. ...
**Grade:** moderate
...
```

**Coach:** Ya tengo lo que necesito del sistema. Veo que llevas entre 17 y 21 días sin entrenar. Me faltan unos datos tuyos: ¿qué días puedes entrenar y cuánto tiempo? ¿Qué material tienes? ¿Qué ejercicios te gustan y cuáles no? ¿Tienes alguna lesión o dolor? ¿Cuál fue la última sesión que hiciste?

**Cliente:** Puedo lunes, miércoles y viernes, 1 hora en el gimnasio. El sábado o el domingo puedo caminar o ir en bici. El gimnasio es completo: barras, mancuernas, poleas y máquinas. Me gustan la sentadilla, el press de banca y el remo. No me gusta correr. No tengo lesiones. De la última sesión no me acuerdo, no lo sé.

(Coach: el importador no guardó `session_title` (la hoja no tiene esa columna), así que miro el último día registrado: el 2026-10-16 fueron Curl femoral, Prensa de piernas y Press banca, o sea la sesión del viernes. La rotación continúa con la del lunes. No hay lesiones que registrar con `coach injury add`.)

**Coach:** Perfecto. Una duda para el cardio: ¿te va bien el sábado y el domingo, o solo uno de los dos?

**Cliente:** No lo sé.

**Coach:** Vale, lo dejo repartido entre sábado y domingo y me dices si cambia. Te preparo el plan.

(El coach escribe `DATA/plan.md` con el contenido que se muestra abajo. No hay hora de inicio, así que `training_schedule` lleva solo los días. El rango de repeticiones es el de 8-12 por defecto, así que no hay línea `rep_range:`.)

**Coach (mensaje final):**

Fecha: 2026-11-02
target_kcal: 1500.0
in_deficit: true
training_schedule: mon; wed; fri; sat; sun

# Plan

## Semana de entrenamiento

Lunes, miércoles y viernes, 1 hora en el gimnasio, como rotación A, B, C: como la última sesión que registraste fue la del viernes (C), empiezas por la del lunes (A). Si un día no llegas, no lo recuperes añadiendo sesiones: sigues con la siguiente [How long habits take]. 3 series de trabajo por ejercicio, de 8 a 12 repeticiones, dejando 2-3 repeticiones en reserva [Target reps in reserve] [Effort limits for older adults and cardiovascular risk]. Sin llegar al fallo, sin aguantar la respiración y parando la serie si la técnica se rompe. Mismos ejercicios que ya has registrado, para que /review los cuente.

Cargas de partida: llevas de 17 a 21 días sin entrenar, así que vuelves con el 85% de la última carga de trabajo (acción "restart") y las recuperas en 1-3 semanas [Short breaks cost little].

- A (lunes): Sentadilla 51,0 kg; Press banca 34,0 kg; Remo con barra 34,0 kg.
- B (miércoles): Jalón al pecho 30,0 kg; Peso muerto rumano 42,5 kg; Press militar 21,0 kg.
- C (viernes): Curl femoral 25,5 kg; Prensa de piernas 85,0 kg; Press banca 34,0 kg.

Progresión [Double progression]: cuando superes las 12 repeticiones en todas las series con 2-3 en reserva, sube el mínimo incremento práctico de carga.

## Cardio

150 minutos a la semana de intensidad moderada (el mínimo de [Weekly baseline dose]): sábado y domingo, 75 minutos cada día, caminando o en bici (sin correr). Esfuerzo 12-13 en la escala de Borg 6-20, empezando por el 12: puedes hablar, pero no cantar. Sin esfuerzo vigoroso (14 o más).

## Nutrición

- Calorías: 1500,0 kcal al día (déficit de 500 kcal) [Deficit size when keeping or building muscle]
- Proteína: 132,0 g (2,0 g/kg)
- Grasa: 41,67 g (mínimo 33,33 g)
- Carbohidratos: 149,25 g
- Fibra: 25 g

Es una estimación de partida: recalíbrala tras 2-4 semanas de pesajes. En un déficit moderado la fuerza suele seguir subiendo aunque el músculo no crezca [Resistance training during any diet, especially for older adults].

## Notas de seguridad

- Tomas un betabloqueante: el cardio se guía por esfuerzo percibido y prueba del habla, no por pulsaciones [Beta-blockers: no formula-based HR zones]; sin trabajo vigoroso sostenido sin permiso médico [RPE as the anchor under beta-blockade].
- Marcaste SÍ en el PAR-Q+: el plan no incluye HIIT, esprints a tope, comba, saltos ni pruebas de una repetición máxima. Si quieres ese tipo de trabajo, antes lo tiene que revisar una persona cualificada en ejercicio o un médico [PAR-Q+ specific thresholds].
- Hipertensión: tu tensión guardada (132/84) no limita el entrenamiento. Mientras no esté controlada, tómatela sentada tras 5 minutos de reposo antes de entrenar; con 140 de sistólica o más, intensidad moderada y revisión con tu médico de cabecera; con 160/90 o más, consulta antes de seguir [Resting BP thresholds to defer or refer].

## Fuentes

[Weekly sets per muscle (dose-response)], [Frequency for hypertrophy], [Full-body versus split], [Target reps in reserve], [Double progression], [Load range for hypertrophy], [Weekly baseline dose], [Effort limits for older adults and cardiovascular risk], [RPE as the anchor under beta-blockade], [Resting BP thresholds to defer or refer], [PAR-Q+ specific thresholds], [Deficit size when keeping or building muscle], [Resistance training during any diet, especially for older adults], [Beta-blockers: no formula-based HR zones], [Short breaks cost little], [How long habits take].

Revisa el plan con /review cada semana.

El plan está guardado en `data/plan.md`. Dime si el cardio del fin de semana no te encaja y lo reorganizo; revisamos con /review cada semana.

## Primeras líneas de DATA/plan.md

```
Fecha: 2026-11-02
target_kcal: 1500.0
in_deficit: true
training_schedule: mon; wed; fri; sat; sun

# Plan
```
