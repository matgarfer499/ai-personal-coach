# /plan dry run: PAR-Q+ follow-up YES

The client is synthetic (tests/skills/plan/client-parq-followup.md, "Lucía"; no real data). Run date: 2026-11-02, with the current skill.
The setup steps (import, `profile set screening.parq_followup_yes true`) had already been done, so `DATA` (used as `COACH_DATA_DIR`; the skill passes no `--data-dir`) holds profile.yaml, checkins.csv and sessions.csv. There is no `plan.md` and no `reviews/` yet. Long `knowledge section` outputs are cut with `...` (verbatim fragments only).

**Cliente:** Quiero un plan nuevo, me gustaría subir pesos.

**Coach:** Claro. Primero miro tu perfil, tus pruebas de seguridad y tu historial de entrenamientos.

```
$ coach safety
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": true, "prescriber_owns_weight": false, "refer_gp": true, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": true, "review_before_vigorous": true, "no_all_out_sprints": true, "emergency_number": "112", "paused_exercises": {}, "reasons": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "recovery-habits.md: \"PAR-Q+ 2023 as the default entry screen\": follow-up YES, pause intensity progression and refer", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}

$ coach profile show
{"data_dir": "DATA", "profile": {"sex": "female", "birth_date": "1992-03-14", "height_cm": 168.0, "weight_kg": 66.0, "goal": "fat_loss", "experience": "intermediate", "activity_level": "desk", "pal_override": null, "language": "es", "region": "es", "emergency_number": null, "medications": ["beta_blocker"], "conditions": ["hypertension"], "screening": {"scoff_positive": false, "parq_any_yes": true, "cardiac_symptoms": false, "menstrual": "normal", "bp_systolic": 132, "bp_diastolic": 84, "parq_followup_yes": true}, "injuries": [], "research_reminder_months": 6}, "missing": ["emergency_number"], "unrecognised": {"medications": [], "conditions": []}}

$ coach knowledge stale
{"months": 6, "stale": []}
```

**Coach:** (No `no_training`, so I can plan. `refer_gp` and `hold_progression` are set: the plan will not raise anything and will end with the deferral line. No stale knowledge, so no `/research stale` reminder.)

Calorie target: there is no `DATA/plan.md` and no `DATA/reviews/`, so rule 3 applies: `coach energy`. `hold_deficit` is false, so no `--current-kcal`. Its notes hold no `active` `no_training` note, so no `pal_override` question.

