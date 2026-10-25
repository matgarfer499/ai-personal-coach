# /setup dry run

The client is synthetic (`tests/skills/setup/client.md`); dry run on 2026-10-24. DATA below stands for an empty scratch directory.

---

**Coach:** Hola, vamos a preparar tu perfil (Hi, let's set up your profile). Antes de nada: ¿prefieres que hablemos en español (es) o en inglés (en)? ¿Y dónde vives?

```
$ coach profile show
{"profile": {"sex": null, "birth_date": null, "height_cm": null, "weight_kg": null, "goal": null, "experience": null, "activity_level": null, "language": null, "region": null, "medications": [], "conditions": [], "screening": {}, "research_reminder_months": 6}, "missing": ["sex", "birth_date", "height_cm", "weight_kg", "goal", "experience", "activity_level", "language", "region"], "unrecognised": {"medications": [], "conditions": []}}
```

**Cliente:** Español. Vivo en Madrid.

```
$ coach profile set language es
... "language": "es", ... "missing": ["sex", "birth_date", "height_cm", "weight_kg", "goal", "experience", "activity_level", "region"] ...
$ coach profile set region es
... "region": "es", ... "missing": ["sex", "birth_date", "height_cm", "weight_kg", "goal", "experience", "activity_level"] ...
```

**Coach:** Perfecto, seguimos en español. Ahora unas preguntas sobre tu relación con la comida. No son un diagnóstico, solo una forma de empezar a hablar y de ajustar bien el plan. Contéstame con sinceridad, sí o no a cada una:
- ¿Alguna vez te provocas el vómito porque te sientes incómodamente llena?
- ¿Te preocupa perder el control sobre cuánto comes?
- ¿Te sientes gorda aunque los demás te digan que estás delgada?
- ¿La comida o el peso dominan tus pensamientos o tu vida?
- ¿Has perdido hace poco mucho peso, de forma que te preocupara a ti o a otras personas?

**Cliente:** No a todas.

```
$ coach profile set screening.scoff_positive false
... "screening": {"scoff_positive": false} ... "missing": ["sex", "birth_date", "height_cm", "weight_kg", "goal", "experience", "activity_level"]
```

**Coach:** Gracias. Ahora lo básico: ¿cuál es tu sexo (las ecuaciones que uso solo existen para mujer y hombre) y tu fecha de nacimiento?

**Cliente:** Mujer. Nací el 14 de marzo de 1992.

```
$ coach profile set sex female
$ coach profile set birth_date 1992-03-14
... "missing": ["height_cm", "weight_kg", "goal", "experience", "activity_level"]
```

**Coach:** ¿Cuánto mides y cuánto pesas aproximadamente?

**Cliente:** 168 cm y 66 kg.

```
$ coach profile set height_cm 168
$ coach profile set weight_kg 66
... "missing": ["goal", "experience", "activity_level"]
```

**Coach:** Ahora el cuestionario de aptitud para la actividad física PAR-Q+ (oficial, en https://eparmedx.com, no se puede cambiar). ¿Ya lo has rellenado?

**Cliente:** Sí, lo rellené en eparmedx.com.

**Coach:** Entonces dime solo el resultado: ¿has contestado SÍ a alguna de las 7 preguntas? ¿Y SÍ a alguna de las preguntas de las páginas de seguimiento?

**Cliente:** Sí a la pregunta de "diagnosed heart condition or high blood pressure". En las preguntas de seguimiento, todas NO.

```
$ coach profile set screening.parq_any_yes true
$ coach profile set screening.parq_followup_yes false
... "screening": {"scoff_positive": false, "parq_any_yes": true, "parq_followup_yes": false} ...
```

**Coach:** Entendido. Ahora, ¿has tenido alguno de estos síntomas: dolor o presión en el pecho, cuello, mandíbula o brazo; falta de aire en reposo o con esfuerzos suaves; mareos o desmayos; palpitaciones; hinchazón de tobillos; dolor en las pantorrillas al caminar? ¿Alguno está pasando ahora o en reposo?

```
$ coach knowledge section recovery-habits "Cardiac warning symptoms: stop and refer"
### Cardiac warning symptoms: stop and refer
**Rule:** If a user reports any of the symptoms below, before or during a session, tell them to stop exercising and seek medical evaluation. ... chest pain at rest, fainting, or chest pain with breathlessness and sweating means calling emergency services now.
...
**Grade:** moderate
...
**Sources:** [S120], [S119]
```

**Cliente:** Ninguno.

```
$ coach profile set screening.cardiac_symptoms false
... "cardiac_symptoms": false ...
```

**Coach:** Bien. ¿Tomas alguna medicación y tienes algún diagnóstico?

**Cliente:** Tomo bisoprolol 2,5 mg por la mañana para la tensión. Tengo hipertensión, me la diagnosticaron hace un año, está controlada.

(Coach: bisoprolol maps to `beta_blocker`, the diagnosis to `hypertension`, per the table in `docs/safety.md`.)

```
$ coach profile set medications beta_blocker
... "medications": ["beta_blocker"], "conditions": [] ...
$ coach profile set conditions hypertension
... "medications": ["beta_blocker"], "conditions": ["hypertension"], "unrecognised": {"medications": [], "conditions": []}
```

**Coach:** ¿Estás embarazada o piensas estarlo pronto? Y como tienes hipertensión: ¿sabes tu última tensión, medida sentada tras 5 minutos de reposo?

**Cliente:** No estoy embarazada ni lo planeo. La tensión no la sé (el médico dice que está controlada).

(Coach: no pregnancy token means "no", nothing stored. With hypertension and no reading, even if "controlled", store nothing; the CLI applies the BP-unknown band.)

**Coach:** Vale. Como no tienes una lectura, no guardo nada y el sistema será prudente. Mídete la tensión una vez, sentada y tras 5 minutos de reposo, y dámela en tu próximo `/checkin`. Sobre el ciclo: ¿tus reglas son regulares, han aparecido irregularidades nuevas, o llevan ausentes 3 meses o más (o tienes menos de 6 al año)?

**Cliente:** Regular, sin cambios recientes.

```
$ coach profile set screening.menstrual normal
... "menstrual": "normal" ...
```

**Coach:** Perfecto. Ahora el objetivo y el entrenamiento. ¿Qué quieres conseguir? ¿Y cuánto llevas entrenando de forma constante?

**Cliente:** Perder grasa sin perder fuerza. Entreno con pesas desde hace 2 años.

**Coach:** ¿Cuántos días a la semana y cuánto tiempo por sesión? ¿Y cómo es tu día a día fuera del gimnasio (trabajo, pasos)?

**Cliente:** 3 días por semana, 1 hora. Trabajo en una oficina, sentada casi todo el día; camino unos 6.000 pasos.

(Coach: "lose fat and keep strength" = `fat_loss`; 2 years = `intermediate`. Desk job and 3 sessions a week is below the "4 or more days" of `desk_training`, so `desk`, per the rule below.)

```
$ coach knowledge section nutrition "Activity multipliers (PAL)"
### Activity multipliers (PAL)
**Rule:** Multiply estimated RMR by a PAL: about 1.4-1.5 (up to 1.6) for desk workers with little exercise or a few short sessions a week; about 1.6-1.75 for desk workers who train most days for about 1 hour; ...
...
**Grade:** moderate
**Sources:** [S166], [S281]

$ coach profile set goal fat_loss
$ coach profile set experience intermediate
$ coach profile set activity_level desk
... "missing": []
```

```
$ coach profile show
{"profile": {"sex": "female", "birth_date": "1992-03-14", "height_cm": 168.0, "weight_kg": 66.0, "goal": "fat_loss", "experience": "intermediate", "activity_level": "desk", "language": "es", "region": "es", "medications": ["beta_blocker"], "conditions": ["hypertension"], "screening": {"scoff_positive": false, "parq_any_yes": true, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal"}, "research_reminder_months": 6}, "missing": [], "unrecognised": {"medications": [], "conditions": []}}

$ coach safety
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": true, "prescriber_owns_weight": false, "refer_gp": true, "no_training": false, "cap_moderate": true, "reasons": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test", "recovery-habits.md: \"Resting BP thresholds to defer or refer\": BP unknown with known hypertension, so a GP review before starting or progressing, and light-to-moderate work only"]}

$ coach energy
{"rmr": 1379.0, "tdee": 1999.55, "target": {"kcal": 1500, "maintenance": 1999.55, "deficit": 500, "clamped": false, "notes": ["nutrition.md: \"Recalibrate TDEE from the weight trend\": starting estimate, recalibrate after 2-4 weeks of weigh-ins", "cardio-health.md: \"Beta-blockers: no formula-based HR zones\": ...", "recovery-habits.md: \"Resting BP thresholds to defer or refer\": ..."]}}

$ coach macros
{"in_deficit": true, "kcal": 1500, "protein_g": 132.0, "fat_g": 41.67, "fat_min_g": 33.33, "carbs_g": 149.25, "fibre_g": 25, "protein_g_per_kg": 2.0, "notes": ["nutrition.md: \"Protein during fat loss\": 2 g/kg/day"]}

$ coach zones
{"method": "rpe", "zones": [{"name": "light", "rpe": [9, 11], "talk_test": "can talk and sing", "bpm": null}, {"name": "moderate", "rpe": [12, 13], "talk_test": "can talk, but not sing", "bpm": null}], "hr_max": null, "hr_max_source": null, "hr_rest": null, "notes": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": ...", "cardio-health.md: \"RPE as the anchor under beta-blockade\": no sustained vigorous work (RPE 14 or more) without medical clearance; start at the low end of moderate"]}
```

(Coach: `use_rpe_not_hr` is true, so no resting pulse or peak heart rate is asked. The review interval stays at the default 6 months.)

**Coach (final message):**

Listo, este es tu perfil y tu punto de partida.

**Lo que he guardado**
- Idioma: español. Región: España (las listas de alimentos están pensadas para España).
- Sexo: mujer. Nacimiento: 1992-03-14. Altura: 168.0 cm. Peso: 66.0 kg.
- Objetivo: perder grasa. Experiencia: intermedia. Actividad: sedentaria con entrenamiento ocasional (oficina, 3 sesiones por semana).
- Medicación: betabloqueante. Condición: hipertensión.
- Cribado completado; sin tensión registrada todavía.
- Recordatorio: te sugeriré refrescar la evidencia del coach cada 6 meses.

**Tus objetivos de partida**
- Calorías: 1500 kcal al día. Es una estimación inicial: la corregiremos con tu tendencia de peso después de 2-4 semanas [nutrition.md: "Recalibrate TDEE from the weight trend"].
- Proteína: 132.0 g. Grasa: 41.67 g (mínimo 33.33 g). Hidratos: 149.25 g. Fibra: 25 g [nutrition.md: "Protein during fat loss"].
- Intensidad (por sensación de esfuerzo y test del habla, no por pulsaciones):
  - Ligera: esfuerzo 9-11, puedes hablar y cantar.
  - Moderada: esfuerzo 12-13, puedes hablar, pero no cantar.

**Lo que cambia lo que debes hacer**
- Tomas un betabloqueante, que limita las pulsaciones, así que no uso zonas por frecuencia cardiaca. Sin esfuerzo sostenido de 14 o más sin visto bueno médico; empieza en la parte baja de la zona moderada [cardio-health.md: "Beta-blockers: no formula-based HR zones"; "RPE as the anchor under beta-blockade"].
- Tienes hipertensión y no tenemos una lectura de tensión, así que toca revisión con tu médico de cabecera antes de empezar o progresar, y de momento solo trabajo ligero a moderado [recovery-habits.md: "Resting BP thresholds to defer or refer"]. Mídete la tensión una vez, sentada y tras 5 minutos de reposo, y dámela en tu próximo `/checkin`.

**Siguientes pasos**
- `/checkin` casi todos los días.
- `/import` para traer tus entrenamientos exportados.
- `/plan` para tu plan de entrenamiento: puedes pedirlo ya, pero la revisión de tu médico va primero.

Esto es orientación general de un entrenador automatizado, no consejo médico. Por lo que me has contado, habla con tu médico (o con el profesional que te indico arriba) antes de ponerlo en práctica.
