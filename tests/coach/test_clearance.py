"""Beta 3 p3-antonio-N6, p6-james-N11, p1-lucia-N10, p1-lucia-N11: the documented way out of a
symptom stop is `coach clearance add`, a clinician's clearance with a date and a note."""

import json
from datetime import date

import pytest

from coach import safety as safety_rules
from coach.cli import main
from coach.profile import Profile, load_profile, save_profile

TODAY = "2026-03-15"


@pytest.fixture
def data_dir(tmp_path):
    save_profile(
        Profile(
            sex="male",
            birth_date=date(1974, 4, 1),
            height_cm=175,
            weight_kg=90,
            goal="fat_loss",
            activity_level="desk",
            language="es",
            region="es",
            screening={
                "scoff_positive": False,
                "parq_any_yes": False,
                "regular_exercise": False,
                "known_disease": [],
                "symptoms": [],
            },
        ),
        tmp_path / "profile.yaml",
    )
    return tmp_path


def run(capsys, data_dir, *args):
    code = main(["--data-dir", str(data_dir), "--today", TODAY, *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def stop(capsys, data_dir, on="2026-03-10"):
    run(capsys, data_dir, "checkin", "add", "--date", on, "--symptoms", "chest_pain")


def plan(data_dir):
    (data_dir / "plan.md").write_text(
        "Fecha: 2026-03-01\ntarget_kcal: 2000\nin_deficit: true\n\n"
        "## Semana de entrenamiento\n- A (lunes): Sentadilla 3x8 40 kg\n",
        encoding="utf-8",
    )


def test_a_symptom_records_its_date(capsys, data_dir):
    stop(capsys, data_dir)
    screening = load_profile(data_dir / "profile.yaml").screening
    assert screening["cardiac_symptoms"] is True
    assert screening["symptoms_on"] == date(2026, 3, 10)


def test_clearance_lifts_the_symptom_stop_but_not_the_review(capsys, data_dir):
    stop(capsys, data_dir)
    code, out = run(
        capsys,
        data_dir,
        "clearance",
        "add",
        "--by",
        "GP",
        "--date",
        "2026-03-14",
        "--note",
        "ECG normal, may exercise",
    )
    assert code == 0, out
    _, safety = run(capsys, data_dir, "safety")
    assert safety["no_training"] is False and safety["refer_gp"] is False
    assert safety["review_before_vigorous"] is True
    assert safety["emergency_line"] is None
    screening = load_profile(data_dir / "profile.yaml").screening
    assert screening["cleared_on"] == date(2026, 3, 14) and screening["cleared_by"] == "GP"
    assert screening["clearance_note"] == "ECG normal, may exercise"


@pytest.mark.parametrize(
    ("when", "word"), [("2026-03-09", "before"), ("2026-03-16", "after today")]
)
def test_clearance_dated_before_the_symptom_or_in_the_future_is_refused(
    capsys, data_dir, when, word
):
    stop(capsys, data_dir)
    code, out = run(
        capsys, data_dir, "clearance", "add", "--by", "GP", "--date", when, "--note", "ok"
    )
    assert code == 2 and word in out["message"]
    _, safety = run(capsys, data_dir, "safety")
    assert safety["no_training"] is True


def test_clearance_needs_who_and_a_note(capsys, data_dir):
    stop(capsys, data_dir)
    code, _ = run(capsys, data_dir, "clearance", "add", "--by", "GP", "--date", "2026-03-14")
    assert code == 2
    code, _ = run(
        capsys, data_dir, "clearance", "add", "--by", " ", "--date", "2026-03-14", "--note", "ok"
    )
    assert code == 2


def test_new_symptoms_after_clearance_stop_training_again(capsys, data_dir):
    stop(capsys, data_dir)
    run(capsys, data_dir, "clearance", "add", "--by", "GP", "--date", "2026-03-14", "--note", "ok")
    stop(capsys, data_dir, on="2026-03-15")
    _, safety = run(capsys, data_dir, "safety")
    assert safety["no_training"] is True
    assert "cleared_on" not in load_profile(data_dir / "profile.yaml").screening


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("screening.cardiac_symptoms", "false"),
        ("screening.cardiac_symptoms", "none"),
        ("screening.symptoms", "no"),
        ("screening.medically_cleared", "true"),
        ("screening.cleared_on", "2026-03-14"),
    ],
)
def test_profile_set_cannot_lift_the_stop(capsys, data_dir, field, value):
    stop(capsys, data_dir)
    run(capsys, data_dir, "profile", "set", "screening.symptoms", "chest_pain")
    code, out = run(capsys, data_dir, "profile", "set", field, value)
    assert code == 2 and "coach clearance" in out["message"]
    _, safety = run(capsys, data_dir, "safety")
    assert safety["no_training"] is True


