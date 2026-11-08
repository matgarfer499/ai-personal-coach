"""Beta 3 p5-elena-N1..N4, p2-marcus-N2, p6-james-N15, p6-james-N13: `coach plan check` reads the
plan's content, not only its header."""

import json
from datetime import date, datetime

import pytest
import yaml

from coach.cli import main
from coach.export import plan_unread
from coach.profile import Profile, save_profile
from coach.runs import Run, append_runs
from coach.sessions.model import ExerciseSet
from coach.sessions.store import append

TODAY = "2026-11-02"


@pytest.fixture
def data_dir(tmp_path):
    save_profile(
        Profile(
            sex="female",
            birth_date=date(1987, 3, 10),
            height_cm=168,
            weight_kg=78,
            goal="fat_loss",
            activity_level="desk",
            language="en",
            region="es",
            screening={
                "scoff_positive": False,
                "parq_any_yes": False,
                "regular_exercise": True,
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


def macros(capsys, data_dir):
    return run(capsys, data_dir, "macros")[1]


WEEK = ["Squat 3x8 60 kg; Bench Press 3x10 40 kg", "Deadlift 3x6 70 kg; Barbell Row 3x10 40 kg"]


def write(
    capsys,
    data_dir,
    week=WEEK,
    nutrition=None,
    cardio="- Saturday: walk 45 minutes.",
    yaml_week=None,
):
    m = macros(capsys, data_dir)
    nutrition = nutrition or (
        f"- Calories: {m['kcal']:g} kcal\n- Protein: {m['protein_g']:.0f} g\n"
        f"- Fat: {m['fat_g']:.0f} g\n- Carbohydrate: {m['carbs_g']:.0f} g\n"
        f"- Fibre: {m['fibre_g']:g} g"
    )
    bullets = "\n".join(f"- {chr(65 + i)} (day {i + 1}): {b}" for i, b in enumerate(week))
    (data_dir / "plan.md").write_text(
        f"Date: {TODAY}\ntarget_kcal: {m['kcal']:g}\nin_deficit: true\n\n"
        f"## Training week\n\n{bullets}\n\n## Cardio\n\n{cardio}\n\n"
        f"## Nutrition\n\n{nutrition}\n\n## Rules used\n\n[Weekly baseline dose]\n",
        encoding="utf-8",
    )
    sessions = yaml_week or [
        {
            "name": chr(65 + i),
            "exercises": [{"exercise": p.strip().split(" 3x")[0], "sets": 3} for p in b.split(";")],
        }
        for i, b in enumerate(week)
    ]
    (data_dir / "plan-week.yaml").write_text(
        yaml.safe_dump({"sessions": sessions}), encoding="utf-8"
    )
    return m


def test_a_coherent_plan_is_ok(capsys, data_dir):
    write(capsys, data_dir)
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is True, out["problems"]


def test_nutrition_outside_the_macros_ranges_is_a_problem(capsys, data_dir):
    write(
        capsys,
        data_dir,
        nutrition="- Calories: 1637 kcal\n- Protein: 300 g\n- Fat: 50 g\n- Fibre: 5 g",
    )
    _, out = run(capsys, data_dir, "plan", "check")
    text = " ".join(out["problems"])
    assert out["ok"] is False and "protein" in text.lower() and "fibre" in text.lower()


def test_a_spanish_nutrition_section_with_decimal_commas_is_read(capsys, data_dir):
    m = write(capsys, data_dir)
    text = (data_dir / "plan.md").read_text(encoding="utf-8")
    protein = f"{m['protein_g']:.1f}".replace(".", ",")
    text = text.replace("## Nutrition", "## Nutrición").split("## Nutrición")[0] + (
        f"## Nutrición\n\n- Proteína: {protein} g\n- Fibra: 2 g\n"
    )
    (data_dir / "plan.md").write_text(text, encoding="utf-8")
    _, out = run(capsys, data_dir, "plan", "check")
    assert any("fibre" in p.lower() for p in out["problems"])
    assert not any("protein" in p.lower() for p in out["problems"])


def test_a_lift_only_in_plan_week_yaml_is_a_problem(capsys, data_dir):
    yaml_week = [
        {
            "name": "A",
            "exercises": [{"exercise": "Squat", "sets": 3}, {"exercise": "Bench Press", "sets": 3}],
        },
        {
            "name": "B",
            "exercises": [
                {"exercise": "Deadlift", "sets": 3},
                {"exercise": "Barbell Row", "sets": 3},
            ],
        },
    ]
    write(capsys, data_dir, week=["Squat 3x8 60 kg", WEEK[1]], yaml_week=yaml_week)
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is False and any("Bench Press" in p for p in out["problems"])


def test_sprints_when_safety_rules_them_out_are_a_problem(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.parq_any_yes", "true")
    write(capsys, data_dir, cardio="- Daily: SIT, 10x30s all-out sprints on the bike.")
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is False and any("sprint" in p.lower() for p in out["problems"])


def test_an_implausible_load_is_a_problem(capsys, data_dir):
    write(capsys, data_dir, week=["Squat 3x8 500 kg; Bench Press 3x10 40 kg", WEEK[1]])
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is False and any("500" in p for p in out["problems"])


def test_a_load_above_the_logged_e1rm_is_a_problem(capsys, data_dir):
    append(
        [
            ExerciseSet(
                source="manual",
                start_time=datetime(2026, 10, 30, 18),
                exercise="Squat",
                exercise_index=0,
                set_index=i,
                weight_kg=60,
                reps=8,
                rir=2,
            )
            for i in range(3)
        ],
        data_dir / "sessions.csv",
    )
    write(capsys, data_dir, week=["Squat 3x8 120 kg; Bench Press 3x10 40 kg", WEEK[1]])
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is False and any("Squat" in p and "120" in p for p in out["problems"])


def test_a_bare_name_that_is_no_lift_is_unread(capsys, data_dir):
    text = "## Training week\n\n- A (Monday): Squat 3x8 60 kg; Mystery Move; Zancadas\n"
    assert plan_unread(text) == ["Mystery Move"]


def test_a_run_longer_than_the_long_run_cap_is_a_problem(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "sport", "both")
    append_runs(
        [Run(date=date(2026, 10, 20 + i), km=8, minutes=48) for i in range(0, 10, 3)],
        data_dir / "runs.csv",
    )
    write(capsys, data_dir, week=[*WEEK, "Long run 18 km easy"])
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is False and any("18" in p and "km" in p for p in out["problems"])


def test_push_up_maps(capsys, data_dir):
    (data_dir / "week.yaml").write_text(
        yaml.safe_dump(
            {"sessions": [{"name": "A", "exercises": [{"exercise": "Push-up", "sets": 3}]}]}
        ),
        encoding="utf-8",
    )
    _, out = run(capsys, data_dir, "strength", "plan-sets", str(data_dir / "week.yaml"))
    assert out["unmapped"] == []


def test_a_prose_bullet_in_the_training_week_is_no_lift_mismatch(capsys, data_dir):
    write(capsys, data_dir, week=[*WEEK])
    text = (data_dir / "plan.md").read_text(encoding="utf-8")
    text = text.replace("\n\n## Cardio", "\n- Rest 2-3 min between sets\n\n## Cardio")
    (data_dir / "plan.md").write_text(text, encoding="utf-8")
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is True, out["problems"]


def test_nutrition_reads_thousands_and_skips_per_kg_and_percent_figures():
    from coach.plancheck import nutrition_numbers

    text = (
        "## Nutrition\n\n- Calories: 1,850 kcal\n- Protein: 1.6 g/kg (125 g)\n"
        "- Fat: 30% of energy (60 g)\n- Fibre: 25 g.\n"
    )
    assert nutrition_numbers(text) == {"kcal": 1850, "protein": 125, "fat": 60, "fibre": 25}


def test_no_more_than_is_a_limit_not_a_prohibition(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.parq_any_yes", "true")
    write(capsys, data_dir, cardio="- Friday: no more than 4 sprints on the bike.")
    _, out = run(capsys, data_dir, "plan", "check")
    assert any("sprint" in p.lower() for p in out["problems"])


def test_run_bullets_are_not_lifts_missing_from_plan_week_yaml(capsys, data_dir):
    write(
        capsys,
        data_dir,
        week=[*WEEK[:1], "Easy run 40 min; Squat 3x8 60 kg"],
        yaml_week=[
            {
                "name": "A",
                "exercises": [
                    {"exercise": "Squat", "sets": 3},
                    {"exercise": "Bench Press", "sets": 3},
                ],
            },
            {"name": "B", "exercises": [{"exercise": "Squat", "sets": 3}]},
        ],
    )
    _, out = run(capsys, data_dir, "plan", "check")
    assert not any("Easy run" in p for p in out["problems"]), out["problems"]


# Beta 4 p1-lucia-F1, p5-elena-F1, p6-james-F1, p7-nuevo-F3: a one-line Nutrition section.
@pytest.mark.parametrize(
    "line",
    [
        "1648 kcal, proteína 131,22 g, grasa 45,78 g, hidratos 177,78 g, fibra 25 g.",
        "1648 kcal; protein 131.22 g; fat 45.78 g; carbohydrate 177.78 g; fibre 25 g",
        "1648 kcal, 131 g protein, 46 g fat, 178 g carbs, 25 g fibre",
        "1.648 kcal, 131 g de proteína, 46 g de grasa, 178 g de hidratos, 25 g de fibra",
    ],
)
def test_a_one_line_nutrition_section_is_read(line):
    from coach.plancheck import nutrition_numbers

    got = nutrition_numbers(f"## Nutrition\n\n{line}\n")
    assert got["kcal"] == 1648 and round(got["protein"]) == 131 and round(got["fat"]) == 46
    assert round(got["carbs"]) == 178 and got["fibre"] == 25


def test_a_nutrient_with_no_number_in_its_part_is_not_read():
    from coach.plancheck import nutrition_numbers

    text = "## Nutrition\n\n- 3 meals with protein, fibre at every meal; 1650 kcal\n"
    assert nutrition_numbers(text) == {"kcal": 1650}


def test_the_kcal_figure_is_not_the_next_nutrients():
    from coach.plancheck import nutrition_numbers

    text = "## Nutrition\n\n- Calories 1650 kcal protein 120 g\n"
    assert nutrition_numbers(text) == {"kcal": 1650, "protein": 120}


def test_a_per_kg_figure_then_grams_after_a_comma_reads_the_grams():
    from coach.plancheck import nutrition_numbers

    text = "## Nutrition\n\n- Protein: 1.6 g/kg, about 120 g a day\n"
    assert nutrition_numbers(text) == {"protein": 120}


# Beta 4 p3-antonio-F1: a plan written after a training stop prescribes no training.
def _stopped(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.symptoms", "chest_pain")
    assert run(capsys, data_dir, "safety")[1]["no_training"] is True


def test_a_no_training_plan_after_a_stop_is_ok_and_exports(capsys, data_dir):
    write(capsys, data_dir)  # the plan before the stop, with its plan-week.yaml
    _stopped(capsys, data_dir)
    m = macros(capsys, data_dir)
    (data_dir / "plan.md").write_text(
        f"Date: {TODAY}\ntarget_kcal: {m['kcal']:g}\nin_deficit: false\n\n"
        "## Training week\n\nNo training until a doctor has seen you.\n\n"
        f"## Nutrition\n\n- Calories: {m['kcal']:g} kcal\n",
        encoding="utf-8",
    )
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is True, out["problems"]
    assert run(capsys, data_dir, "plan", "export", "--no-qr")[0] == 0


@pytest.mark.parametrize(
    "week, cardio",
    [
        (WEEK, "- Rest."),
        ([], "- Sunday: easy run 5 km."),
        ([], "- Saturday: walk 45 minutes."),
        ([], "- Saturday: walk 1 hour."),
    ],
)
def test_a_plan_with_training_after_a_stop_is_stale(capsys, data_dir, week, cardio):
    write(capsys, data_dir, week=week, cardio=cardio)
    _stopped(capsys, data_dir)
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is False and any("stale" in p for p in out["problems"])


def test_unlabelled_lift_bullets_are_training():
    from coach.plancheck import prescribes_training
    from coach.strength import load_muscle_map

    text = "## Training week\n\n- Squat 3x8 60 kg\n- Bench press 3x8 40 kg\n"
    assert prescribes_training(text, load_muscle_map())