```
$ ls DATA/reviews
ls: cannot access 'DATA/reviews': No such file or directory
(DATA/plan.md did not exist either: the DATA listing held only profile.yaml, checkins.csv, sessions.csv)

$ coach energy
{"rmr": 1379.0, "tdee": 1999.55, "target": {"kcal": 1500, "maintenance": 1999.55, "deficit": 500, "clamped": false, "notes": ["nutrition.md: \"Recalibrate TDEE from the weight trend\": starting estimate, recalibrate after 2-4 weeks of weigh-ins", "cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "recovery-habits.md: \"PAR-Q+ 2023 as the default entry screen\": follow-up YES, pause intensity progression and refer", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}}

$ coach macros --kcal 1500 --in-deficit
{"in_deficit": true, "kcal": 1500.0, "protein_g": 132.0, "fat_g": 41.67, "fat_min_g": 33.33, "carbs_g": 149.25, "fibre_g": 25, "protein_g_per_kg": 2.0, "notes": ["nutrition.md: \"Protein during fat loss\": 2 g/kg/day"]}

$ coach zones
{"method": "rpe", "zones": [{"name": "light", "rpe": [9, 11], "talk_test": "can talk and sing", "bpm": null}, {"name": "moderate", "rpe": [12, 13], "talk_test": "can talk, but not sing", "bpm": null}], "hr_max": null, "hr_max_source": null, "hr_rest": null, "notes": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "cardio-health.md: \"RPE as the anchor under beta-blockade\": no sustained vigorous work (RPE 14 or more) without medical clearance; start at the low end of moderate", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": a PAR-Q+ YES, so a qualified exercise professional or clinician reviews vigorous or maximal work (HIIT, 1RM tests, all-out sprints) before it starts; light-to-moderate work until then"]}

$ ls DATA/sessions.csv
DATA/sessions.csv

$ coach strength sets
{"week": {"start": "2026-10-10", "end": "2026-10-16"}, "sets": {"quads": 6.0, "glutes": 4.5, "adductors": 3.0, "chest": 6.0, "triceps": 4.5, "front_delts": 6.0, "back": 6.0, "biceps": 3.0, "rear_delts": 3.0, "hamstrings": 6.0}, "unmapped": [], "reference_sets_per_week": 10}

$ coach strength progress
{"lifts": {"Curl femoral": {"action": "restart", "load_kg": 25.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 17 days off, restart at 85% of the last working load"]}, "Jalón al pecho": {"action": "restart", "load_kg": 30.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 19 days off, restart at 85% of the last working load"]}, "Peso muerto rumano": {"action": "restart", "load_kg": 42.5, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 19 days off, restart at 85% of the last working load"]}, "Prensa de piernas": {"action": "restart", "load_kg": 85.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 17 days off, restart at 85% of the last working load"]}, "Press banca": {"action": "restart", "load_kg": 34.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 17 days off, restart at 85% of the last working load"]}, "Press militar": {"action": "restart", "load_kg": 21.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 19 days off, restart at 85% of the last working load"]}, "Remo con barra": {"action": "restart", "load_kg": 34.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 21 days off, restart at 85% of the last working load"]}, "Sentadilla": {"action": "restart", "load_kg": 51.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 21 days off, restart at 85% of the last working load"]}}, "unmatched_rep_ranges": [], "rep_ranges_outside_lookback": []}
```

(No `plan.md`, so no `--rep-range` is passed: the default 8-12 applies and every lift returns it. `unmatched_rep_ranges` and `rep_ranges_outside_lookback` are empty.)

**Coach:** (Loading the knowledge that applies: the always-rules, hypertension (BP rules), beta-blocker, the PAR-Q+ follow-up YES and `review_before_vigorous` rules, the break since the last session, goal fat_loss. Not novice (intermediate), not 65+, not pregnant, not GLP-1.)

