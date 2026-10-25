# /plan dry run

El cliente es sintético (tests/skills/plan/client.md, "Lucía"; sin datos reales). Fecha de la ejecución: 2026-10-24. DATA es una copia del estado inicial (profile.yaml, checkins.csv y sessions.csv ya importado; sin `plan.md` ni `reviews/`).

**Cliente:** ¿Me haces un plan para las próximas semanas?

**Coach:** Claro. Primero miro tu perfil, las comprobaciones de seguridad y tu historial de entrenamientos.

```
$ uv run python -m coach --data-dir DATA safety --json
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": true, "prescriber_owns_weight": false, "refer_gp": false, "no_training": false, "cap_moderate": false, "hold_progression": false, "reasons": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test"]}

$ uv run python -m coach --data-dir DATA profile show --json
{"profile": {"sex": "female", "birth_date": "1992-03-14", "height_cm": 168.0, "weight_kg": 66.0, "goal": "fat_loss", "experience": "intermediate", "activity_level": "desk", "language": "es", "region": "es", "medications": ["beta_blocker"], "conditions": ["hypertension"], "screening": {"scoff_positive": false, "parq_any_yes": true, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal", "bp_systolic": 132, "bp_diastolic": 84}, "research_reminder_months": 6}, "missing": [], "unrecognised": {"medications": [], "conditions": []}}

$ uv run python -m coach --data-dir DATA knowledge stale --json
{"months": 6, "stale": []}
```

(No hay `data/reviews/` ni `data/plan.md`, así que el objetivo calórico sale de `coach energy`. `hold_deficit` es false, así que no hace falta `--current-kcal`.)

```
$ uv run python -m coach --data-dir DATA energy --json
{"rmr": 1379.0, "tdee": 1999.55, "target": {"kcal": 1500, "maintenance": 1999.55, "deficit": 500, "clamped": false, "notes": ["nutrition.md: \"Recalibrate TDEE from the weight trend\": starting estimate, recalibrate after 2-4 weeks of weigh-ins", "cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test"]}}

$ uv run python -m coach --data-dir DATA macros --kcal 1500 --in-deficit --json
{"in_deficit": true, "kcal": 1500.0, "protein_g": 132.0, "fat_g": 41.67, "fat_min_g": 33.33, "carbs_g": 149.25, "fibre_g": 25, "protein_g_per_kg": 2.0, "notes": ["nutrition.md: \"Protein during fat loss\": 2 g/kg/day"]}

$ uv run python -m coach --data-dir DATA zones --json
{"method": "rpe", "zones": [{"name": "light", "rpe": [9, 11], "talk_test": "can talk and sing", "bpm": null}, {"name": "moderate", "rpe": [12, 13], "talk_test": "can talk, but not sing", "bpm": null}], "hr_max": null, "hr_max_source": null, "hr_rest": null, "notes": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "cardio-health.md: \"RPE as the anchor under beta-blockade\": no sustained vigorous work (RPE 14 or more) without medical clearance; start at the low end of moderate"]}

$ uv run python -m coach --data-dir DATA strength sets --json
{"week": {"start": "2026-10-10", "end": "2026-10-16"}, "sets": {"quads": 6.0, "glutes": 4.5, "adductors": 3.0, "chest": 6.0, "triceps": 4.5, "front_delts": 6.0, "back": 6.0, "biceps": 3.0, "rear_delts": 3.0, "hamstrings": 6.0}, "unmapped": [], "reference_sets_per_week": 10}

$ uv run python -m coach --data-dir DATA strength progress --json
{"Curl femoral": {"action": "restart", "load_kg": 27.0, "rep_range": [8, 12], "reasons": ["strength-hypertrophy.md: \"Short breaks cost little\": 8 days off, restart at 90% of the last working load"]},
 "Jalón al pecho": {"action": "restart", "load_kg": 31.5, "rep_range": [8, 12], "reasons": [... "10 days off, restart at 90% of the last working load"]},
 "Peso muerto rumano": {"action": "restart", "load_kg": 45.0, "rep_range": [8, 12], "reasons": [... "10 days off ..."]},
 "Prensa de piernas": {"action": "restart", "load_kg": 90.0, "rep_range": [8, 12], "reasons": [... "8 days off ..."]},
 "Press banca": {"action": "restart", "load_kg": 36.0, "rep_range": [8, 12], "reasons": [... "8 days off ..."]},
 "Press militar": {"action": "restart", "load_kg": 22.5, "rep_range": [8, 12], "reasons": [... "10 days off ..."]},
 "Remo con barra": {"action": "restart", "load_kg": 36.0, "rep_range": [8, 12], "reasons": [... "12 days off ..."]},
 "Sentadilla": {"action": "restart", "load_kg": 54.0, "rep_range": [8, 12], "reasons": [... "12 days off ..."]}}
```

