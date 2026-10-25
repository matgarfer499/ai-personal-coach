"""Runs the worked example in docs/adding-an-importer.md so the doc cannot drift."""

import re
from datetime import datetime
from pathlib import Path

import pytest

from coach.sessions.importers import base

DOC = Path(__file__).parent.parent.parent / "docs" / "adding-an-importer.md"


def test_worked_example_runs(tmp_path, monkeypatch):
    blocks = re.findall(r"```python\n(.*?)```", DOC.read_text(encoding="utf-8"), re.S)
    example = next(b for b in blocks if "class LiftLogCsv" in b)
    monkeypatch.setattr(base, "IMPORTERS", list(base.IMPORTERS))
    namespace: dict = {}
    exec(compile(example, str(DOC), "exec"), namespace)

    export = tmp_path / "liftlog.csv"
    export.write_text(
        "Day,Lift,Set,Kg,Reps,Warmup\n"
        "2025-08-20,Squat,1,40,10,yes\n"
        "2025-08-20,Squat,2,80,6,no\n"
        "2025-08-20,Pull Up,1,,8,no\n"
    )
    importer = base.detect(export)
    assert importer.name == "liftlog_csv"
    sets = importer.read(export)
    assert [(s.exercise, s.exercise_index, s.set_index, s.set_type) for s in sets] == [
        ("Squat", 0, 0, "warmup"),
        ("Squat", 0, 1, "normal"),
        ("Pull Up", 1, 0, "normal"),
    ]
    assert sets[0].start_time == datetime(2025, 8, 20)
    assert sets[2].weight_kg is None
    bad = tmp_path / "bad.csv"
    bad.write_text("Day,Lift,Set,Kg,Reps,Warmup\nmonday,Squat,1,40,10,no\n")
    with pytest.raises(base.ImporterError):
        importer.read(bad)
    code_lines = [line for line in example.strip().splitlines() if line.strip()]
    assert len(code_lines) <= 45