```
$ coach knowledge section strength-hypertrophy "Weekly sets per muscle (dose-response)"
### Weekly sets per muscle (dose-response)
**Rule:** For a client whose priority is muscle gain and who has time, move each major muscle toward roughly 10 or more hard weekly sets ... Treat 10 as a better-than-lower reference point, not a hard minimum; fewer sets still work. ... For strength or health goals, fewer sets suffice because returns diminish quickly.
...
**Grade:** strong

$ coach knowledge section strength-hypertrophy "Frequency for hypertrophy"
### Frequency for hypertrophy
**Rule:** Choose how often to train each muscle by schedule, recovery and preference. Use frequency to fit in the weekly volume, not as a goal in itself. ...
...
**Grade:** strong

$ coach knowledge section strength-hypertrophy "Full-body versus split"
### Full-body versus split
**Rule:** Let the client pick full-body, upper/lower or another split based on available days and enjoyment. For 2-3 days per week, full-body sessions are the simplest way to hit each muscle twice. ...
...
**Grade:** moderate

$ coach knowledge section strength-hypertrophy "Target reps in reserve"
### Target reps in reserve
**Rule:** Prescribe most working sets at about 1-3 RIR for hypertrophy and 1-4 RIR for strength-focused heavy sets. ... A set ended with 5+ RIR is probably too easy for hypertrophy.
...
**Grade:** moderate

$ coach knowledge section strength-hypertrophy "Double progression"
### Double progression
**Rule:** Use double progression. Pick a rep range (for example 8-12). When the client beats the top of the range by 1-2 reps on all work sets at the target RIR, add the smallest practical increment within about 2-10% ... Adding reps or sets at the same load is equally valid when the next jump is too big. ...
...
**Grade:** moderate

$ coach knowledge section strength-hypertrophy "Load range for hypertrophy"
### Load range for hypertrophy
**Rule:** For a hypertrophy or body-composition goal, let the client choose loads anywhere from about 6 to 30 reps per set based on preference, joint comfort and equipment. Default to moderate loads (about 6-15 reps). ...
...
**Grade:** strong

$ coach knowledge section strength-hypertrophy "Load range for maximal strength"
### Load range for maximal strength
**Rule:** If the client wants to get stronger, include regular heavier work in the 3-8 rep range (about 75-85%+ 1RM) on main lifts once technique is solid. ...
...
**Grade:** strong

$ coach knowledge section cardio-health "Weekly baseline dose"
### Weekly baseline dose
**Rule:** Default weekly health baseline for every client: 150-300 min of moderate cardio, or 75-150 min vigorous, or a mix ..., plus at least 2 full-body strength sessions. Use 150 moderate or 75 vigorous min as the minimum and push toward 300/150 when the client has time. ...
...
**Grade:** strong

$ coach knowledge section recovery-habits "Resting BP thresholds to defer or refer"
### Resting BP thresholds to defer or refer
**Rule:** ... Clients with known or suspected hypertension take a seated reading after 5 min rest ... before sessions while BP is not yet controlled. A band applies when either number reaches it. ...
...
**Grade:** emerging

$ coach knowledge section strength-hypertrophy "Effort limits for older adults and cardiovascular risk"
### Effort limits for older adults and cardiovascular risk
**Rule:** For older beginners (over about 60) and anyone with hypertension or cardiovascular risk, start at about 2-3 RIR (about 13-15 on the Borg 6-20 scale), avoid training to failure, stop a set when form breaks down, and avoid breath-holding (Valsalva). ...
...
**Grade:** moderate

$ coach knowledge section cardio-health "RPE as the anchor under beta-blockade"
### RPE as the anchor under beta-blockade
**Rule:** For clients on beta-blockers, use RPE as the main intensity anchor: Borg 12-13 (CR10 about 5-6) for moderate work ... starting at the lower end ..., with the talk test as a check. Set a ceiling: no sustained vigorous work (RPE 14 or more, ACSM's vigorous band) without medical clearance. ...
...
**Grade:** emerging

$ coach knowledge section recovery-habits "PAR-Q+ 2023 as the default entry screen"
### PAR-Q+ 2023 as the default entry screen
**Rule:** ...
...

$ coach knowledge section recovery-habits "PAR-Q+ specific thresholds"
### PAR-Q+ specific thresholds
**Rule:** Anyone over 45, or with any PAR-Q+ YES, gets a qualified exercise professional or clinician review before vigorous or maximal work (HIIT, 1RM testing, all-out sprints). All-out sprint formats (SIT, REHIT) also require all PAR-Q+ answers NO and at least 4 weeks of regular moderate cardio without symptoms; ...
...
**Grade:** moderate

$ coach knowledge section recovery-habits "How long habits take"
### How long habits take
**Rule:** ... One missed session does not undo progress; get back on track at the next opportunity ("never miss twice" is a practical heuristic, not a tested finding). Never promise "21 days".
...
**Grade:** emerging

$ coach knowledge section strength-hypertrophy "Short breaks cost little"
### Short breaks cost little
**Rule:** Reassure users that a holiday or illness break of a few weeks is not a meaningful setback. As a heuristic, after under about 2 weeks off restart at about 90% of previous working loads; after longer breaks start 10-20% below previous working loads and rebuild over 1-3 weeks ... Expect to regain previous levels within a few weeks. ...
...
**Grade:** emerging

$ coach knowledge section nutrition "Deficit size when keeping or building muscle"
### Deficit size when keeping or building muscle
**Rule:** For clients who want to keep or build muscle while losing fat, keep the deficit at or below about 500 kcal/day, with high protein and resistance training throughout. ...
...
**Grade:** moderate

$ coach knowledge section nutrition "Resistance training during any diet, especially for older adults"
### Resistance training during any diet, especially for older adults
**Rule:** Any client in a deficit should do resistance training at least 2-3 times a week throughout the diet; ...
...
**Grade:** moderate
```

