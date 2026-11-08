# /setup dry run: positive eating-disorder screen

> [!NOTE]
> Recorded before the ACSM 2015 screen became the default (beta-2 fixes, 2026-11-08). /setup now
> asks three ACSM questions (regular exercise, known disease, warning symptoms) and offers the
> PAR-Q+ only as an optional link; the PAR-Q+ steps below show that optional path.

> **What is not verbatim:** CLI outputs are as the CLI printed them, except where shortened with `...` (long `knowledge section` and `profile set` outputs, cut to the part that matters) and where the scratch data folder path is shown as `DATA`. Commands are normalised for reading: `--json` is left out and quoting is added where a shell needs it. The dialogue is a simulation of a model following the skill, not a recording of a real conversation.

The client is synthetic (`tests/skills/setup/client-positive-screen.md`); dry run on 2026-11-02 with the current skill. DATA below stands for an empty scratch directory (`COACH_DATA_DIR`, as the skill says: no `--data-dir`). `profile set` outputs are trimmed to the `screening` block and `missing`.

---

```
$ coach profile show
{"data_dir": "DATA", "profile": {"sex": null, "birth_date": null, "height_cm": null, "weight_kg": null, "goal": null, "experience": null, "activity_level": null, "pal_override": null, "language": null, "region": null, "emergency_number": null, "medications": [], "conditions": [], "screening": {}, "injuries": [], "research_reminder_months": 6}, "missing": ["sex", "birth_date", "height_cm", "weight_kg", "goal", "experience", "activity_level", "language", "region", "emergency_number"], "unrecognised": {"medications": [], "conditions": []}}
```

