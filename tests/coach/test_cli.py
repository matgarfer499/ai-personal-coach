import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from coach import catalogue
from coach.checkins import Checkin, append_checkin
from coach.cli import main
from coach.profile import Profile, load_profile, save_profile
from coach.sessions.model import ExerciseSet
from coach.sessions.store import append

TODAY = "2026-04-01"
SKYR = "Skyr de prueba"
# Synthetic catalogue product with no fibre value: 50 kcal, 8 g protein per 100 g.
SKYR_PRODUCT = catalogue.CatalogueProduct(
    barcode="8400000000024",
    product_name=SKYR,
    brand="Marca Prueba",
    chain="Eroski",
    per="100 g",
    kcal=50,
    protein_g=8,
    carbs_g=4.1,
    fat_g=0.2,
    fibre_g=None,
    allergens=(),
    url="https://world.openfoodfacts.org/product/8400000000024",
    fetched_on=date(2026, 3, 1),
)
HEVY_EXPORT = Path(__file__).parent.parent / "fixtures" / "hevy" / "basic.csv"
HEVY_LEFTOVERS = Path(__file__).parent.parent / "fixtures" / "hevy" / "template_leftover.csv"


@pytest.fixture
def data_dir(tmp_path):
    save_profile(
        Profile(
            sex="male",
            birth_date=date(1996, 4, 1),
            height_cm=180,
            weight_kg=80,
            goal="fat_loss",
            activity_level="desk",
            screening={"scoff_positive": False, "parq_any_yes": False},
        ),
        tmp_path / "profile.yaml",
    )
    return tmp_path