Ahora cargo las reglas que aplican: las de siempre, hipertensión, betabloqueante y objetivo de pérdida de grasa (no es principiante, no tiene 65 o más, no está embarazada, no usa GLP-1).

```
$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Weekly sets per muscle (dose-response)"
### Weekly sets per muscle (dose-response)
**Rule:** ... move each major muscle toward roughly 10 or more hard weekly sets over time ... Treat 10 as a better-than-lower reference point, not a hard minimum ... For strength or health goals, fewer sets suffice ...
**Grade:** strong
...

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Frequency for hypertrophy"
### Frequency for hypertrophy
**Rule:** Choose how often to train each muscle by schedule, recovery and preference. Use frequency to fit in the weekly volume, not as a goal in itself. ...
**Grade:** strong
...

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Full-body versus split"
### Full-body versus split
**Rule:** Let the client pick full-body, upper/lower or another split based on available days and enjoyment. For 2-3 days per week, full-body sessions are the simplest way to hit each muscle twice. ...
**Grade:** moderate
...

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Target reps in reserve"
### Target reps in reserve
**Rule:** Prescribe most working sets at about 1-3 RIR for hypertrophy and 1-4 RIR for strength-focused heavy sets. Warm-up and technique sets do not count as working sets. A set ended with 5+ RIR is probably too easy for hypertrophy.
**Grade:** moderate
...

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Double progression"
### Double progression
**Rule:** Use double progression. Pick a rep range (for example 8-12). When the client beats the top of the range by 1-2 reps on all work sets at the target RIR, add the smallest practical increment within about 2-10% ... For content health-focused clients, holding a challenging routine steady is acceptable ...
**Grade:** moderate
...

$ uv run python -m coach --data-dir DATA knowledge section cardio-health "Weekly baseline dose"
### Weekly baseline dose
**Rule:** Default weekly health baseline for every client: 150-300 min of moderate cardio, or 75-150 min vigorous, or a mix ..., plus at least 2 full-body strength sessions. Use 150 moderate or 75 vigorous min as the minimum and push toward 300/150 when the client has time. ... brisk walking counts. ... Let the client choose modalities they enjoy ...
**Grade:** strong
...

$ uv run python -m coach --data-dir DATA knowledge section recovery-habits "Resting BP thresholds to defer or refer"
### Resting BP thresholds to defer or refer
**Rule:** ... seated reading after 5 min rest ... before sessions while BP is not yet controlled. ... At 160-179 systolic or 90-109 diastolic, or with BP unknown ...: GP review before starting a programme or progressing ..., and light-to-moderate work only until BP is controlled. At 140-159 systolic with diastolic below 90: train at moderate intensity and recommend a GP check.
**Grade:** emerging
...

$ uv run python -m coach --data-dir DATA knowledge section strength-hypertrophy "Effort limits for older adults and cardiovascular risk"
### Effort limits for older adults and cardiovascular risk
**Rule:** For older beginners (over about 60) and anyone with hypertension or cardiovascular risk, start at about 2-3 RIR (about 13-15 on the Borg 6-20 scale), avoid training to failure, stop a set when form breaks down, and avoid breath-holding (Valsalva). ...
**Grade:** moderate
...

$ uv run python -m coach --data-dir DATA knowledge section cardio-health "RPE as the anchor under beta-blockade"
### RPE as the anchor under beta-blockade
**Rule:** For clients on beta-blockers, use RPE as the main intensity anchor: Borg 12-13 ... for moderate work ..., starting at the lower end ..., with the talk test as a check. Set a ceiling: no sustained vigorous work (RPE 14 or more ...) without medical clearance. ...
**Grade:** emerging
...

$ uv run python -m coach --data-dir DATA knowledge section nutrition "Deficit size when keeping or building muscle"
### Deficit size when keeping or building muscle
**Rule:** ... keep the deficit at or below about 500 kcal/day, with high protein and resistance training throughout. Tell them strength usually keeps rising in a moderate deficit even when muscle gain stalls. ...
**Grade:** moderate
...

$ uv run python -m coach --data-dir DATA knowledge section nutrition "Resistance training during any diet, especially for older adults"
### Resistance training during any diet, especially for older adults
**Rule:** Any client in a deficit should do resistance training at least 2-3 times a week throughout the diet; older adults start at 2 days a week ... Monitor strength and function, not just scale weight.
**Grade:** moderate
...
```