**Coach:** Hola, vamos a preparar tu perfil (Hi, let's set up your profile). ¿Prefieres que hablemos en español (es) o en inglés (en)? / Would you rather talk in Spanish (es) or English (en)? ¿Y dónde vives?

**Cliente:** Español. Vivo en Valencia.

```
$ coach profile set language es
... "screening": {} ... "missing": ["sex", "birth_date", "height_cm", "weight_kg", "goal", "experience", "activity_level", "region", "emergency_number"], "unrecognised": {"medications": [], "conditions": []}}
$ coach profile set region es
... "screening": {} ... "missing": ["sex", "birth_date", "height_cm", "weight_kg", "goal", "experience", "activity_level", "emergency_number"], "unrecognised": {"medications": [], "conditions": []}}
```

**Coach:** Perfecto, seguimos en español. ¿A qué número llamas en una emergencia donde vives?

**Cliente:** No lo sé.

**Coach:** Te guardo el de tu región, el 112; compruébalo por si acaso.

```
$ coach profile set emergency_number 112
... "screening": {} ... "missing": ["sex", "birth_date", "height_cm", "weight_kg", "goal", "experience", "activity_level"], "unrecognised": {"medications": [], "conditions": []}}
```

**Coach:** Antes de hablar de números, unas preguntas sobre tu relación con la comida. No son un diagnóstico, solo una forma de conversar y de ajustar bien lo que te propongo. Contéstame con sinceridad, sí o no a cada una:
- ¿Alguna vez te provocas el vómito porque te sientes incómodamente llena?
- ¿Te preocupa perder el control sobre cuánto comes?
- ¿Te sientes gorda aunque los demás te digan que estás delgada?
- ¿La comida o el peso dominan tus pensamientos o tu vida?
- ¿Has perdido hace poco mucho peso, de forma que te preocupara a ti o a otras personas?

**Cliente:** Sí a "la comida o el peso dominan mis pensamientos" y sí a "me preocupa perder el control de lo que como". No al resto.

(Coach: two clear yes answers, so `scoff_yes_count` is 2; the CLI applies the cut point. The loss-of-control yes could be a warning sign, so the coach asks one follow-up.)

**Coach:** Gracias por contármelo, de verdad. Sobre lo de perder el control: ¿te pasa que comes mucho de golpe y sientes que no puedes parar?

**Cliente:** No lo sé.

(Coach: an unclear answer is not counted as a warning sign, so `scoff_positive` stays `false`; the count of 2 is positive by itself.)

```
$ coach profile set screening.scoff_yes_count 2
$ coach profile set screening.scoff_positive false
... "screening": {"scoff_yes_count": 2, "scoff_positive": false} ... "missing": ["sex", "birth_date", "height_cm", "weight_kg", "goal", "experience", "activity_level"], "unrecognised": {"medications": [], "conditions": []}}
$ coach safety
{"screened": true, "no_deficit": true, "no_weight_targets": true, "hold_deficit": false, "use_rpe_not_hr": false, "prescriber_owns_weight": false, "refer_gp": true, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": false, "review_before_vigorous": true, "no_all_out_sprints": true, "emergency_number": "112", "paused_exercises": {}, "reasons": ["nutrition.md: \"Eating-disorder screening: brief questions as a prompt\": positive screen (2 or more yes answers) or a warning sign, so no deficit, weight targets or weigh-ins; suggest a GP or eating-disorder professional", "recovery-habits.md: \"PAR-Q+ specific thresholds\": PAR-Q+ not answered, so no all-out sprint formats (SIT, REHIT); they need every answer NO", "recovery-habits.md: \"PAR-Q+ specific thresholds\": PAR-Q+ not answered, so light-to-moderate work only until it is"]}
```

**Coach:** Con lo que me cuentas, el resultado de esta parte es "positivo": no es un diagnóstico, pero a partir de ahora no te propondré ningún déficit de calorías, ningún objetivo de peso ni pesarte, y te recomendaré hablarlo con un profesional. Sigamos con lo básico: ¿cuál es tu sexo (las ecuaciones que uso solo existen para mujer y para hombre), tu fecha de nacimiento y cuánto mides?

**Cliente:** Mujer, nací el 2 de junio de 1999 y mido 163 cm. El peso prefiero no decirlo.

```
$ coach profile set sex female
$ coach profile set birth_date 1999-06-02
$ coach profile set height_cm 163
... "screening": {"scoff_yes_count": 2, "scoff_positive": false} ... "missing": ["weight_kg", "goal", "experience", "activity_level"], "unrecognised": {"medications": [], "conditions": []}}
```

**Coach:** Sin problema, no hace falta que te peses ni que lo busques. Solo si te sientes cómoda, ¿podrías darme un peso aproximado, lo que tú creas? Lo uso únicamente para las estimaciones; si prefieres no hacerlo, lo dejamos.

**Cliente:** Unos 58 kg.

```
$ coach profile set weight_kg 58
... "screening": {"scoff_yes_count": 2, "scoff_positive": false} ... "missing": ["goal", "experience", "activity_level"], "unrecognised": {"medications": [], "conditions": []}}
```

**Coach:** Gracias. Ahora el cuestionario de aptitud para la actividad física PAR-Q+ (el oficial, en https://eparmedx.com; no se puede cambiar). Si ya lo has rellenado, dime: ¿has contestado SÍ a alguna de las 7 preguntas? ¿Y a alguna de las preguntas de las páginas de seguimiento?

**Cliente:** Lo he rellenado. Todo NO, en las 7 preguntas y en las de seguimiento.

```
$ coach profile set screening.parq_any_yes false
$ coach profile set screening.parq_followup_yes false
... "screening": {"scoff_yes_count": 2, "scoff_positive": false, "parq_any_yes": false, "parq_followup_yes": false} ... "missing": ["goal", "experience", "activity_level"], "unrecognised": {"medications": [], "conditions": []}}
```

(Coach: all NO and under 45, so no review before vigorous work is asked.)

**Coach:** Bien. Ahora unos síntomas que conviene descartar. ¿Has notado dolor u opresión en el pecho, el cuello, la mandíbula o el brazo; falta de aire en reposo o con esfuerzos pequeños; mareos o desmayos; palpitaciones; hinchazón de tobillos; o dolor en las pantorrillas al caminar?

```
$ coach knowledge section recovery-habits "Cardiac warning symptoms: stop and refer"
### Cardiac warning symptoms: stop and refer
**Rule:** If a user reports any of the symptoms below, before or during a session, tell them to stop exercising and seek medical evaluation. ... Separately, as general first-aid practice rather than ACSM text: chest pain at rest, fainting, or chest pain with breathlessness and sweating means calling emergency services now.
...
**Grade:** moderate
```

**Cliente:** Ninguno.

```
$ coach profile set screening.cardiac_symptoms false
... "screening": {"scoff_yes_count": 2, "scoff_positive": false, "parq_any_yes": false, "parq_followup_yes": false, "cardiac_symptoms": false} ... "missing": ["goal", "experience", "activity_level"], "unrecognised": {"medications": [], "conditions": []}}
```

**Coach:** Perfecto. ¿Tomas alguna medicación o tienes algún diagnóstico? Y, ¿estás embarazada o buscando un embarazo? Si conoces tu tensión arterial (la última medida sentada, tras 5 minutos de reposo), dímela también.

**Cliente:** Ninguna medicación, ningún diagnóstico, no estoy embarazada. La tensión no lo sé.

(Nothing stored: no token means no medications, conditions or pregnancy, and no blood pressure reading is given, so `bp_systolic` and `bp_diastolic` stay unset.)

**Coach:** Vale. Sobre el ciclo: ¿tus reglas son regulares, han pasado a ser irregulares hace poco, o llevas 3 meses o más sin regla (o menos de 6 al año)? ¿Usas anticoncepción hormonal?

**Cliente:** Regular. Lo de la anticoncepción no lo sé.

```
$ coach profile set screening.menstrual normal
... "screening": {"scoff_yes_count": 2, "scoff_positive": false, "parq_any_yes": false, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal"} ... "missing": ["goal", "experience", "activity_level"], "unrecognised": {"medications": [], "conditions": []}}
```

**Coach:** Anotado. Una cosa por si acaso: si usas anticoncepción hormonal, esta enmascara el ciclo, así que si notas poca energía, poco deseo o una lesión por estrés en un hueso, cuéntamelo en el `/checkin`. Ahora tu objetivo y tu entrenamiento: ¿qué te gustaría conseguir? ¿Entrenas ahora o lo dejaste, y desde cuándo? ¿Cuántos días a la semana? ¿Cómo es tu día a día (trabajo o estudios, cuánto te mueves)? ¿Tienes alguna lesión o dolor ahora mismo?

**Cliente:** Quiero perder 5 kilos lo antes posible. Soy novata, empecé en el gimnasio hace 2 meses, 3 días por semana. Soy estudiante y estoy sentada casi todo el día. Lesiones, no lo sé.

(Coach: the goal is stored as `fat_loss`, as she said it; the CLI gives maintenance whatever the goal. Two months of training is `novice`. An unsure answer on injuries records none. Desk life and 3 sessions a week is `desk`.)

```
$ coach profile set goal fat_loss
$ coach profile set experience novice
$ coach profile set activity_level desk
... "screening": {"scoff_yes_count": 2, "scoff_positive": false, "parq_any_yes": false, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal"} ... "missing": [], "unrecognised": {"medications": [], "conditions": []}}
```

```
$ coach knowledge section nutrition "Activity multipliers (PAL)"
### Activity multipliers (PAL)
**Rule:** Multiply estimated RMR by a PAL: about 1.4-1.5 (up to 1.6) for desk workers with little exercise or a few short sessions a week; ...
...
```

```
$ coach profile show
{"data_dir": "DATA", "profile": {"sex": "female", "birth_date": "1999-06-02", "height_cm": 163.0, "weight_kg": 58.0, "goal": "fat_loss", "experience": "novice", "activity_level": "desk", "pal_override": null, "language": "es", "region": "es", "emergency_number": "112", "medications": [], "conditions": [], "screening": {"scoff_yes_count": 2, "scoff_positive": false, "parq_any_yes": false, "parq_followup_yes": false, "cardiac_symptoms": false, "menstrual": "normal"}, "injuries": [], "research_reminder_months": 6}, "missing": [], "unrecognised": {"medications": [], "conditions": []}}
```

`missing` is empty and nothing is unrecognised.

```
$ coach safety
{"screened": true, "no_deficit": true, "no_weight_targets": true, "hold_deficit": false, "use_rpe_not_hr": false, "prescriber_owns_weight": false, "refer_gp": true, "no_training": false, "cap_moderate": false, "no_calorie_targets": false, "hold_progression": false, "review_before_vigorous": false, "no_all_out_sprints": false, "emergency_number": "112", "paused_exercises": {}, "reasons": ["nutrition.md: \"Eating-disorder screening: brief questions as a prompt\": positive screen (2 or more yes answers) or a warning sign, so no deficit, weight targets or weigh-ins; suggest a GP or eating-disorder professional"]}

$ coach energy
{"rmr": 1302.75, "tdee": 1888.99, "target": {"kcal": 1889, "maintenance": 1888.99, "deficit": 0, "clamped": false, "notes": ["nutrition.md: \"Recalibrate TDEE from the weight trend\": starting estimate from an equation", "nutrition.md: \"Eating-disorder screening: brief questions as a prompt\": positive screen (2 or more yes answers) or a warning sign, so no deficit, weight targets or weigh-ins; suggest a GP or eating-disorder professional"]}}

$ coach macros
{"in_deficit": false, "kcal": 1889, "protein_g": 92.8, "fat_g": 52.47, "fat_min_g": 41.98, "carbs_g": 261.39, "fibre_g": 25, "protein_g_per_kg": 1.6, "notes": ["nutrition.md: \"Daily protein target for people who lift\": 1.6 g/kg/day"]}

$ coach zones
{"method": "hrmax", "zones": [{"name": "light", "rpe": [9, 11], "talk_test": "can talk and sing", "bpm": [108, 119]}, {"name": "moderate", "rpe": [12, 13], "talk_test": "can talk, but not sing", "bpm": [121, 144]}, {"name": "vigorous", "rpe": [14, 17], "talk_test": "only a few words without pausing for breath", "bpm": [146, 180]}], "hr_max": 189, "hr_max_source": "tanaka", "hr_rest": null, "notes": ["cardio-health.md: \"ACSM intensity bands\": zones are approximate; check them against RPE and the talk test", "cardio-health.md: \"HRmax: formulas and setting the anchor\": HRmax from Tanaka is a rough start and can be off by 20+ bpm; use an observed all-out peak when you have one"]}
```

`use_rpe_not_hr` is false, so the coach asks for the two pulse readings.

**Coach:** Última cosa antes de darte el resumen: para afinar las zonas de intensidad, si lo sabes, dime tu pulso en reposo por la mañana y el pulso máximo que hayas visto en un esfuerzo a tope. Si no los sabes, no pasa nada.

**Cliente:** No lo sé.

(Both skipped; `zones` is not rerun, the output above stands.)

**Coach (final message):**

Tu perfil está listo. Esto es lo que he guardado y lo que te propongo.

**Lo que he guardado**
- Idioma español, región España y el número de emergencias 112.
- Sexo, fecha de nacimiento, altura y un peso aproximado (solo para las estimaciones).
- Los resultados de los cribados de salud (alimentación, PAR-Q+, síntomas cardiacos y ciclo).
- Sin medicación, sin diagnósticos, sin embarazo.
- Tu objetivo tal como me lo has contado, tu experiencia (novata) y tu actividad diaria (sentada, entrenando unos días a la semana).

**Objetivos de partida**
- Calorías: 1889 kcal al día. Es lo que el programa calcula para mantenerte, sin déficit.
- Proteína: 92,8 g. Grasa: 52,47 g. Hidratos de carbono: 261,39 g. Fibra: 25 g.
- Zonas de intensidad (aproximadas; contrástalas con el esfuerzo percibido y con la prueba del habla):
  - Ligera: esfuerzo 9 a 11, puedes hablar y cantar, 108 a 119 pulsaciones por minuto.
  - Moderada: esfuerzo 12 a 13, puedes hablar pero no cantar, 121 a 144 pulsaciones por minuto.
  - Vigorosa: esfuerzo 14 a 17, solo unas pocas palabras sin parar a respirar, 146 a 180 pulsaciones por minuto.
- El pulso máximo de partida, 189, sale de una fórmula (Tanaka) y puede fallar en 20 o más pulsaciones; si algún día lo observas en un esfuerzo a tope, lo afinamos.

**Lo que debes saber**
- [nutrition.md: "Eating-disorder screening: brief questions as a prompt"] Por lo que me has contado sobre la comida, no te propongo ningún déficit de calorías, ningún objetivo de peso ni pesarte; las calorías de arriba son de mantenimiento. Te recomiendo hablarlo con tu médico de cabecera o con un profesional de trastornos de la conducta alimentaria. No es un diagnóstico, es una forma de cuidarte, y su valoración va primero en todo lo relacionado con tu objetivo de peso.
- Si usas anticoncepción hormonal, enmascara el ciclo: cuéntame en el `/checkin` si notas poca energía, poco deseo o una lesión por estrés en un hueso.
- Si te falta aire en reposo, notas dolor en el pecho o te desmayas, para y busca atención médica (112 si es dolor de pecho en reposo, desmayo, o dolor de pecho con falta de aire y sudor).

**Siguientes pasos**
- `/checkin` casi todos los días (sin peso ni medidas).
- `/import` para traerme tus exportaciones de entrenamientos.
- `/plan` para el plan de entrenamiento: puedes pedirlo, pero primero va la valoración del profesional que te he nombrado.
- Cada 6 meses te sugeriré refrescar la evidencia en la que me baso.

Esto es orientación general de un entrenador automatizado, no consejo médico. Por lo que me has contado, habla con tu médico (o con el profesional que te indico arriba) antes de ponerlo en práctica.