def test_checkin_symptoms_no_points_to_clearance(capsys, data_dir):
    code, out = run(capsys, data_dir, "checkin", "add", "--symptoms", "no")
    assert code == 2 and "coach clearance" in out["message"]


def test_clearance_does_not_lift_a_bp_stop(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.bp_systolic", "185")
    stop(capsys, data_dir)
    run(capsys, data_dir, "clearance", "add", "--by", "GP", "--date", "2026-03-14", "--note", "ok")
    _, safety = run(capsys, data_dir, "safety")
    assert safety["no_training"] is True


def test_clearance_with_nothing_to_clear_is_refused(capsys, data_dir):
    code, out = run(
        capsys, data_dir, "clearance", "add", "--by", "GP", "--date", "2026-03-14", "--note", "ok"
    )
    assert code == 2 and "nothing" in out["message"]


def test_clearance_covers_the_acsm_disease_cell(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.known_disease", "metabolic")
    _, safety = run(capsys, data_dir, "safety")
    assert safety["no_training"] is True and safety["clearance_before_exercise"] is True
    run(
        capsys,
        data_dir,
        "clearance",
        "add",
        "--by",
        "endocrinologist",
        "--date",
        "2026-03-14",
        "--note",
        "ok",
    )
    _, safety = run(capsys, data_dir, "safety")
    assert safety["no_training"] is False and safety["review_before_vigorous"] is True


def test_plan_md_is_suspended_while_training_stops(capsys, data_dir):
    plan(data_dir)
    stop(capsys, data_dir)
    text = (data_dir / "plan.md").read_text(encoding="utf-8")
    assert "## Plan suspendido" in text and text.startswith("Fecha: 2026-03-01\n")
    stop(capsys, data_dir)  # a second report keeps one section
    assert (data_dir / "plan.md").read_text(encoding="utf-8").count("## Plan suspendido") == 1
    _, check = run(capsys, data_dir, "plan", "check")
    assert check["ok"] is False
    run(capsys, data_dir, "clearance", "add", "--by", "GP", "--date", "2026-03-14", "--note", "ok")
    text = (data_dir / "plan.md").read_text(encoding="utf-8")
    assert "Plan suspendido" not in text and "Sentadilla 3x8 40 kg" in text


def test_a_symptom_without_a_plan_writes_no_plan(capsys, data_dir):
    stop(capsys, data_dir)
    assert not (data_dir / "plan.md").exists()


def test_clearance_show(capsys, data_dir):
    stop(capsys, data_dir)
    run(capsys, data_dir, "clearance", "add", "--by", "GP", "--date", "2026-03-14", "--note", "ok")
    code, out = run(capsys, data_dir, "clearance", "show")
    assert code == 0 and out["clearance"]["by"] == "GP" and out["symptoms_on"] == "2026-03-10"


def test_a_review_from_before_the_symptoms_does_not_skip_the_restart(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.vigorous_reviewed", "true")
    stop(capsys, data_dir)
    run(capsys, data_dir, "clearance", "add", "--by", "GP", "--date", "2026-03-14", "--note", "ok")
    _, out = run(capsys, data_dir, "safety")
    assert out["review_before_vigorous"] is True
    # Cited under the ACSM rule, so zones and runs name it when they hold vigorous zones back.
    assert any(r.startswith(safety_rules.ACSM) and "cleared by GP" in r for r in out["reasons"])


def test_a_bp_stop_moots_the_light_to_moderate_restart(capsys, data_dir):
    stop(capsys, data_dir)
    run(capsys, data_dir, "clearance", "add", "--by", "GP", "--date", "2026-03-14", "--note", "ok")
    run(capsys, data_dir, "profile", "set", "screening.bp_systolic", "185")
    _, out = run(capsys, data_dir, "safety")
    assert out["no_training"] is True
    assert not any("cleared by" in r for r in out["reasons"])


def test_the_suspension_keeps_the_day_it_started(capsys, data_dir):
    plan(data_dir)
    run(capsys, data_dir, "profile", "set", "screening.bp_systolic", "185")
    main(
        ["--data-dir", str(data_dir), "--today", "2026-03-20", "profile", "set", "weight_kg", "89"]
    )
    capsys.readouterr()
    text = (data_dir / "plan.md").read_text(encoding="utf-8")
    assert "desde 2026-03-15:" in text and "2026-03-20" not in text
