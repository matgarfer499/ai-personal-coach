# Synthetic client for the /review dry run

Invented person (the same "Lucía" as tests/skills/state/profile.yaml); no real data. Start state:
copy tests/skills/state/ into the run's data dir, then (as setup, outside the skill) run
`uv run python -m coach --data-dir DATA import tests/skills/import/workouts.csv`. Run the review
for the week ending 2026-10-18. If the coach asks something not listed here, the client answers
"no lo sé".

Opening message: "¿Hacemos la revisión de la semana?"

Answers if asked:
- Adherencia: ha cumplido las 3 sesiones y la comida casi todos los días.
- Desde hace unas dos semanas duerme peor (6 horas) y le molestan un poco las rodillas al
  entrenar. La motivación está bien; el rendimiento no ha bajado tras descansar; ánimo bien.
- Está contenta con el ritmo de pérdida.
- Lo que come ahora: unas 1.600 kcal al día según la app (no tiene un plan escrito todavía).
- Si el coach propone cambios: acepta la semana de descarga y el nuevo objetivo de calorías.
