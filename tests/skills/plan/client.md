# Synthetic client for the /plan dry run

Invented person (the same "Lucía" as tests/skills/state/profile.yaml); no real data. Start state:
copy tests/skills/state/ into the run's data dir, then (as setup, outside the skill) run
`uv run python -m coach --data-dir DATA import tests/skills/import/workouts.csv`. If the coach asks
something not listed here, the client answers "no lo sé".

Opening message: "¿Me haces un plan para las próximas semanas?"

Answers if asked:
- Días disponibles: lunes, miércoles y viernes, 1 hora en el gimnasio; sábado o domingo puede
  caminar o ir en bici.
- Material: gimnasio completo (barras, mancuernas, poleas, máquinas).
- Le gusta: sentadilla, press de banca, remo. No le gusta: correr.
- Lesiones: ninguna.