(For the PAR-Q+ entry-screen rule the body is cut to `...` here to keep the file short; the dry run read it whole.)

**Coach:** Ya tengo lo que necesito de tu perfil. Para armar la semana me faltan unos datos: ¿qué días puedes entrenar y cuánto tiempo? ¿Qué material tienes? ¿Qué ejercicios te gustan y cuáles no? ¿Alguna lesión o dolor? ¿Cuál fue la última sesión que hiciste? Y de cardio, ¿cuánto haces ahora por tu cuenta y en qué días?

**Cliente:** Puedo lunes, miércoles y viernes, 1 hora. El sábado camino. Tengo gimnasio completo. Lo de los ejercicios que me gustan, las lesiones y la última sesión, no lo sé.

**Coach:** Perfecto. ¿Cuántos minutos caminas el sábado, más o menos? ¿Y has podido hablar ya con el médico por lo del cuestionario PAR-Q+?

**Cliente:** Los minutos no lo sé. Al médico aún no he ido.

**Coach:** (Sin ejercicios preferidos, se mantienen los que ya registra, con los mismos nombres, para que `/review` pueda contarlos. No hay `session_title` en el registro, así que la rotación se deduce del último día registrado (2026-10-16: Curl femoral, Prensa de piernas, Press banca, la sesión del viernes) y sigue con la del lunes. Sin lesiones, no hay `coach injury add`. Sin minutos de cardio actuales, se empieza por el mínimo de la regla (150 min) y no se inventa un reparto por días: solo se ha ofrecido el sábado. Al ser `hold_progression`: mismas series que las registradas, esfuerzo no más duro que el de las últimas sesiones, cargas solo las que da el comando (que bajan al 85% tras el descanso), y no se sube nada aunque ella lo pida. Sin hora de inicio, `training_schedule` lleva solo los días. Se escribe `DATA/plan.md`.)

```
$ cat > DATA/plan.md   (file written; content identical to the final message below, including the review line and the deferral line)
```

**Coach (final message):**

Fecha: 2026-11-02
target_kcal: 1500.0
in_deficit: true
training_schedule: mon; wed; fri; sat

## Semana de entrenamiento

Tres sesiones de cuerpo completo de 1 hora en el gimnasio: lunes, miércoles y viernes, en
rotación A, B, C (empiezas por la del lunes, porque la última que registraste fue la del
viernes; si un día no llegas, sigues con la siguiente sin recuperar nada) [Weekly baseline dose]
[Full-body versus split] [How long habits take]. Mismos ejercicios, con los mismos nombres, y
las mismas 3 series que ya registras, así cada músculo se queda cerca de sus series semanales
actuales [Weekly sets per muscle (dose-response)] [Frequency for hypertrophy].

Me pedías subir pesos. Por ahora no: tu respuesta en el cuestionario PAR-Q+ pide que te vea tu
médico, y mientras tanto no se sube ni la carga, ni las series, ni el esfuerzo
[PAR-Q+ 2023 as the default entry screen]. Este plan es de mantenimiento, no de progresión.

Todas las series de trabajo: 3 series de 8-12 repeticiones, dejando 2-3 repeticiones en reserva
(RIR). Nunca al fallo, para la serie si la técnica se rompe y no aguantes la respiración
[Target reps in reserve] [Effort limits for older adults and cardiovascular risk]. Tus últimas
sesiones fueron con 2 RIR; no es más duro que eso. Aunque llegues a 12 repeticiones en todas las
series, no subas la carga: misma carga y mismas repeticiones hasta que tu médico lo revise
[Double progression].

Cargas de partida (el comando marca "restart": llevas de 17 a 21 días sin hacer cada ejercicio y
se retoma al 85% de la última carga de trabajo [Short breaks cost little]):

**Lunes (A)**
- Sentadilla: 51,0 kg (21 días sin hacerla)
- Press banca: 34,0 kg (17 días)
- Remo con barra: 34,0 kg (21 días)