**Coach:** Ya tengo lo que necesito del sistema. Me faltan unos datos tuyos. ¿Qué días puedes entrenar y cuánto tiempo? ¿Qué material tienes? ¿Qué ejercicios te gustan y cuáles no? ¿Tienes alguna lesión?

**Cliente:** Puedo lunes, miércoles y viernes, 1 hora en el gimnasio. El sábado o el domingo puedo caminar o ir en bici. El gimnasio es completo: barras, mancuernas, poleas y máquinas. Me gustan la sentadilla, el press de banca y el remo. No me gusta correr. No tengo lesiones.

**Coach:** Perfecto. Una duda para el cardio: ¿te va bien el sábado y el domingo, o solo uno de los dos?

**Cliente:** No lo sé.

**Coach:** Vale, lo dejo repartido entre sábado y domingo y me dices si cambia. Te preparo el plan.

(El coach escribe `DATA/plan.md` con el contenido que se muestra abajo.)

**Coach (mensaje final):**

Fecha: 2026-10-24
target_kcal: 1500
in_deficit: true

# Plan

## Semana de entrenamiento

Lunes, miércoles y viernes, 1 hora en el gimnasio. 3 series de trabajo por ejercicio, de 8 a 12 repeticiones, dejando 2-3 repeticiones en reserva [Target reps in reserve] [Effort limits for older adults and cardiovascular risk]. Sin llegar al fallo, sin aguantar la respiración y parando la serie si la técnica se rompe. Mismos ejercicios que ya has registrado, para que /review los cuente.

Cargas de partida: has estado de 8 a 12 días sin entrenar, así que vuelves con el 90% de la última carga de trabajo (acción "restart") [Short breaks cost little].

- Lunes: Sentadilla 54,0 kg; Press banca 36,0 kg; Remo con barra 36,0 kg.
- Miércoles: Jalón al pecho 31,5 kg; Peso muerto rumano 45,0 kg; Press militar 22,5 kg.
- Viernes: Curl femoral 27,0 kg; Prensa de piernas 90,0 kg; Press banca 36,0 kg.

Progresión [Double progression]: cuando superes las 12 repeticiones en todas las series con 2-3 en reserva, sube el mínimo incremento práctico de carga.

## Cardio

150 minutos a la semana de intensidad moderada (el mínimo de [Weekly baseline dose]): sábado y domingo, 75 minutos cada día, caminando o en bici (sin correr). Esfuerzo 12-13 en la escala de Borg 6-20, empezando por el 12: puedes hablar, pero no cantar. Sin esfuerzo vigoroso (14 o más).

## Nutrición

- Calorías: 1500 kcal al día (déficit de 500 kcal) [Deficit size when keeping or building muscle]
- Proteína: 132,0 g (2,0 g/kg)
- Grasa: 41,67 g (mínimo 33,33 g)
- Carbohidratos: 149,25 g
- Fibra: 25 g

Es una estimación de partida: recalíbrala tras 2-4 semanas de pesajes. En un déficit moderado la fuerza suele seguir subiendo aunque el músculo no crezca.

## Notas de seguridad

- Tomas un betabloqueante: el cardio se guía por esfuerzo percibido y prueba del habla, no por pulsaciones [Beta-blockers: no formula-based HR zones]; sin trabajo vigoroso sostenido sin permiso médico [RPE as the anchor under beta-blockade].
- Hipertensión: tu tensión guardada (132/84) no limita el entrenamiento. Mientras no esté controlada, tómatela sentada tras 5 minutos de reposo antes de entrenar; con 140 de sistólica o más, intensidad moderada y revisión con tu médico de cabecera; con 160/90 o más, consulta antes de seguir [Resting BP thresholds to defer or refer].

## Fuentes

[Weekly sets per muscle (dose-response)], [Frequency for hypertrophy], [Full-body versus split], [Target reps in reserve], [Double progression], [Weekly baseline dose], [Effort limits for older adults and cardiovascular risk], [RPE as the anchor under beta-blockade], [Resting BP thresholds to defer or refer], [Deficit size when keeping or building muscle], [Resistance training during any diet, especially for older adults], [Beta-blockers: no formula-based HR zones], [Short breaks cost little].

Revisa el plan con /review cada semana.

El plan está guardado en `data/plan.md`. Dime si el cardio del fin de semana no te encaja y lo reorganizo; revisamos con /review cada semana.

## Primeras 5 líneas de DATA/plan.md

```
Fecha: 2026-10-24
target_kcal: 1500
in_deficit: true

# Plan
```
