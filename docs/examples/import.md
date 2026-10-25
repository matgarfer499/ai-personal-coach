# /import dry run

The client is synthetic (tests/skills/import/client.md). Run date: 2026-10-24.

**Cliente:** Te paso mis entrenos de las últimas 4 semanas: tests/skills/import/workouts.csv. Los apunto en una hoja de cálculo, no en una app.

**Coach:** (Leo el perfil para saber el idioma y reviso la seguridad antes de importar.)

```
$ coach profile show
{"profile": {"sex": "female", "birth_date": "1992-03-14", "height_cm": 168.0, "weight_kg": 66.0, "goal": "fat_loss", "experience": "intermediate", "activity_level": "desk", "language": "es", "region": "es", "medications": ["beta_blocker"], "conditions": ["hypertension"], "screening": {...}, "research_reminder_months": 6}, "missing": [], "unrecognised": {"medications": [], "conditions": []}}
```

```
$ coach safety
{"screened": true, "no_deficit": false, "no_weight_targets": false, "hold_deficit": false, "use_rpe_not_hr": true, "prescriber_owns_weight": false, "refer_gp": false, "no_training": false, "cap_moderate": false, "reasons": ["cardio-health.md: \"Beta-blockers: no formula-based HR zones\": prescribe by RPE and the talk test"]}
```

**Coach:** Vale, importo el archivo tal y como está, sin copiarlo ni tocarlo.

```
$ coach import tests/skills/import/workouts.csv
{"importer": "generic_csv", "read": 144, "added": 144, "duplicates": 0, "first_day": "2026-09-21", "last_day": "2026-10-16", "warnings": []}
```

(El importador se detectó solo como `generic_csv`, así que no hace falta preguntar de qué app viene. Hay series añadidas, así que cuento las series de la última semana.)

```
$ coach strength sets --week-ending 2026-10-16
{"week": {"start": "2026-10-10", "end": "2026-10-16"}, "sets": {"quads": 6.0, "glutes": 4.5, "adductors": 3.0, "chest": 6.0, "triceps": 4.5, "front_delts": 6.0, "back": 6.0, "biceps": 3.0, "rear_delts": 3.0, "hamstrings": 6.0}, "unmapped": [], "reference_sets_per_week": 10}
```

```
$ coach knowledge section strength-hypertrophy "Weekly sets per muscle (dose-response)"
### Weekly sets per muscle (dose-response)
**Rule:** For a client whose priority is muscle gain and who has time, move each major muscle toward roughly 10 or more hard weekly sets over time, ... Treat 10 as a better-than-lower reference point, not a hard minimum; fewer sets still work. ... For strength or health goals, fewer sets suffice because returns diminish quickly.
**Grade:** strong
...
```

**Coach:** Importado, Lucía.

- Leídas: 144 series. Añadidas: 144. Duplicadas: 0.
- Del 2026-09-21 al 2026-10-16.
- Sin avisos.

Series duras de la última semana (del 2026-10-10 al 2026-10-16). El trabajo indirecto cuenta como media serie, por eso salen valores como 4.5:

| Músculo | Series |
|---|---|
| Cuádriceps | 6.0 |
| Glúteos | 4.5 |
| Aductores | 3.0 |
| Pecho | 6.0 |
| Tríceps | 4.5 |
| Deltoides anterior | 6.0 |
| Espalda | 6.0 |
| Bíceps | 3.0 |
| Deltoides posterior | 3.0 |
| Isquiotibiales | 6.0 |

La referencia es 10 series por músculo y semana. Es una referencia para ganar músculo, no un mínimo: con tu objetivo (perder grasa) o si buscas fuerza o salud, bastan menos series [Weekly sets per muscle (dose-response)]. Todos tus ejercicios están en el mapa de músculos; ninguno queda sin contar.

Una nota aparte y corta: al tomar betabloqueantes no se usan zonas de pulso calculadas con fórmula; se dosifica el cardio por esfuerzo percibido y test del habla [Beta-blockers: no formula-based HR zones].

**Cliente:** Ups, creo que te lo he mandado dos veces, vuelve a importarlo por si acaso.

**Coach:** Sin problema, repito la importación; las series ya guardadas se saltan.

```
$ coach import tests/skills/import/workouts.csv
{"importer": "generic_csv", "read": 144, "added": 0, "duplicates": 144, "first_day": "2026-09-21", "last_day": "2026-10-16", "warnings": []}
```

(No se añadió nada, así que se omite el recuento semanal. El motivo de seguridad ya se dio en esta conversación y no se repite.)

## Final message (coach)

Hecho: no ha pasado nada raro. Esta segunda vez leí 144 series, añadí 0 y las 144 salieron como duplicadas, así que tu registro no ha cambiado (sigue del 2026-09-21 al 2026-10-16, sin avisos). Puedes volver a pasarme el archivo cuando quieras; lo ya guardado se salta solo.