**Miércoles (B)**
- Peso muerto rumano: 42,5 kg (19 días)
- Press militar: 21,0 kg (19 días)
- Jalón al pecho: 30,0 kg (19 días)

**Viernes (C)**
- Prensa de piernas: 85,0 kg (17 días)
- Press banca: 34,0 kg (17 días)
- Curl femoral: 25,5 kg (17 días)

## Cardio

Mínimo semanal: 150 minutos de cardio moderado [Weekly baseline dose]. El sábado es tu día de
caminata. No me has dicho cuántos minutos caminas ni otros días libres, así que los minutos que
no te quepan el sábado, repártelos en paseos cortos los días que tú elijas y dímelos para dejarlos
fijados en el plan.

Intensidad: esfuerzo percibido (RPE) 12-13, puedes hablar pero no cantar. Empieza en el extremo
bajo, RPE 12 [RPE as the anchor under beta-blockade]. Sin trabajo intenso sostenido (RPE 14 o
más) sin visto bueno de tu médico. Con betabloqueante es fácil puntuar el esfuerzo por debajo y
acabar yendo más fuerte; revisa en las primeras sesiones cómo notas el RPE.

## Nutrición

Objetivo diario (fase de pérdida de grasa):
- Calorías: 1500,0 kcal
- Proteína: 132,0 g
- Grasa: 41,67 g
- Carbohidratos: 149,25 g
- Fibra: 25 g

El déficit es de 500 kcal respecto a tu mantenimiento estimado (1999,55 kcal), el límite
recomendado para conservar músculo [Deficit size when keeping or building muscle]. Es una
estimación inicial: se recalibra tras 2-4 semanas de pesajes [Recalibrate TDEE from the weight
trend]. El entrenamiento de fuerza se mantiene durante toda la dieta [Resistance training during
any diet, especially for older adults]. Proteína: 2 g/kg/día [Protein during fat loss].

## Notas de seguridad

- Cuestionario PAR-Q+ con respuesta SÍ en las preguntas de seguimiento y sin revisión médica
  todavía: hasta que te vea tu médico, el plan no sube cargas, series ni esfuerzo. Que el médico
  revise primero si puedes entrenar fuerza y caminar a ritmo moderado, teniendo en cuenta tu
  hipertensión y tu betabloqueante [PAR-Q+ 2023 as the default entry screen].
- Sin trabajo intenso ni máximo (HIIT, esprints a tope, comba, saltos, pruebas de una repetición
  máxima) hasta que una persona cualificada en ejercicio o un médico lo revise [PAR-Q+ specific
  thresholds].
- Tomas un betabloqueante: por eso la intensidad del cardio va por esfuerzo percibido y la
  prueba del habla, no por pulsaciones [Beta-blockers: no formula-based HR zones].
- Hipertensión: tu última tensión registrada (132/84) está por debajo de los tramos que piden
  consulta. Mide la tensión sentada, tras 5 minutos de reposo, antes de las sesiones mientras no
  esté controlada [Resting BP thresholds to defer or refer].

## Fuentes

[Weekly baseline dose], [Full-body versus split], [Weekly sets per muscle (dose-response)],
[Frequency for hypertrophy], [Target reps in reserve], [Effort limits for older adults and
cardiovascular risk], [Double progression], [Short breaks cost little], [How long habits take],
[RPE as the anchor under beta-blockade], [Beta-blockers: no formula-based HR zones], [Resting BP
thresholds to defer or refer], [PAR-Q+ 2023 as the default entry screen], [PAR-Q+ specific
thresholds], [Deficit size when keeping or building muscle], [Recalibrate TDEE from the weight
trend], [Resistance training during any diet, especially for older adults], [Protein during fat
loss].

Revisa el plan con /review cada semana.

Esto es orientación general de un entrenador automatizado, no consejo médico. Por lo que me has contado, habla con tu médico (o con el profesional que te indico arriba) antes de ponerlo en práctica.