def run(capsys, *args):
    code = main(["--data-dir", str(args[0]), "--today", TODAY, *args[1:], "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_safety(capsys, data_dir):
    code, out = run(capsys, data_dir, "safety")
    assert code == 0
    assert out["screened"] is True and out["no_deficit"] is False


def test_energy(capsys, data_dir):
    code, out = run(capsys, data_dir, "energy")
    assert code == 0
    assert out["rmr"] == pytest.approx(1780)
    assert out["tdee"] == pytest.approx(1780 * 1.45)
    assert out["target"]["deficit"] == 500
    assert out["target"]["kcal"] == round(1780 * 1.45) - 500


def test_energy_goal_and_tdee_override(capsys, data_dir):
    _, out = run(capsys, data_dir, "energy", "--goal", "maintenance", "--tdee", "2400")
    assert out["target"]["kcal"] == 2400


def test_energy_pal_reaches_the_target(capsys, data_dir):
    _, out = run(capsys, data_dir, "energy", "--goal", "maintenance", "--pal", "1.6")
    assert out["tdee"] == pytest.approx(1780 * 1.6)
    assert out["target"]["kcal"] == round(1780 * 1.6)


def test_goal_typo_is_rejected(capsys, data_dir):
    assert main(["--data-dir", str(data_dir), "energy", "--goal", "fatloss"]) == 2
    assert "fatloss" in json.loads(capsys.readouterr().out)["message"]


def test_macros_kcal_below_floor_is_raised(capsys, data_dir):
    _, out = run(capsys, data_dir, "macros", "--kcal", "900")
    assert out["kcal"] == 1500


def test_macros_follow_the_target(capsys, data_dir):
    _, out = run(capsys, data_dir, "macros")
    assert out["kcal"] == round(1780 * 1.45) - 500
    assert out["protein_g"] == pytest.approx(160)  # 2.0 g/kg in a deficit


def test_incomplete_profile_is_a_clear_error(capsys, data_dir):
    (data_dir / "profile.yaml").write_text("language: es\n")
    code, out = run(capsys, data_dir, "energy")
    assert code == 2
    assert out == {"error": "profile_incomplete", "field": "sex"}


def test_trend_from_checkins(capsys, data_dir):
    start = date(2026, 3, 4)
    for d in range(28):
        append_checkin(
            Checkin(start + timedelta(d), weight_kg=80 - 0.05 * d, intake_kcal=2000),
            data_dir / "checkins.csv",
        )
    _, out = run(capsys, data_dir, "trend")
    assert out["status"] == "ok"
    assert out["rate_kg_week"] == pytest.approx(-0.35)
    assert out["recalibrated_tdee"] == pytest.approx(2000 + 0.35 * 7700 / 7)


def test_trend_ignores_weigh_ins_after_today(capsys, data_dir):
    start = date(2026, 3, 4)  # TODAY is 2026-04-01, the last of these 29 days
    for d in range(29):
        append_checkin(
            Checkin(start + timedelta(d), weight_kg=80 - 0.05 * d, intake_kcal=2000),
            data_dir / "checkins.csv",
        )
    _, before = run(capsys, data_dir, "trend")
    append_checkin(
        Checkin(date(2026, 4, 2), weight_kg=70, intake_kcal=900), data_dir / "checkins.csv"
    )
    _, after = run(capsys, data_dir, "trend")
    assert after == before


def test_trend_insufficient(capsys, data_dir):
    append_checkin(Checkin(date(2026, 3, 30), weight_kg=80), data_dir / "checkins.csv")
    _, out = run(capsys, data_dir, "trend")
    assert out["status"] == "insufficient_data"
    assert out["recalibrated_tdee"] is None


def test_zones(capsys, data_dir):
    _, out = run(capsys, data_dir, "zones", "--hr-rest", "60")
    assert out["method"] == "hrr"
    assert out["hr_max"] == 187  # Tanaka at 30
    assert [z["name"] for z in out["zones"]] == ["light", "moderate", "vigorous"]


def test_strength_e1rm_and_deload(capsys, data_dir):
    _, out = run(
        capsys, data_dir, "strength", "e1rm", "--weight", "100", "--reps", "8", "--rir", "2"
    )
    assert out["e1rm"] == round(100 * (1 + 10 / 30), 2)  # CLI output has 2 decimals
    _, out = run(capsys, data_dir, "strength", "deload", "--signs", "performance_stall,poor_sleep")
    assert out["deload"]["volume_cut"] == [0.3, 0.5]


def test_knowledge_stale_uses_profile_months(capsys, data_dir):
    _, out = run(capsys, data_dir, "knowledge", "stale")
    assert out["months"] == 6 and out["stale"] == []
    code = main(
        ["--data-dir", str(data_dir), "--today", "2030-01-01", "knowledge", "stale", "--json"]
    )
    out = json.loads(capsys.readouterr().out)
    assert code == 0 and len(out["stale"]) == 4


def test_knowledge_section(capsys, data_dir):
    code = main(["--data-dir", str(data_dir), "knowledge", "section", "nutrition", "Dietary fibre"])
    assert code == 0
    assert capsys.readouterr().out.startswith("### Dietary fibre")


def test_module_entry_point(data_dir):
    result = subprocess.run(
        [sys.executable, "-m", "coach", "--data-dir", str(data_dir), "safety", "--json"],
        capture_output=True,
        text=True,
        check=True,
    )
    assert json.loads(result.stdout)["screened"] is True


def _log(data_dir):
    sets = []
    for day, reps in [(18, 13), (25, 13)]:
        start = datetime(2026, 3, day, 18, 0)
        sets += [
            ExerciseSet("hevy_csv", start, "Bench Press (Barbell)", 0, i, weight_kg=60.0, reps=reps)
            for i in range(3)
        ]
    sets.append(ExerciseSet("hevy_csv", datetime(2026, 3, 25, 18, 0), "Zercher Carry", 1, 0))
    append(sets, data_dir / "sessions.csv")


def test_strength_sets_counts_the_week(capsys, data_dir):
    _log(data_dir)
    _, out = run(capsys, data_dir, "strength", "sets", "--week-ending", "2026-04-01")
    assert out["week"] == {"start": "2026-03-26", "end": "2026-04-01"}
    assert out["sets"] == {}
    _, default = run(capsys, data_dir, "strength", "sets")  # the last logged week
    _, out = run(capsys, data_dir, "strength", "sets", "--week-ending", "2026-03-25")
    assert default == out
    assert out["sets"]["chest"] == 3 and out["sets"]["triceps"] == 1.5
    assert out["unmapped"] == ["Zercher Carry"]
    assert out["reference_sets_per_week"] == 10


def test_strength_ignores_sessions_after_today(capsys, data_dir):
    _log(data_dir)
    later = [
        ExerciseSet(
            "hevy_csv",
            datetime(2026, 4, 5, 18, 0),
            "Bench Press (Barbell)",
            0,
            i,
            weight_kg=80.0,
            reps=5,
        )
        for i in range(3)
    ]
    _, before = run(capsys, data_dir, "strength", "progress")
    _, sets_before = run(capsys, data_dir, "strength", "sets")
    append(later, data_dir / "sessions.csv")
    assert run(capsys, data_dir, "strength", "progress")[1] == before
    assert run(capsys, data_dir, "strength", "sets")[1] == sets_before


def test_strength_progress_one_and_all(capsys, data_dir):
    _log(data_dir)
    _, out = run(capsys, data_dir, "strength", "progress", "--exercise", "bench press (barbell)")
    assert out["Bench Press (Barbell)"]["action"] == "increase_load"
    _, out = run(capsys, data_dir, "strength", "progress")
    assert set(out) == {"Bench Press (Barbell)", "Zercher Carry"}


def test_strength_progress_uses_the_rep_range_given_per_lift(capsys, data_dir):
    _log(data_dir)
    _, out = run(
        capsys,
        data_dir,
        "strength",
        "progress",
        "--rep-range",
        "bench press (barbell)=10-15",
        "--rep-range",
        "squat=5-8",  # a lift with no logged sets is ignored
    )
    bench = out["Bench Press (Barbell)"]
    assert bench["action"] == "add_reps" and bench["rep_range"] == [10, 15]
    assert "beats 15" in bench["reasons"][0]
    assert out["Zercher Carry"]["rep_range"] == [8, 12]  # the rule's default
    _, out = run(capsys, data_dir, "strength", "progress", "--rep-range", "bench press=6-8")
    assert out["Bench Press (Barbell)"]["rep_range"] == [6, 8]
    assert out["Bench Press (Barbell)"]["action"] == "increase_load"
    _, out = run(capsys, data_dir, "strength", "progress", "--exercise", "zercher carry")
    assert out["Zercher Carry"]["rep_range"] == [8, 12]


def test_strength_progress_rejects_a_bad_rep_range(capsys, data_dir):
    _log(data_dir)
    code, out = run(capsys, data_dir, "strength", "progress", "--rep-range", "bench press=12-8")
    assert code == 2 and "lower than" in out["message"]
    code, out = run(capsys, data_dir, "strength", "progress", "--rep-range", "bench press")
    assert code == 2 and "EXERCISE=LOW-HIGH" in out["message"]


def test_import_hevy_twice(capsys, data_dir):
    _, out = run(capsys, data_dir, "import", str(HEVY_EXPORT))
    assert out == {
        "importer": "hevy_csv",
        "read": 8,
        "added": 8,
        "duplicates": 0,
        "first_day": "2025-07-24",
        "last_day": "2025-07-26",
        "skipped_empty": 0,
        "warnings": [],
    }
    _, out = run(capsys, data_dir, "import", str(HEVY_EXPORT))
    assert (out["added"], out["duplicates"]) == (0, 8)


def test_import_skips_and_reports_template_leftovers(capsys, data_dir):
    # Rows with no reps, weight, duration or distance carry nothing the coach reads. A duration-only
    # set (the plank) is a real set and stays.
    _, out = run(capsys, data_dir, "import", str(HEVY_LEFTOVERS))
    assert (out["read"], out["added"], out["duplicates"], out["skipped_empty"]) == (6, 3, 0, 3)
    assert out["read"] == out["added"] + out["duplicates"] + out["skipped_empty"]
    assert len(out["warnings"]) == 1
    warning = out["warnings"][0]
    assert "Bench Press (Barbell)" in warning and "Lateral Raise (Dumbbell)" in warning
    assert "Plank" not in warning and "2026-01-02" in warning
    stored = (data_dir / "sessions.csv").read_text()
    assert "Plank" in stored and "Lateral Raise" not in stored
    _, again = run(capsys, data_dir, "import", str(HEVY_LEFTOVERS))
    assert (again["added"], again["duplicates"], again["skipped_empty"]) == (0, 3, 3)


def test_import_unknown_file_is_a_clear_error(capsys, data_dir, tmp_path):
    other = tmp_path / "other.csv"
    other.write_text("foo,bar\n1,2\n")
    code, out = run(capsys, data_dir, "import", str(other))
    assert code == 2 and "no importer" in out["message"]


def test_import_warns_when_another_source_has_the_session(capsys, data_dir, tmp_path):
    export = tmp_path / "manual.csv"
    export.write_text("date,exercise,weight_kg,reps\n2025-07-24 11:25,Bench Press,62.5,8\n")
    run(capsys, data_dir, "import", str(export))
    _, out = run(capsys, data_dir, "import", str(HEVY_EXPORT))
    assert out["warnings"] and "2025-07-24T11:25:00" in out["warnings"][0]


def test_menu_totals_from_the_real_tables(capsys, data_dir):
    _, out = run(
        capsys,
        data_dir,
        "menu",
        "--region",
        "es",
        "--item",
        "lentejas, cocidas=200",
        "--item",
        "pulpo, crudo=100",
        "--item",
        "ñoquis=50",
    )
    assert out["kcal"] > 0 and out["protein_g"] > 0
    assert out["unknown"] == ["ñoquis"]


def test_menu_finds_catalogue_products(capsys, data_dir):
    catalogue.save([SKYR_PRODUCT], data_dir)
    _, out = run(capsys, data_dir, "menu", "--region", "es", "--item", f"{SKYR}=150")
    assert out["unknown"] == [] and out["protein_g"] == pytest.approx(12)
    assert out["missing"] == {"fibre_g": [SKYR]}


def test_menu_checks_totals_against_the_targets(capsys, data_dir):
    _, targets = run(capsys, data_dir, "macros")
    _, out = run(
        capsys, data_dir, "menu", "--region", "es", "--item", "lentejas, cocidas=200", "--targets"
    )
    assert out["targets"]["kcal"] == targets["kcal"]
    assert out["totals"]["kcal"] < targets["kcal"]
    assert out["check"]["kcal"] == "under" and out["ok"] is False
    assert set(out["check"]) == {"kcal", "protein_g", "fat_g", "fibre_g"}


def test_menu_targets_from_a_stored_calorie_target(capsys, data_dir):
    args = ["--region", "es", "--item", "lentejas, cocidas=200", "--targets"]
    _, out = run(capsys, data_dir, "menu", *args, "--kcal", "2100", "--in-deficit")
    _, macros = run(capsys, data_dir, "macros", "--kcal", "2100", "--in-deficit")
    assert out["targets"] == macros and macros["kcal"] == 2100


def test_typed_kcal_cannot_keep_a_deficit_the_flags_forbid(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.scoff_positive", "true")
    _, energy = run(capsys, data_dir, "energy")
    _, out = run(capsys, data_dir, "macros", "--kcal", "1500", "--in-deficit")
    assert out["kcal"] == energy["target"]["kcal"] > 1500
    assert out["in_deficit"] is False


def test_typed_kcal_cannot_keep_a_surplus_the_flags_forbid(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "goal", "muscle_gain")
    run(capsys, data_dir, "profile", "set", "screening.scoff_positive", "true")
    _, energy = run(capsys, data_dir, "energy")
    _, out = run(capsys, data_dir, "macros", "--kcal", "4000")
    assert out["kcal"] == energy["target"]["kcal"] < 4000


def test_typed_kcal_cannot_keep_a_deficit_an_older_adult_may_not_have(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "birth_date", "1955-01-01")  # 71, no obesity
    _, energy = run(capsys, data_dir, "energy")
    assert energy["target"]["deficit"] == 0
    _, out = run(capsys, data_dir, "macros", "--kcal", "1600", "--in-deficit")
    assert out["kcal"] == energy["target"]["kcal"] > 1600 and out["in_deficit"] is False


def test_menu_check_bands():
    from coach.cli import menu_check

    targets = {"kcal": 2000, "protein_g": 150, "fat_g": 55, "fat_min_g": 45, "fibre_g": 25}
    ok = {"kcal": 2050, "protein_g": 150, "fat_g": 45, "fibre_g": 25, "carbs_g": 0}
    assert menu_check(ok, targets) == {
        "kcal": "ok",
        "protein_g": "ok",
        "fat_g": "ok",
        "fibre_g": "ok",
    }
    over = ok | {"kcal": 2101, "protein_g": 149, "fat_g": 44}
    check = menu_check(over, targets)
    assert check["kcal"] == "over" and check["protein_g"] == "under" and check["fat_g"] == "under"


def test_menu_check_with_missing_values():
    from coach.cli import menu_check

    targets = {"kcal": 2000, "protein_g": 150, "fat_g": 55, "fat_min_g": 45, "fibre_g": 25}
    totals = {"kcal": 2050, "protein_g": 150, "fat_g": 40, "fibre_g": 20, "carbs_g": 0}
    missing = {"kcal": ["x"], "protein_g": ["x"], "fat_g": ["x"]}
    check = menu_check(totals | {"missing": missing}, targets)
    # Missing kcal cannot be judged; a floor already reached stays ok (the true total is
    # higher); a floor not reached with a value missing is unknown, not under.
    assert check == {"kcal": "missing", "protein_g": "ok", "fat_g": "missing", "fibre_g": "under"}


def test_menu_with_a_missing_value_is_not_ok(capsys, data_dir):
    catalogue.save([SKYR_PRODUCT], data_dir)
    items = [f"{SKYR}=150", "lentejas, cocidas=200"]
    args = [a for item in items for a in ("--item", item)]
    _, out = run(capsys, data_dir, "menu", "--region", "es", *args, "--targets")
    assert out["totals"]["missing"] == {"fibre_g": [SKYR]}
    assert out["check"]["fibre_g"] == "missing" and out["ok"] is False


def test_menu_item_needs_grams(capsys, data_dir):
    code, out = run(capsys, data_dir, "menu", "--item", "arroz")
    assert code == 2 and "NAME=GRAMS" in out["message"]


def test_profile_set_and_show(capsys, tmp_path):
    base = ["--data-dir", str(tmp_path), "--json"]
    assert main(["--data-dir", str(tmp_path), "profile", "set", "sex", "female", "--json"]) == 0
    capsys.readouterr()
    for field, value in [
        ("birth_date", "1990-05-17"),
        ("height_cm", "165"),
        ("weight_kg", "62.5"),
        ("medications", "glp1,metoprolol"),
        ("screening.scoff_positive", "false"),
        ("screening.menstrual", "normal"),
        ("research_reminder_months", "3"),
    ]:
        assert main(["--data-dir", str(tmp_path), "profile", "set", field, value, "--json"]) == 0
        capsys.readouterr()
    main(["--data-dir", str(tmp_path), "profile", "show", "--json"])
    out = json.loads(capsys.readouterr().out)
    assert out["profile"]["birth_date"] == "1990-05-17"
    assert out["profile"]["height_cm"] == 165.0
    assert out["profile"]["medications"] == ["glp1", "metoprolol"]
    assert out["profile"]["screening"] == {"scoff_positive": False, "menstrual": "normal"}
    assert out["profile"]["research_reminder_months"] == 3
    assert out["missing"] == ["goal", "experience", "activity_level", "language", "region"]
    assert out["unrecognised"] == {"medications": ["metoprolol"], "conditions": []}
    assert base  # same flags as other commands


@pytest.mark.parametrize(
    "field,value,message",
    [
        ("sex", "other", "sex"),
        ("height_cm", "tall", "height_cm"),
        ("birth_date", "17/05/1990", "birth_date"),
        ("screening.scoff_positive", "maybe", "true or false"),
        ("screening.scoff_yes_count", "6", "0 to 5"),
        ("screening.unknown", "true", "unknown screening key"),
        ("nickname", "x", "unknown profile field"),
    ],
)
def test_profile_set_rejects_bad_values(capsys, tmp_path, field, value, message):
    code = main(["--data-dir", str(tmp_path), "profile", "set", field, value, "--json"])
    out = json.loads(capsys.readouterr().out)
    assert code == 2 and message in out["message"]
    assert not (tmp_path / "profile.yaml").exists()


def test_checkin_add(capsys, data_dir):
    code, out = run(
        capsys, data_dir, "checkin", "add", "--weight", "79.8", "--sleep", "7", "--notes", "ok"
    )
    assert code == 0 and out["date"] == TODAY and out["weight_kg"] == 79.8


def test_checkin_refuses_weight_after_positive_screen(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.scoff_positive", "true")
    code, out = run(capsys, data_dir, "checkin", "add", "--weight", "79.8")
    assert code == 2 and "weigh-ins" in out["message"]
    for flag in ("--waist", "--intake"):
        code, out = run(capsys, data_dir, "checkin", "add", flag, "80")
        assert code == 2
    code, out = run(capsys, data_dir, "checkin", "add", "--sleep", "6")
    assert code == 0 and out["weight_kg"] is None


def test_one_scoff_yes_answer_still_allows_a_deficit(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.scoff_positive", "none")
    run(capsys, data_dir, "profile", "set", "screening.scoff_yes_count", "1")
    _, energy = run(capsys, data_dir, "energy")
    assert energy["target"]["deficit"] > 0
    code, _ = run(capsys, data_dir, "checkin", "add", "--weight", "79.8", "--waist", "80")
    assert code == 0


def test_two_scoff_yes_answers_block_the_deficit_and_body_logs(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.scoff_positive", "none")
    run(capsys, data_dir, "profile", "set", "screening.scoff_yes_count", "2")
    _, energy = run(capsys, data_dir, "energy")
    assert energy["target"]["deficit"] == 0
    for flag in ("--weight", "--waist", "--intake"):
        code, _ = run(capsys, data_dir, "checkin", "add", flag, "80")
        assert code == 2


def test_under_18s_get_no_targets_or_body_logs(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "birth_date", "2010-01-01")
    code, out = run(capsys, data_dir, "macros")
    assert code == 2 and "Under-18s" in out["message"]
    code, out = run(capsys, data_dir, "checkin", "add", "--weight", "60")
    assert code == 2 and "Under-18s" in out["message"]
    code, _ = run(capsys, data_dir, "checkin", "add", "--sleep", "8")
    assert code == 0


def test_pregnancy_refuses_weigh_ins_with_its_own_reason(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "sex", "female")
    run(capsys, data_dir, "profile", "set", "conditions", "pregnant")
    code, out = run(capsys, data_dir, "checkin", "add", "--weight", "70")
    assert code == 2 and '"Pregnancy"' in out["message"] and "Eating-disorder" not in out["message"]
    code, _ = run(capsys, data_dir, "checkin", "add", "--waist", "90", "--intake", "2200")
    assert code == 0
    _, trend = run(capsys, data_dir, "trend")
    assert trend["status"] == "disabled" and '"Pregnancy"' in trend["notes"][0]


def test_data_dir_from_environment(capsys, data_dir, monkeypatch):
    monkeypatch.setenv("COACH_DATA_DIR", str(data_dir))
    assert main(["safety", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["screened"] is True


def test_profile_show_names_the_data_dir_it_resolved(capsys, data_dir, monkeypatch):
    """Skills read and write files by path, so they learn the directory from the CLI."""
    assert main(["--data-dir", str(data_dir), "profile", "show", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data_dir"] == str(data_dir.resolve())
    monkeypatch.setenv("COACH_DATA_DIR", str(data_dir))
    assert main(["profile", "show", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data_dir"] == str(data_dir.resolve())


def test_data_dir_is_absolute_even_when_given_relative(capsys, data_dir, monkeypatch):
    monkeypatch.chdir(data_dir.parent)
    assert main(["--data-dir", data_dir.name, "profile", "show", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data_dir"] == str(data_dir.resolve())


def test_default_data_dir_is_the_repo_data_folder(capsys, tmp_path, monkeypatch):
    from coach import cli

    assert cli.DEFAULT_DATA_DIR == Path(cli.__file__).resolve().parent.parent / "data"
    monkeypatch.setattr(cli, "DEFAULT_DATA_DIR", tmp_path / "data")  # never read the real one
    monkeypatch.delenv("COACH_DATA_DIR", raising=False)
    assert main(["profile", "show", "--json"]) == 0
    assert json.loads(capsys.readouterr().out)["data_dir"] == str((tmp_path / "data").resolve())


def test_profile_set_blood_pressure(capsys, tmp_path):
    for field, value in [("screening.bp_systolic", "150"), ("screening.bp_diastolic", "88")]:
        assert main(["--data-dir", str(tmp_path), "profile", "set", field, value, "--json"]) == 0
    capsys.readouterr()
    code = main(
        ["--data-dir", str(tmp_path), "profile", "set", "screening.bp_systolic", "high", "--json"]
    )
    assert code == 2 and "whole number" in json.loads(capsys.readouterr().out)["message"]
    assert (
        main(["--data-dir", str(tmp_path), "profile", "set", "screening.bp_systolic", "none"]) == 0
    )
    assert "bp_systolic" not in load_profile(tmp_path / "profile.yaml").screening


def test_cli_rounds_floats_for_quoting(capsys, data_dir):
    _, out = run(capsys, data_dir, "macros")
    for key in ("protein_g", "fat_g", "carbs_g"):
        assert out[key] == round(out[key], 2)


def test_foods_search(capsys, data_dir):
    _, out = run(capsys, data_dir, "foods", "search", "pollo", "--region", "es")
    names = [f["name_es"] for f in out["foods"]]
    assert "pechuga de pollo, cruda" in names
    assert "repollo" not in names  # whole words, not substrings
    assert {"carbs_g", "fat_g", "fibre_g"} <= set(out["foods"][0])
    _, plain = run(capsys, data_dir, "foods", "search", "brocoli", "--region", "es")
    _, accented = run(capsys, data_dir, "foods", "search", "brócoli", "--region", "es")
    assert plain == accented and plain["foods"]  # accents do not matter
    catalogue.save([SKYR_PRODUCT], data_dir)
    _, out = run(capsys, data_dir, "foods", "search", "skyr", "--region", "es")
    assert [p["product_name"] for p in out["products"]] == [SKYR]
    assert out["products"][0]["protein_g"] > 0


def test_bad_arguments_answer_in_json(capsys):
    from coach.cli import main

    assert main(["strength", "e1rm", "--weight", "heavy", "--reps", "5", "--json"]) == 2
    out = json.loads(capsys.readouterr().out)
    assert out["error"] == "invalid" and "--weight" in out["message"]


def _stalled_bench(data_dir):
    sets = []
    for day in (10, 14, 18, 22, 26):
        start = datetime(2026, 3, day, 18, 0)
        sets += [
            ExerciseSet("hevy_csv", start, "Bench Press (Barbell)", 0, i, weight_kg=60.0, reps=10)
            for i in range(3)
        ]
    append(sets, data_dir / "sessions.csv")


def test_injury_add_pauses_its_lifts_and_clear_resumes_them(capsys, data_dir):
    _stalled_bench(data_dir)
    assert (
        run(capsys, data_dir, "strength", "progress")[1]["Bench Press (Barbell)"]["action"]
        == "stalled"
    )
    code, out = run(
        capsys,
        data_dir,
        "injury",
        "add",
        "hombro derecho",
        "--since",
        "2026-03-12",
        "--professional",
        "fisioterapeuta",
        "--exercises",
        "bench press, Overhead Press",
    )
    assert code == 0
    assert out["injuries"] == [
        {
            "area": "hombro derecho",
            "status": "active",
            "since": "2026-03-12",
            "professional": "fisioterapeuta",
            "exercises": ["bench press", "Overhead Press"],
        }
    ]
    progress = run(capsys, data_dir, "strength", "progress")[1]["Bench Press (Barbell)"]
    assert progress["action"] == "paused" and progress["load_kg"] == 60
    assert "fisioterapeuta" in progress["reasons"][0]
    _, flags = run(capsys, data_dir, "safety")
    assert flags["paused_exercises"]["bench press"]["reasons"] == progress["reasons"]

    _, out = run(capsys, data_dir, "injury", "clear", "Hombro Derecho", "--on", "2026-03-27")
    assert out["injuries"][0]["status"] == "cleared"
    assert out["injuries"][0]["cleared_on"] == "2026-03-27"
    progress = run(capsys, data_dir, "strength", "progress")[1]["Bench Press (Barbell)"]
    assert progress["action"] == "add_reps"  # the held sessions are not a stall


def test_injury_without_a_professional_refers(capsys, data_dir):
    run(capsys, data_dir, "injury", "add", "rodilla")
    _, flags = run(capsys, data_dir, "safety")
    assert flags["refer_gp"] is True


def test_injury_add_again_updates_the_same_area(capsys, data_dir):
    run(capsys, data_dir, "injury", "add", "rodilla", "--exercises", "Squat")
    _, out = run(capsys, data_dir, "injury", "add", "Rodilla", "--professional", "traumatólogo")
    assert len(out["injuries"]) == 1
    assert out["injuries"][0]["exercises"] == ["Squat"]  # kept unless given again
    assert out["injuries"][0]["professional"] == "traumatólogo"
    _, listed = run(capsys, data_dir, "injury", "list")
    assert listed == out


def test_a_new_injury_in_a_cleared_area_starts_unassessed(capsys, data_dir):
    run(
        capsys,
        data_dir,
        "injury",
        "add",
        "rodilla",
        "--professional",
        "fisio",
        "--since",
        "2026-01-10",
        "--exercises",
        "Squat",
    )
    run(capsys, data_dir, "injury", "clear", "rodilla", "--on", "2026-02-01")
    _, out = run(capsys, data_dir, "injury", "add", "rodilla", "--since", "2026-03-20")
    assert out["injuries"] == [
        {"area": "rodilla", "status": "active", "since": "2026-03-20", "exercises": ["Squat"]}
    ]
    assert run(capsys, data_dir, "safety")[1]["refer_gp"] is True


def test_injury_names_match_aliases_and_unmatched_names_are_reported(capsys, data_dir):
    _log(data_dir)  # logs "Bench Press (Barbell)" and "Zercher Carry"
    _, out = run(
        capsys,
        data_dir,
        "injury",
        "add",
        "hombro",
        "--professional",
        "fisio",
        "--exercises",
        "press banca, press militar",
    )
    assert out["unmatched"] == ["press militar"]
    progress = run(capsys, data_dir, "strength", "progress")[1]["Bench Press (Barbell)"]
    assert progress["action"] == "paused"


def test_changing_parq_answers_drops_an_old_vigorous_review(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.parq_any_yes", "false")
    run(capsys, data_dir, "profile", "set", "screening.vigorous_reviewed", "true")
    run(capsys, data_dir, "profile", "set", "screening.parq_any_yes", "false")  # same answer
    assert run(capsys, data_dir, "profile", "show")[1]["profile"]["screening"]["vigorous_reviewed"]
    run(capsys, data_dir, "profile", "set", "screening.parq_any_yes", "true")
    screening = run(capsys, data_dir, "profile", "show")[1]["profile"]["screening"]
    assert "vigorous_reviewed" not in screening
    assert run(capsys, data_dir, "safety")[1]["review_before_vigorous"] is True


def test_clearing_an_unknown_injury_is_a_clear_error(capsys, data_dir):
    code, out = run(capsys, data_dir, "injury", "clear", "codo")
    assert code == 2 and "codo" in out["message"]


def test_profile_set_points_injuries_to_their_command(capsys, data_dir):
    code, out = run(capsys, data_dir, "profile", "set", "injuries", "rodilla")
    assert code == 2 and "coach injury" in out["message"]


def test_vigorous_review_can_be_recorded(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.parq_any_yes", "true")
    assert run(capsys, data_dir, "safety")[1]["review_before_vigorous"] is True
    run(capsys, data_dir, "profile", "set", "screening.vigorous_reviewed", "true")
    _, flags = run(capsys, data_dir, "safety")
    assert flags["review_before_vigorous"] is False and flags["no_all_out_sprints"] is True


def test_a_region_without_its_folder_is_refused_with_a_hint(capsys, data_dir):
    code, out = run(capsys, data_dir, "profile", "set", "region", "mx")
    assert code == 2
    assert "regions/mx" in out["message"] and "docs/adding-a-region.md" in out["message"]
    _, shown = run(capsys, data_dir, "profile", "show")
    assert shown["profile"]["region"] is None


def test_region_none_clears_it(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "region", "es")
    code, out = run(capsys, data_dir, "profile", "set", "region", "none")
    assert code == 0 and out["profile"]["region"] is None


def test_safety_prints_the_emergency_number(capsys, data_dir):
    assert run(capsys, data_dir, "safety")[1]["emergency_number"] is None
    run(capsys, data_dir, "profile", "set", "region", "es")
    assert run(capsys, data_dir, "safety")[1]["emergency_number"] == "112"
    run(capsys, data_dir, "profile", "set", "emergency_number", "061")
    assert run(capsys, data_dir, "safety")[1]["emergency_number"] == "061"
