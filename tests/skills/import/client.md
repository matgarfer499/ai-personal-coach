# Synthetic client for the /import dry run

Invented person (the same "Lucía" as tests/skills/state/profile.yaml); no real data. Start state:
copy tests/skills/state/ into the run's data dir (no sessions.csv yet). If the coach asks something
not listed here, the client answers "no lo sé".

Opening message: "Te paso mis entrenos de las últimas 4 semanas: tests/skills/import/workouts.csv.
Los apunto en una hoja de cálculo, no en una app."

After the coach reports the import, the client says: "Ups, creo que te lo he mandado dos veces,
vuelve a importarlo por si acaso." (Expect 0 added and every set counted as a duplicate.)
