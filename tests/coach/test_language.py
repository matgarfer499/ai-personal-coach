"""Beta 3 p1-lucia-N6, N7, N8, p4-sara-N12, p1-lucia-I4/I5 (b2): the CLI's own sentences follow
the profile language, with a decimal comma in Spanish."""

import json
from datetime import date

import pytest

from coach.checkins import Checkin, weight_jump
from coach.cli import main
from coach.profile import Profile, save_profile
from coach.text import number
from coach.trend import weight_trend

TODAY = "2026-11-08"


@pytest.fixture
def data_dir(tmp_path):
    save_profile(
        Profile(
            sex="female",
            birth_date=date(1988, 1, 1),
            height_cm=162,
            weight_kg=82,
            goal="fat_loss",
            activity_level="desk",
            language="es",
            region="es",
            screening={"scoff_positive": False, "parq_any_yes": False},
        ),
        tmp_path / "profile.yaml",
    )
    return tmp_path


def run(capsys, data_dir, *args):
    code = main(["--data-dir", str(data_dir), "--today", TODAY, *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_number_uses_a_decimal_comma_in_spanish():
    assert number(65.61, "es") == "65,61"
    assert number(65.61, "en") == "65.61"
    assert number(1.6, "es") == "1,6" and number(25.0, "es") == "25"


def test_trend_notes_in_spanish():
    out = weight_trend([(date(2026, 11, 1), 82.0)], language="es")
    assert out.notes[0].startswith("Aún no hay datos para ver la tendencia: faltan 6 pesajes")
    assert weight_trend([], language="es").notes == ["sin pesajes"]


def test_weight_jump_in_spanish():
    text = weight_jump(
        Checkin(date=date(2026, 11, 2), weight_kg=99.5),
        [Checkin(date=date(2026, 11, 1), weight_kg=72.0)],
        language="es",
    )
    assert "99,5 kg" in text and "comprueba" in text


def test_a_future_checkin_is_refused_in_spanish(capsys, data_dir):
    code, out = run(capsys, data_dir, "checkin", "add", "--date", "2026-11-18", "--weight", "82")
    assert code == 2 and "es posterior a hoy" in out["message"]


def test_the_protein_note_uses_a_decimal_comma(capsys, data_dir):
    _, out = run(capsys, data_dir, "macros")
    note = next(n for n in out["notes"] if n.startswith("convención"))
    assert "65,61 kg" in note and "1,6 g" in note


def test_the_veg_and_fruit_warning_is_spanish(capsys, data_dir):
    _, out = run(capsys, data_dir, "menu", "--targets", "--item", "pechuga de pollo, cruda=150")
    assert any(w.startswith("Ese día las comidas planificadas suman") for w in out["warnings"])


def test_a_stale_plan_says_so_in_spanish(capsys, data_dir):
    (data_dir / "plan.md").write_text(
        "Fecha: 2026-11-01\ntarget_kcal: 1600\nin_deficit: true\n", encoding="utf-8"
    )
    run(capsys, data_dir, "checkin", "add", "--symptoms", "dizzy")
    _, out = run(capsys, data_dir, "plan", "check")
    assert any(p.startswith("El plan anterior ya no vale") for p in out["problems"])
