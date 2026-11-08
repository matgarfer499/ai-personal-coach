"""PDF export of data/plan.md (needs the optional `pdf` extra: uv sync --extra pdf)."""

import json
import sys
from datetime import date

import pytest

from coach.cli import main
from coach.export import plan_exercises
from coach.profile import Profile, save_profile

PLAN = """Fecha: 2026-11-02
target_kcal: 1500.0
in_deficit: true
training_schedule: mon; wed; fri

# Plan

## Semana de entrenamiento

Lunes, miércoles y viernes, 3 series de 8 a 12 repeticiones [Target reps in reserve].

- A (lunes): Sentadilla 51,0 kg; Press banca 34,0 kg; Remo con barra 34,0 kg.
- B (miércoles): Jalón al pecho 30,0 kg; Peso muerto rumano 42,5 kg.
- C (viernes 18:30): Prensa de piernas 85,0 kg; Press banca 34,0 kg; Zancadas.
- Sentadilla: 6-8 reps

## Cardio

- Sábado: caminar 75 minutos.

## Fuentes

[Target reps in reserve], [Weekly baseline dose].
"""


@pytest.fixture
def data_dir(tmp_path):
    save_profile(
        Profile(
            sex="female",
            birth_date=date(1992, 3, 10),
            height_cm=165,
            weight_kg=62,
            goal="maintenance",
            activity_level="desk",
            language="es",
            region="es",
            screening={"scoff_positive": False},
        ),
        tmp_path / "profile.yaml",
    )
    (tmp_path / "plan.md").write_text(PLAN, encoding="utf-8")
    return tmp_path


def run(capsys, data_dir, *args):
    code = main(["--data-dir", str(data_dir), "--today", "2026-11-02", *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_exercises_come_from_the_training_week_bullets_once_each():
    assert plan_exercises(PLAN) == [
        "Sentadilla",
        "Press banca",
        "Remo con barra",
        "Jalón al pecho",
        "Peso muerto rumano",
        "Prensa de piernas",
        "Zancadas",
    ]


def test_english_plan_and_prose_lines_are_not_exercises():
    text = (
        "Date: 2026-11-02\n## Training week\nSquat 3 sets.\n- A (Mon): Squat 40 kg\n"
        "## Cardio\n- Walk 30 min\n"
    )
    assert plan_exercises(text) == ["Squat"]


def test_export_writes_the_plan_with_a_video_link_per_exercise(capsys, data_dir):
    pytest.importorskip("reportlab")
    code, out = run(capsys, data_dir, "plan", "export")
    assert code == 0, out
    assert out["pdf"] == "plan.pdf" and out["qr"] is True
    assert out["exercises"] == plan_exercises(PLAN)
    data = (data_dir / "plan.pdf").read_bytes()
    assert data.startswith(b"%PDF")
    assert b"Prensa de piernas" in data and b"Cardio" in data
    link = b"https://www.youtube.com/results?search_query=Press+banca+t%C3%A9cnica"
    assert data.count(b"/URI (" + link + b")") == 1  # once, though two sessions use it
    assert b"target_kcal" not in data  # header lines are for the CLI, not the printout


def test_export_in_english_searches_for_technique(capsys, data_dir):
    pytest.importorskip("reportlab")
    run(capsys, data_dir, "profile", "set", "language", "en")
    run(capsys, data_dir, "plan", "export")
    data = (data_dir / "plan.pdf").read_bytes()
    assert b"search_query=Sentadilla+technique" in data and b"t%C3%A9cnica" not in data


def test_export_has_optional_qr_codes_and_an_out_path(capsys, data_dir):
    pytest.importorskip("reportlab")
    run(capsys, data_dir, "plan", "export", "--out", "con-qr.pdf")
    code, out = run(capsys, data_dir, "plan", "export", "--out", "sin-qr.pdf", "--no-qr")
    assert code == 0 and out["qr"] is False
    without_qr = (data_dir / "sin-qr.pdf").read_bytes()
    assert b"youtube.com" in without_qr  # the link is still printed as text
    assert (data_dir / "con-qr.pdf").stat().st_size > len(without_qr)


def test_export_without_a_plan_says_to_run_plan(capsys, data_dir):
    (data_dir / "plan.md").unlink()
    code, out = run(capsys, data_dir, "plan", "export")
    assert code == 2 and "/plan" in out["message"]


def test_export_without_the_extra_says_how_to_install_it(capsys, data_dir, monkeypatch):
    for name in [n for n in sys.modules if n == "reportlab" or n.startswith("reportlab.")]:
        monkeypatch.delitem(sys.modules, name)
    monkeypatch.setitem(sys.modules, "reportlab", None)  # as if it were not installed
    code, out = run(capsys, data_dir, "plan", "export")
    assert code == 2 and "uv sync --extra pdf" in out["message"]
    assert not (data_dir / "plan.pdf").exists()
