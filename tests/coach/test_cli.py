import dataclasses
import json
import subprocess
import sys
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest

from coach import catalogue, energy
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


def _stopped_active(data_dir):
    profile = load_profile(data_dir / "profile.yaml")
    profile.activity_level = "active"
    profile.screening = {"scoff_positive": False, "cardiac_symptoms": True}
    save_profile(profile, data_dir / "profile.yaml")


def _rmr(data_dir):
    return energy.rmr_mifflin(load_profile(data_dir / "profile.yaml"), date(2026, 4, 1))


def test_energy_active_note_under_no_training_and_explicit_pal(capsys, data_dir):
    _stopped_active(data_dir)

    def notes(*extra):
        return run(capsys, data_dir, "energy", *extra)[1]["target"]["notes"]

    assert any("no change is needed" in n for n in notes())
    assert any(f"pal_override {energy.DESK_PAL:g}`" in n for n in notes())
    assert not any("no change is needed" in n for n in notes("--pal", "1.8"))
    assert not any("no change is needed" in n for n in notes("--tdee", "2400"))


def test_pal_override_reaches_energy_and_macros(capsys, data_dir):
    _stopped_active(data_dir)
    run(capsys, data_dir, "profile", "set", "pal_override", str(energy.DESK_PAL))
    _, out = run(capsys, data_dir, "energy")
    kcal = round(_rmr(data_dir) * energy.DESK_PAL)  # no deficit while training is stopped
    assert out["target"]["kcal"] == kcal
    assert any("using stored pal_override" in n for n in out["target"]["notes"])
    _, macros = run(capsys, data_dir, "macros")
    assert macros["kcal"] == kcal
    _, shown = run(capsys, data_dir, "profile", "show")
    assert shown["profile"]["pal_override"] == energy.DESK_PAL
    assert "pal_override" not in shown["missing"]
    # The flag clears: the stored choice is ignored, never silently kept in force.
    run(capsys, data_dir, "profile", "set", "screening.cardiac_symptoms", "false")
    _, out = run(capsys, data_dir, "energy")
    assert out["tdee"] == pytest.approx(_rmr(data_dir) * energy.band_midpoint("active"))
    run(capsys, data_dir, "profile", "set", "pal_override", "none")
    assert load_profile(data_dir / "profile.yaml").pal_override is None


def test_profile_set_pal_override_warns_when_it_has_no_effect(capsys, data_dir):
    def warnings():
        out = run(capsys, data_dir, "profile", "set", "pal_override", "1.45")[1]
        return out.get("warnings", [])

    assert any("no effect" in w for w in warnings())  # activity level is desk
    _stopped_active(data_dir)
    assert warnings() == []
    run(capsys, data_dir, "profile", "set", "screening.cardiac_symptoms", "false")
    assert any("inactive until a training hold applies" in w for w in warnings())


def test_stored_pal_override_is_announced_by_the_cli(capsys, data_dir):
    _stopped_active(data_dir)
    run(capsys, data_dir, "profile", "set", "pal_override", str(energy.DESK_PAL))
    _, out = run(capsys, data_dir, "energy")
    assert any("using stored pal_override" in n for n in out["target"]["notes"])


def test_macros_with_the_desk_pal_match_the_energy_rerun(capsys, data_dir):
    _stopped_active(data_dir)
    pal = str(energy.DESK_PAL)
    _, rerun = run(capsys, data_dir, "energy", "--pal", pal)
    kcal = rerun["target"]["kcal"]
    assert kcal == round(_rmr(data_dir) * energy.DESK_PAL)  # no deficit while training is stopped
    _, with_kcal = run(capsys, data_dir, "macros", "--pal", pal, "--kcal", str(kcal))
    _, derived = run(capsys, data_dir, "macros", "--pal", pal)
    assert with_kcal["kcal"] == derived["kcal"] == kcal and derived["in_deficit"] is False


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
    (data_dir / "profile.yaml").write_text("language: es\n", encoding="utf-8")
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
    assert out["lifts"]["Bench Press (Barbell)"]["action"] == "increase_load"
    _, out = run(capsys, data_dir, "strength", "progress")
    assert set(out["lifts"]) == {"Bench Press (Barbell)", "Zercher Carry"}


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
    bench = out["lifts"]["Bench Press (Barbell)"]
    assert bench["action"] == "add_reps" and bench["rep_range"] == [10, 15]
    assert "beats 15" in bench["reasons"][0]
    assert out["lifts"]["Zercher Carry"]["rep_range"] == [8, 12]  # the rule's default
    _, out = run(capsys, data_dir, "strength", "progress", "--rep-range", "bench press=6-8")
    assert out["lifts"]["Bench Press (Barbell)"]["rep_range"] == [6, 8]
    assert out["lifts"]["Bench Press (Barbell)"]["action"] == "increase_load"
    _, out = run(capsys, data_dir, "strength", "progress", "--exercise", "zercher carry")
    assert out["lifts"]["Zercher Carry"]["rep_range"] == [8, 12]


def test_progress_reports_rep_range_names_that_match_no_lift(capsys, data_dir):
    _log(data_dir)
    pulldown = ExerciseSet(
        "hevy_csv", datetime(2026, 3, 25, 18, 0), "Lat Pulldown - Close Grip (Cable)", 2, 0
    )
    append([pulldown], data_dir / "sessions.csv")
    _, out = run(
        capsys,
        data_dir,
        "strength",
        "progress",
        "--rep-range",
        "*=6-8",  # the default for every lift is not a name to match
        "--rep-range",
        "press banca=5-8",  # a Spanish alias of the logged bench press
        "--rep-range",
        "Lat Pulldown - Close Grip=10-12",  # the logged variant
        "--rep-range",
        "Lat Pulldown - Wide Grip=10-12",  # another variant of a logged lift
        "--rep-range",
        "sentadilla bulgara=8-10",  # no logged lift
    )
    assert out["unmatched_rep_ranges"] == ["Lat Pulldown - Wide Grip", "sentadilla bulgara"]
    assert out["lifts"]["Bench Press (Barbell)"]["rep_range"] == [5, 8]
    assert out["lifts"]["Zercher Carry"]["rep_range"] == [6, 8]
    assert out["lifts"]["Lat Pulldown - Close Grip (Cable)"]["rep_range"] == [10, 12]


def test_unmatched_rep_ranges_look_at_every_logged_lift(capsys, data_dir):
    _log(data_dir)
    old = ExerciseSet(
        "hevy_csv", datetime(2026, 2, 20, 18, 0), "Barbell Row", 3, 0, weight_kg=50.0, reps=8
    )
    append([old], data_dir / "sessions.csv")  # last logged 5 weeks before TODAY
    _, out = run(
        capsys,
        data_dir,
        "strength",
        "progress",
        "--exercise",
        "zercher carry",
        "--rep-range",
        "bench press=6-8",  # logged, only filtered out of this output
        "--rep-range",
        "barbell row=6-8",  # logged, but outside the 28-day window
        "--rep-range",
        "sentadilla=6-8",
        "--rep-range",
        "*=6-8",
    )
    assert out["unmatched_rep_ranges"] == ["sentadilla"]  # and `*` is never in the list
    assert out["rep_ranges_outside_lookback"] == []  # --exercise bypasses the window
    _, out = run(
        capsys, data_dir, "strength", "progress", "--rep-range", "barbell row=6-8"
    )  # logged, but not among the lifts shown: say so, so the skills need not infer it
    assert out["rep_ranges_outside_lookback"] == ["barbell row"]


def test_exercise_bypasses_the_window_so_its_range_is_not_outside_it(capsys, data_dir):
    _log(data_dir)
    old = ExerciseSet(
        "hevy_csv", datetime(2026, 2, 20, 18, 0), "Barbell Row", 3, 0, weight_kg=50.0, reps=8
    )
    append([old], data_dir / "sessions.csv")
    _, out = run(
        capsys,
        data_dir,
        "strength",
        "progress",
        "--exercise",
        "barbell row",
        "--rep-range",
        "barbell row=6-8",
    )
    assert out["lifts"]["Barbell Row"]["rep_range"] == [6, 8]
    assert out["rep_ranges_outside_lookback"] == [] and out["unmatched_rep_ranges"] == []


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
        "conflicts": 0,
        "skipped_future": 0,
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
    stored = (data_dir / "sessions.csv").read_text(encoding="utf-8")
    assert "Plank" in stored and "Lateral Raise" not in stored
    _, again = run(capsys, data_dir, "import", str(HEVY_LEFTOVERS))
    assert (again["added"], again["duplicates"], again["skipped_empty"]) == (0, 3, 3)


def test_import_unknown_file_is_a_clear_error(capsys, data_dir, tmp_path):
    other = tmp_path / "other.csv"
    other.write_text("foo,bar\n1,2\n", encoding="utf-8")
    code, out = run(capsys, data_dir, "import", str(other))
    assert code == 2 and "no importer" in out["message"]


def test_import_warns_when_another_source_has_the_session(capsys, data_dir, tmp_path):
    export = tmp_path / "manual.csv"
    export.write_text(
        "date,exercise,weight_kg,reps\n2025-07-24 11:25,Bench Press,62.5,8\n", encoding="utf-8"
    )
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


def test_profile_show_lists_a_missing_emergency_number(capsys, data_dir):
    assert "emergency_number" in run(capsys, data_dir, "profile", "show")[1]["missing"]
    main(["--data-dir", str(data_dir), "profile", "set", "emergency_number", "112", "--json"])
    capsys.readouterr()
    assert "emergency_number" not in run(capsys, data_dir, "profile", "show")[1]["missing"]


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
        ("emergency_number", "112"),
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


def test_foods_search_splits_a_quoted_phrase_into_words(capsys, data_dir):
    _, quoted = run(capsys, data_dir, "foods", "search", "pechuga pollo", "--region", "es")
    _, words = run(capsys, data_dir, "foods", "search", "pechuga", "pollo", "--region", "es")
    assert quoted == words and quoted["foods"]
    # an exact table name, comma included, finds its food
    _, named = run(capsys, data_dir, "foods", "search", "pechuga de pollo, cruda", "--region", "es")
    assert "pechuga de pollo, cruda" in [f["name_es"] for f in named["foods"]]


LABEL = (
    "products", "add", "--label", "--name", "Proteina chocolate", "--chain", "Mercadona",
    "--per", "100 g", "--kcal", "380", "--protein", "30", "--carbs", "40", "--fat", "9.5",
    "--allergens", "none",
)  # fmt: skip


def test_products_add_label_stores_the_label_values_without_network(capsys, data_dir, monkeypatch):
    import urllib.request

    def no_network(*a, **k):
        raise AssertionError("the label path must not reach the network")

    monkeypatch.delenv("COACH_OFF_CONTACT", raising=False)
    monkeypatch.setattr(urllib.request, "urlopen", no_network)
    code, out = run(capsys, data_dir, *LABEL, "--fibre", "3", "--allergens", "soja, leche;huevo")
    assert code == 0
    assert out["added"]["barcode"] == "label-proteina-chocolate"
    assert out["added"]["source"] == "label (entered by hand)"
    assert out["added"]["allergens"] == ["soja", "leche", "huevo"]
    row = catalogue.load(data_dir)[0]
    assert (row.kcal, row.fibre_g, row.per, row.chain) == (380, 3, "100 g", "Mercadona")
    code, out = run(
        capsys, data_dir, *LABEL[:3], "--name", "Otro", *LABEL[5:], "--barcode", "8400000000017"
    )
    assert code == 0 and out["added"]["barcode"] == "8400000000017"
    code, out = run(capsys, data_dir, *LABEL)  # same name again
    assert code != 0 and "already" in out["message"]


@pytest.mark.parametrize(
    "flag, value",
    [
        ("--kcal", "901"),
        ("--protein", "100.5"),
        ("--fat", "-1"),
        ("--carbs", "nan"),
        ("--fibre", "abc"),
        ("--barcode", "12ab"),
        ("--barcode", "../../x"),
        ("--barcode", "1234567"),
        ("--barcode", "123456789012345"),
    ],
)
def test_label_values_out_of_range_are_refused(capsys, data_dir, flag, value):
    code, out = run(capsys, data_dir, *LABEL, flag, value)
    assert code != 0 and out["error"] == "invalid"
    assert not (data_dir / "catalogue.csv").exists()


def test_label_energy_far_from_the_macros_warns(capsys, data_dir):
    args = [*LABEL]
    args[args.index("--kcal") + 1] = "200"
    _, out = run(capsys, data_dir, *args)
    assert out["warnings"] and "label again" in out["warnings"][0]


def test_label_requires_every_value(capsys, data_dir):
    args = [a for a in LABEL if a not in ("--kcal", "380")]
    code, out = run(capsys, data_dir, *args)
    assert code != 0 and "--kcal" in out["message"]


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
        run(capsys, data_dir, "strength", "progress")[1]["lifts"]["Bench Press (Barbell)"]["action"]
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
    progress = run(capsys, data_dir, "strength", "progress")[1]["lifts"]["Bench Press (Barbell)"]
    assert progress["action"] == "paused" and progress["load_kg"] == 60
    assert "fisioterapeuta" in progress["reasons"][0]
    _, flags = run(capsys, data_dir, "safety")
    assert flags["paused_exercises"]["bench press"]["reasons"] == progress["reasons"]

    _, out = run(capsys, data_dir, "injury", "clear", "Hombro Derecho", "--on", "2026-03-27")
    assert out["injuries"][0]["status"] == "cleared"
    assert out["injuries"][0]["cleared_on"] == "2026-03-27"
    progress = run(capsys, data_dir, "strength", "progress")[1]["lifts"]["Bench Press (Barbell)"]
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
    progress = run(capsys, data_dir, "strength", "progress")[1]["lifts"]["Bench Press (Barbell)"]
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


def test_an_empty_region_is_an_error_and_codes_are_stored_normalised(capsys, data_dir):
    for empty in ("", "   "):
        assert run(capsys, data_dir, "profile", "set", "region", empty)[0] == 2
    assert run(capsys, data_dir, "profile", "show")[1]["profile"]["region"] is None
    _, out = run(capsys, data_dir, "profile", "set", "region", "ES ")
    assert out["profile"]["region"] == "es"
    path = data_dir / "profile.yaml"
    text = "".join(
        line
        for line in path.read_text(encoding="utf-8").splitlines(True)
        if not line.startswith("region:")
    )
    path.write_text(text + 'region: ""\n', encoding="utf-8")  # empty is unset, not "none"
    assert "region" in run(capsys, data_dir, "profile", "show")[1]["missing"]


def test_a_region_that_is_a_path_is_refused_by_the_cli_and_the_file_loader(capsys, data_dir):
    for bad in ("../x", "/abs", "es/../es"):
        code, out = run(capsys, data_dir, "profile", "set", "region", bad)
        assert code == 2 and "not a region code" in out["message"]
    path = data_dir / "profile.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "region: ../x\n", encoding="utf-8")
    code, out = run(capsys, data_dir, "profile", "show")
    assert code == 2 and "not a region code" in out["message"]


def test_an_empty_region_flag_is_an_error(capsys, data_dir):
    for args in (("menu", "--item", "pollo=100"), ("foods", "search", "pollo")):
        code, out = run(capsys, data_dir, *args, "--region", "")
        assert code == 2 and "region" in out["message"]


def test_emergency_number_none_is_a_declined_number(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "emergency_number", "None")
    show = run(capsys, data_dir, "profile", "show")[1]
    assert show["profile"]["emergency_number"] == "none"
    assert "emergency_number" not in show["missing"]
    assert run(capsys, data_dir, "safety")[1]["emergency_number"] is None
    run(capsys, data_dir, "profile", "set", "region", "es")
    assert (
        run(capsys, data_dir, "safety")[1]["emergency_number"] == "112"
    )  # the region's still wins


def test_a_region_without_its_folder_is_refused_with_a_hint(capsys, data_dir):
    code, out = run(capsys, data_dir, "profile", "set", "region", "mx")
    assert code == 2
    assert "regions/mx" in out["message"] and "docs/adding-a-region.md" in out["message"]
    _, shown = run(capsys, data_dir, "profile", "show")
    assert shown["profile"]["region"] is None


def test_region_none_is_an_explicit_no_region(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "region", "es")
    code, out = run(capsys, data_dir, "profile", "set", "region", "none")
    assert code == 0 and out["profile"]["region"] == "none"


def test_a_profile_with_no_region_chosen_is_complete_and_works_without_a_table(capsys, data_dir):
    for field, value in [
        ("experience", "novice"),
        ("language", "es"),
        ("emergency_number", "999"),
    ]:
        run(capsys, data_dir, "profile", "set", field, value)
    assert run(capsys, data_dir, "profile", "show")[1]["missing"] == ["region"]  # never chosen
    run(capsys, data_dir, "profile", "set", "region", "none")
    assert run(capsys, data_dir, "profile", "show")[1]["missing"] == []
    assert run(capsys, data_dir, "safety")[1]["emergency_number"] == "999"
    code, out = run(capsys, data_dir, "menu", "--item", "arroz blanco, cocido=100")
    assert code == 0 and out["unknown"] == [] and out["kcal"] > 0
    assert run(capsys, data_dir, "foods", "search", "pollo")[0] == 0
    assert run(capsys, data_dir, "foods", "search", "pollo", "--region", "none")[0] == 0


def test_every_spelling_of_no_region_works_everywhere(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "region", "NONE")
    assert run(capsys, data_dir, "profile", "show")[1]["profile"]["region"] == "none"
    for flag in ("none", "NONE", "None"):
        assert run(capsys, data_dir, "foods", "search", "pollo", "--region", flag)[0] == 0
        assert run(capsys, data_dir, "menu", "--region", flag, "--item", "pollo=100")[0] == 0
    path = data_dir / "profile.yaml"
    path.write_text(path.read_text(encoding="utf-8") + "region: None\n", encoding="utf-8")
    for spelling in ("region: None", "region: NONE"):
        text = "".join(
            line
            for line in path.read_text(encoding="utf-8").splitlines(True)
            if not line.startswith("region:")
        )
        path.write_text(text + spelling + "\n", encoding="utf-8")
        code, out = run(capsys, data_dir, "safety")
        assert code == 0 and out["emergency_number"] is None
        assert run(capsys, data_dir, "menu", "--item", "pollo=100")[0] == 0
        assert run(capsys, data_dir, "profile", "show")[1]["missing"].count("region") == 0


def test_safety_prints_the_emergency_number(capsys, data_dir):
    assert run(capsys, data_dir, "safety")[1]["emergency_number"] is None
    run(capsys, data_dir, "profile", "set", "region", "es")
    assert run(capsys, data_dir, "safety")[1]["emergency_number"] == "112"
    run(capsys, data_dir, "profile", "set", "emergency_number", "061")
    assert run(capsys, data_dir, "safety")[1]["emergency_number"] == "061"


def _label(*extra, name="Proteina chocolate"):
    args = list(LABEL)
    args[args.index("--name") + 1] = name
    return [*args, *extra]


def test_label_slug_collision_is_a_different_product_not_a_replace(capsys, data_dir):
    # a key stored by an older version, when the slug alone was the key
    legacy = dataclasses.replace(
        SKYR_PRODUCT,
        barcode="label-yogur-0",
        product_name="Yogur 0%",
        source=catalogue.LABEL_SOURCE,
    )
    catalogue.save([legacy], data_dir)
    code, out = run(capsys, data_dir, *_label(name="Yogur 0"))
    assert code != 0
    assert "DIFFERENT product" in out["message"] and "--barcode" in out["message"]
    assert "--replace" not in out["message"]
    assert [p.product_name for p in catalogue.load(data_dir)] == ["Yogur 0%"]


def test_label_same_name_again_may_be_replaced(capsys, data_dir):
    run(capsys, data_dir, *_label())
    code, out = run(capsys, data_dir, *_label())
    assert code != 0 and "--replace" in out["message"]
    assert run(capsys, data_dir, *_label("--replace"))[0] == 0


def test_label_non_latin_names_get_a_stable_hash_key(capsys, data_dir):
    import hashlib

    from coach.text import fold

    _, out = run(capsys, data_dir, *_label(name="豆腐 1L"))
    digest = hashlib.sha1(fold("豆腐 1L").encode()).hexdigest()[:8]
    assert out["added"]["barcode"] == f"label-1l-{digest}"
    code, out = run(capsys, data_dir, *_label(name="牛奶 1L"))
    assert code == 0 and out["added"]["barcode"] != f"label-1l-{digest}"
    assert len(catalogue.load(data_dir)) == 2


def test_label_key_hash_ignores_case_and_accents_and_lossless_names_stay_plain(capsys, data_dir):
    _, a = run(capsys, data_dir, *_label(name="Yogur 0%"))
    _, b = run(capsys, data_dir, *_label("--replace", name="YÓGUR 0%"))
    assert a["added"]["barcode"] == b["added"]["barcode"] != "label-yogur-0"
    _, c = run(capsys, data_dir, *_label(name="Galleta de prueba"))
    assert c["added"]["barcode"] == "label-galleta-de-prueba"


def test_label_keys_are_injective_for_dashes_and_spaces(capsys, data_dir):
    _, spaced = run(capsys, data_dir, *_label(name="Galleta de prueba"))
    code, dashed = run(capsys, data_dir, *_label(name="Galleta-de-prueba"))
    assert code == 0 and dashed["added"]["barcode"] != spaced["added"]["barcode"]
    assert len(catalogue.load(data_dir)) == 2


@pytest.mark.parametrize(
    "extra",
    [["--kcal", "1"], ["--fibre", "1"], ["--allergens", "soja"], ["--barcode", "8400000000017"]],
)
def test_label_only_flags_without_label_are_refused(capsys, data_dir, extra):
    code, out = run(capsys, data_dir, "products", "add", "8400000000017", "--chain", "X", *extra)
    assert code != 0 and extra[0] in out["message"] and "--label" in out["message"]


def test_label_with_a_positional_barcode_is_refused(capsys, data_dir):
    code, out = run(capsys, data_dir, *LABEL[:3], "8400000000017", *LABEL[3:])
    assert code != 0 and "--barcode" in out["message"]


def test_label_barcode_must_be_ascii_digits(capsys, data_dir):
    code, _ = run(capsys, data_dir, *_label("--barcode", "٨٤٠٠٠٠٠٠٠٠٠١٧"))
    assert code != 0 and not (data_dir / "catalogue.csv").exists()


def test_label_stores_the_cleaned_name(capsys, data_dir):
    _, out = run(capsys, data_dir, *_label(name="Prote\x00ina\x1b choco"))
    assert out["added"]["product_name"] == "Prote ina choco"
    assert "\x00" not in (data_dir / "catalogue.csv").read_text(encoding="utf-8")


def test_label_numbers_take_a_decimal_comma_and_refuse_underscores(capsys, data_dir):
    code, out = run(capsys, data_dir, *_label("--fibre", "2,5"))
    assert code == 0 and out["added"]["fibre_g"] == 2.5
    for text, value in ((",5", 0.5), (".5", 0.5), ("5.", 5)):
        _, out = run(capsys, data_dir, *_label("--fibre", text, "--replace"))
        assert out["added"]["fibre_g"] == value, text
    for bad in ("1_0", "1,2,3", "1.2.3", "1e1", " ", ".", ","):
        code, _ = run(capsys, data_dir, *_label("--fibre", bad, name="Otro"))
        assert code != 0, bad
    for text, value in (("1,234", 1.23), ("9.500", 9.5)):
        _, out = run(capsys, data_dir, *_label("--fibre", text, "--replace"))
        assert out["added"]["fibre_g"] == value, text


def test_label_allergens_are_required_and_unknown_is_stored_with_a_warning(capsys, data_dir):
    no_allergens = [a for a in LABEL if a not in ("--allergens", "none")]
    code, out = run(capsys, data_dir, *no_allergens)
    assert code != 0 and "--allergens" in out["message"]
    _, none = run(capsys, data_dir, *LABEL)
    assert none["added"]["allergens"] == [] and none["warnings"] == []
    _, unknown = run(capsys, data_dir, *_label("--allergens", "unknown", name="Otro"))
    assert unknown["added"]["allergens"] == ["unknown"]
    assert (
        "allergens unknown: do not use for anyone with an allergy or intolerance"
        in (unknown["warnings"])
    )


@pytest.mark.parametrize(
    "text, stored",
    [
        ("Unknown", ["unknown"]),
        ("UNKNOWN", ["unknown"]),
        ("desconocido", ["unknown"]),
        ("No sé", ["unknown"]),
        ("unknown, soja", ["unknown", "soja"]),
        ("soja, Desconocidos", ["unknown", "soja"]),
        ("Ninguno", []),
        ("ninguna", []),
        ("Sin alérgenos", []),
        ("NONE", []),
    ],
)
def test_label_allergen_sentinels_are_folded_and_bilingual(capsys, data_dir, text, stored):
    _, out = run(capsys, data_dir, *_label("--allergens", text))
    assert out["added"]["allergens"] == stored
    assert bool(out["warnings"]) == ("unknown" in stored)


@pytest.mark.parametrize("text", ["none, leche", "ninguno; soja", "none, unknown", ", "])
def test_label_none_with_other_allergens_is_refused(capsys, data_dir, text):
    code, out = run(capsys, data_dir, *_label("--allergens", text))
    assert code != 0 and "--allergens" in out["message"]
    assert not (data_dir / "catalogue.csv").exists()


def test_label_replace_never_overwrites_an_open_food_facts_row(capsys, data_dir):
    off_row = dataclasses.replace(SKYR_PRODUCT, barcode="8400000000017")
    catalogue.save([off_row], data_dir)
    for extra in (["--replace"], []):
        code, out = run(capsys, data_dir, *_label("--barcode", "8400000000017", *extra))
        assert code != 0 and "Open Food Facts" in out["message"]
    assert catalogue.load(data_dir) == [off_row]


@pytest.mark.parametrize(
    "text, stored",
    [
        ("No lo sé", ["unknown"]),
        ("NS/NC", ["unknown"]),
        ("sin información", ["unknown"]),
        ("no consta", ["unknown"]),
        ("unknown.", ["unknown"]),
        ("Desconocido (ilegible)", ["unknown"]),
        ("Leche, leche, LECHE", ["Leche"]),
        ("No contiene", []),
        ("none, None", []),
    ],
)
def test_label_allergen_sentinels_fail_closed(capsys, data_dir, text, stored):
    _, out = run(capsys, data_dir, *_label("--allergens", text))
    assert out["added"]["allergens"] == stored


@pytest.mark.parametrize("text", ["none.", "ninguno declarado", "Ninguna, soja", "sin alergenos!"])
def test_label_ambiguous_sentinels_are_refused_not_stored(capsys, data_dir, text):
    code, out = run(capsys, data_dir, *_label("--allergens", text))
    assert code != 0 and "--allergens" in out["message"]
    assert not (data_dir / "catalogue.csv").exists()


@pytest.mark.parametrize("kcal", ["1.674", "1,234", "12.500", "99,999"])
def test_label_kcal_that_looks_like_kj_or_thousands_is_refused(capsys, data_dir, kcal):
    code, out = run(capsys, data_dir, *_label("--kcal", kcal))
    assert code != 0 and "kcal" in out["message"] and "kJ" in out["message"]


def test_label_over_another_source_says_how_to_get_a_separate_row(capsys, data_dir):
    catalogue.save([dataclasses.replace(SKYR_PRODUCT, barcode="8400000000017")], data_dir)
    _, out = run(capsys, data_dir, *_label("--barcode", "8400000000017"))
    assert "use a different --barcode, or omit --barcode" in out["message"]


@pytest.mark.parametrize("kcal", ["0,125", "0.500", "0.000"])
def test_label_kcal_with_a_leading_zero_is_a_plain_decimal(capsys, data_dir, kcal):
    code, _ = run(capsys, data_dir, *_label("--kcal", kcal))
    assert code == 0


@pytest.mark.parametrize(
    "text, stored",
    [
        ("piñones", ["piñones"]),
        ("frutos secos (piñones)", ["frutos secos (piñones)"]),
        ("sesamo", ["sesamo"]),
        ("ilegible", ["unknown"]),
        ("No legible", ["unknown"]),
        ("no indicado", ["unknown"]),
        ("not sure", ["unknown"]),
        ("N/A", ["unknown"]),
        ("?", ["unknown"]),
        ("no sé", ["unknown"]),
        ("soja, no lo sé", ["unknown", "soja"]),
    ],
)
def test_label_sentinels_match_whole_words_only(capsys, data_dir, text, stored):
    _, out = run(capsys, data_dir, *_label("--allergens", text))
    assert out["added"]["allergens"] == stored


@pytest.mark.parametrize("text", ["sin lactosa", "sin gluten", "soja, sin huevo"])
def test_label_sin_phrases_are_not_allergen_names(capsys, data_dir, text):
    code, out = run(capsys, data_dir, *_label("--allergens", text))
    assert code != 0 and "--allergens" in out["message"]
    assert not (data_dir / "catalogue.csv").exists()


@pytest.mark.parametrize(
    "text, stored",
    [
        ("ningún alérgeno", []),
        ("No alérgenos", []),
        ("sin alérgeno", []),
        ("nada", []),
        ("illegible", ["unknown"]),
        ("N.A.", ["unknown"]),
        ("nd", ["unknown"]),
        ("no data", ["unknown"]),
        ("no info", ["unknown"]),
        ("no información", ["unknown"]),
        ("not readable", ["unknown"]),
        ("soja?", ["unknown", "soja"]),
        ("soja (no sé)", ["unknown", "soja"]),
        ("leche, no sé si lleva soja", ["unknown", "leche", "soja"]),
    ],
)
def test_label_allergens_fail_closed_by_structure(capsys, data_dir, text, stored):
    _, out = run(capsys, data_dir, *_label("--allergens", text))
    assert out["added"]["allergens"] == stored
    assert bool(out["warnings"]) == ("unknown" in stored)


@pytest.mark.parametrize(
    "text",
    [
        "no sesamo",
        "no semillas",
        "gluten free",
        "lactose free",
        "libre de gluten",
        "sin lactosa",
        "sin trazas",
        "soja, no sesamo",
    ],
)
def test_label_free_from_claims_are_refused(capsys, data_dir, text):
    code, out = run(capsys, data_dir, *_label("--allergens", text))
    assert code != 0 and "write only the allergens the pack declares" in out["message"]
    assert not (data_dir / "catalogue.csv").exists()


UNRECOGNISED = "unrecognised allergen text: do not use for anyone with an allergy"


@pytest.mark.parametrize("text", ["n.a", "NA", "n/d", "-", "tbd", "kiwi"])
def test_label_unrecognised_allergen_text_is_stored_and_adds_unknown(capsys, data_dir, text):
    _, out = run(capsys, data_dir, *_label("--allergens", text))
    assert out["added"]["allergens"] == ["unknown", text]
    assert len(out["warnings"]) == 1 and out["warnings"][0].startswith(UNRECOGNISED)
    assert out["warnings"][0].endswith("until checked")


@pytest.mark.parametrize(
    "text, stored",
    [
        ("desconozco los alergenos", ["unknown"]),
        ("gluten (trigo, cebada)", ["gluten (trigo, cebada)"]),
        ("Frutos de cáscara (ilegible)", ["unknown", "Frutos de cáscara"]),
        ("piñones", ["piñones"]),
        ("sesamo", ["sesamo"]),
        ("Sésamo, Piñones; Huevo", ["Sésamo", "Piñones", "Huevo"]),
        ("soja (no sé)", ["unknown", "soja"]),
        ("leche, no sé si lleva soja", ["unknown", "leche", "soja"]),
    ],
)
def test_label_recognised_allergens_keep_the_clients_spelling(capsys, data_dir, text, stored):
    _, out = run(capsys, data_dir, *_label("--allergens", text))
    assert out["added"]["allergens"] == stored
    assert not any(w.startswith(UNRECOGNISED) for w in out["warnings"])


@pytest.mark.parametrize(
    "text", ["without gluten", "exento de gluten", "doesn't contain nuts", "libre de soja"]
)
def test_label_more_free_from_claims_are_refused(capsys, data_dir, text):
    code, out = run(capsys, data_dir, *_label("--allergens", text))
    assert code != 0 and "write only the allergens the pack declares" in out["message"]


def test_label_with_energy_but_no_macros_warns_in_a_full_sentence(capsys, data_dir):
    args = _label("--kcal", "100", "--protein", "0", "--carbs", "0", "--fat", "0")
    code, out = run(capsys, data_dir, *args, "--replace")
    assert code == 0
    assert out["warnings"] == [
        "label kcal is stated but no energy-yielding macros are listed: read the label "
        "again, fix it with --replace"
    ]


def test_label_plain_key_ignores_accents(capsys, data_dir):
    _, out = run(capsys, data_dir, *_label(name="Proteína chocolate"))
    assert out["added"]["barcode"] == "label-proteina-chocolate"


def test_explicit_barcode_with_replace_may_rename_the_product(capsys, data_dir):
    run(capsys, data_dir, *_label("--barcode", "8400000000017", name="Protein choco"))
    code, out = run(
        capsys,
        data_dir,
        *_label("--barcode", "8400000000017", "--replace", name="Proteina chocolate"),
    )
    assert code == 0
    assert [p.product_name for p in catalogue.load(data_dir)] == ["Proteina chocolate"]


def test_confirm_per_is_refused_with_label(capsys, data_dir):
    code, out = run(capsys, data_dir, *_label("--confirm-per"))
    assert code != 0 and "--confirm-per" in out["message"]


def test_label_name_clash_with_a_known_food_via_another_barcode(capsys, data_dir):
    code, out = run(capsys, data_dir, *_label(name="pechuga de pollo, cruda"))
    assert code != 0 and "already a food or product name" in out["message"]
    run(capsys, data_dir, *_label("--barcode", "8400000000017"))
    code, out = run(capsys, data_dir, *_label("--barcode", "8400000000024"))
    assert code != 0 and "already a food or product name" in out["message"]


def test_label_energy_warning_does_not_blame_the_source(capsys, data_dir):
    args = _label()
    args[args.index("--kcal") + 1] = "200"
    _, out = run(capsys, data_dir, *args)
    warning = out["warnings"][0]
    assert "source uses" not in warning and "4/4/9" in warning
    assert "read the label again" in warning and "check the pack" not in warning


# Beta p3-antonio-I1/I5, p1-lucia-I8.
def test_cardiac_symptoms_hold_the_target_at_maintenance(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.cardiac_symptoms", "true")
    _, out = run(capsys, data_dir, "energy")
    assert out["target"]["deficit"] == 0
    _, macros = run(capsys, data_dir, "macros")
    assert macros["in_deficit"] is False
    _, raised = run(capsys, data_dir, "macros", "--kcal", "1700", "--in-deficit")
    assert raised["kcal"] == out["target"]["kcal"] and raised["in_deficit"] is False


def test_checkin_symptoms_set_the_cardiac_flag(capsys, data_dir):
    code, out = run(capsys, data_dir, "checkin", "add", "--symptoms", "dizzy, chest_pain")
    assert code == 0 and out["symptoms"] == ["dizzy", "chest_pain"]
    assert "dizzy" in out["notes"]
    assert load_profile(data_dir / "profile.yaml").screening["cardiac_symptoms"] is True
    _, safety = run(capsys, data_dir, "safety")
    assert safety["refer_gp"] and safety["no_training"] and safety["deferral_line"]


def test_checkin_unknown_symptom_is_refused(capsys, data_dir):
    code, out = run(capsys, data_dir, "checkin", "add", "--symptoms", "headache")
    assert code == 2 and "chest_pain" in out["message"]
    assert "cardiac_symptoms" not in load_profile(data_dir / "profile.yaml").screening


def test_checkin_notes_report_possible_red_flags_without_setting_one(capsys, data_dir):
    code, out = run(capsys, data_dir, "checkin", "add", "--notes", "mareo al subir escaleras")
    assert code == 0 and out["possible_red_flags"] == ["dizzy"]
    assert "cardiac_symptoms" not in load_profile(data_dir / "profile.yaml").screening


def test_checkin_symptoms_are_kept_when_another_field_is_refused(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "screening.scoff_positive", "true")
    code, _ = run(capsys, data_dir, "checkin", "add", "--weight", "70", "--symptoms", "faint")
    assert code == 2
    assert load_profile(data_dir / "profile.yaml").screening["cardiac_symptoms"] is True


def test_checkin_records_neck_jaw_or_arm_pain(capsys, data_dir):
    code, out = run(capsys, data_dir, "checkin", "add", "--symptoms", "neck_jaw_arm_pain")
    assert code == 0 and out["symptoms"] == ["neck_jaw_arm_pain"]


# Beta p1-lucia-I1, p6-james-I1: no check-ins dated after today.
def test_checkin_refuses_a_future_date(capsys, data_dir):
    code, out = run(capsys, data_dir, "checkin", "add", "--date", "2026-04-02", "--weight", "80")
    assert code == 2 and "after today" in out["message"]
    assert not (data_dir / "checkins.csv").exists()
    code, _ = run(capsys, data_dir, "checkin", "add", "--date", TODAY, "--weight", "80")
    assert code == 0


# Beta p1-lucia-I2: the echo is the row as stored, plus the fields just given.
def test_checkin_echo_shows_the_merged_row(capsys, data_dir):
    run(capsys, data_dir, "checkin", "add", "--weight", "81", "--intake", "1700", "--sleep", "6.5")
    _, out = run(capsys, data_dir, "checkin", "add", "--weight", "81.7")
    assert out["weight_kg"] == 81.7 and out["intake_kcal"] == 1700 and out["sleep_hours"] == 6.5
    assert out["given"] == ["weight_kg"]


# Beta p1-lucia-I4, p4-sara-I5, p5-elena-I12: "none" means an empty list.
@pytest.mark.parametrize("value", ["none", "None", "no", "ninguno", "ninguna", "nada"])
def test_profile_none_medications_is_an_empty_list(capsys, data_dir, value):
    _, out = run(capsys, data_dir, "profile", "set", "medications", value)
    assert out["profile"]["medications"] == [] and out["unrecognised"]["medications"] == []


# Beta p1-lucia-I3, p4-sara-I4: pregnancy is a condition token, not a field.
def test_profile_set_pregnant_points_to_conditions(capsys, data_dir):
    code, out = run(capsys, data_dir, "profile", "set", "pregnant", "true")
    assert code == 2 and "conditions pregnant" in out["message"]


# Beta p3-antonio-I7: an unknown medication is recorded, and the output says so plainly.
def test_unrecognised_items_are_explained(capsys, data_dir):
    _, out = run(capsys, data_dir, "profile", "set", "medications", "enalapril")
    assert out["unrecognised"]["medications"] == ["enalapril"]
    assert "no calculation depends on" in out["unrecognised_note"]


# Beta p3-antonio-I6: the region's number counts, so it is not asked for again.
def test_region_emergency_number_is_not_missing(capsys, data_dir):
    _, out = run(capsys, data_dir, "profile", "show")
    assert "emergency_number" in out["missing"]
    _, out = run(capsys, data_dir, "profile", "set", "region", "es")
    assert "emergency_number" not in out["missing"]


# Beta p6-james-I1: a typo such as 99 for 72 kg is flagged, not silently stored.
def test_checkin_warns_on_an_implausible_weight_jump(capsys, data_dir):
    run(capsys, data_dir, "checkin", "add", "--date", "2026-03-30", "--weight", "72")
    _, out = run(capsys, data_dir, "checkin", "add", "--weight", "99")
    assert any("27" in w and "2026-03-30" in w for w in out["warnings"])
    _, calm = run(capsys, data_dir, "checkin", "add", "--date", "2026-03-31", "--weight", "72.4")
    assert calm["warnings"] == []


def test_checkin_weight_jump_after_a_long_gap_is_still_flagged(capsys, data_dir):
    run(capsys, data_dir, "checkin", "add", "--date", "2026-03-01", "--weight", "72")
    _, out = run(capsys, data_dir, "checkin", "add", "--weight", "99")
    assert out["warnings"]


def test_future_date_error_says_symptoms_were_recorded(capsys, data_dir):
    code, out = run(
        capsys, data_dir, "checkin", "add", "--date", "2026-04-02", "--symptoms", "chest_pain"
    )
    assert code == 2 and "symptoms recorded" in out["message"]


def test_energy_prints_its_ranges(capsys, data_dir):
    _, out = run(capsys, data_dir, "energy")
    low, high = out["rmr_range"]
    assert low < out["rmr"] < high and out["tdee_range"][0] < out["tdee"] < out["tdee_range"][1]


def test_menu_protein_passes_from_the_band_low_end():
    from coach.cli import menu_check

    targets = {"kcal": 2000, "protein_g": 160, "protein_min_g": 128, "fat_min_g": 50, "fibre_g": 25}
    totals = {"kcal": 2000, "protein_g": 130, "fat_g": 60, "fibre_g": 30}
    assert menu_check(totals, targets)["protein_g"] == "ok"
    assert menu_check(totals | {"protein_g": 120}, targets)["protein_g"] == "under"


# Beta p2-marcus-I1: a heavy lifter's log far from the 8-12 default is flagged, so the skill
# asks for the range instead of judging 5-rep sets against 12.
def _deadlifts(data_dir, reps=5):
    sets = [
        ExerciseSet(
            "hevy_csv",
            datetime(2026, 3, d, 18, 0),
            "Deadlift (Barbell)",
            0,
            i,
            weight_kg=120.0,
            reps=reps,
        )
        for d in (18, 25)
        for i in range(3)
    ]
    append(sets, data_dir / "sessions.csv")


def test_progress_flags_a_log_outside_the_default_rep_range(capsys, data_dir):
    _deadlifts(data_dir)
    _, out = run(capsys, data_dir, "strength", "progress")
    assert out["rep_range_source"]["Deadlift (Barbell)"] == "default"
    assert "median 5" in out["rep_range_notes"]["Deadlift (Barbell)"]
    _, given = run(capsys, data_dir, "strength", "progress", "--rep-range", "deadlift=3-6")
    assert given["rep_range_source"]["Deadlift (Barbell)"] == "given"
    assert given["rep_range_notes"] == {}


def test_progress_no_note_when_the_log_fits_the_default(capsys, data_dir):
    _deadlifts(data_dir, reps=10)
    _, out = run(capsys, data_dir, "strength", "progress")
    assert out["rep_range_notes"] == {}


# Beta p2-marcus-I6/I7: a planned week is checked before it is prescribed.
def test_plan_sets_counts_a_planned_week(capsys, data_dir):
    plan = data_dir / "week.yaml"
    plan.write_text(
        "sessions:\n"
        "  - name: Push\n"
        "    exercises:\n"
        "      - {exercise: Bench Press (Barbell), sets: 3}\n"
        "      - {exercise: Overhead Press (Barbell), sets: 3}\n"
        "  - name: Pull\n"
        "    exercises:\n"
        "      - {exercise: Lat Pulldown (Cable), sets: 4}\n"
        "      - {exercise: Made Up Lift, sets: 2}\n",
        encoding="utf-8",
    )
    code, out = run(capsys, data_dir, "strength", "plan-sets", str(plan))
    assert code == 0 and out["sets"]["chest"] == 3
    assert "chest" in out["below_reference"] and out["reference_sets_per_week"] == 10
    assert out["unmapped"] == ["Made Up Lift"]


def test_plan_sets_rejects_a_malformed_plan(capsys, data_dir):
    plan = data_dir / "week.yaml"
    plan.write_text(
        "sessions:\n  - name: Push\n    exercises:\n      - {exercise: Bench}\n", encoding="utf-8"
    )
    code, out = run(capsys, data_dir, "strength", "plan-sets", str(plan))
    assert code == 2 and "sets" in out["message"]


# Beta p2-marcus-I4/I5.
def test_import_reports_conflicting_reexports(capsys, data_dir, tmp_path):
    first = tmp_path / "a.csv"
    first.write_text(
        "date,exercise,weight_kg,reps\n2025-07-24 11:25,Bench Press,62.5,8\n", encoding="utf-8"
    )
    run(capsys, data_dir, "import", str(first))
    lbs = tmp_path / "b.csv"
    lbs.write_text(
        "date,exercise,weight_lbs,reps\n2025-07-24 11:25,Bench Press,140,8\n", encoding="utf-8"
    )
    _, out = run(capsys, data_dir, "import", str(lbs))
    assert out["duplicates"] == 1 and out["conflicts"] == 1
    assert any("kept the stored" in w for w in out["warnings"])


def test_import_skips_sets_after_today(capsys, data_dir, tmp_path):
    export = tmp_path / "future.csv"
    export.write_text(
        "date,exercise,weight_kg,reps\n"
        "2026-03-30 10:00,Squat,80,5\n"
        "2026-04-05 10:00,Squat,82.5,5\n",
        encoding="utf-8",
    )
    _, out = run(capsys, data_dir, "import", str(export))
    assert out["added"] == 1 and out["skipped_future"] == 1
    assert any("after today" in w for w in out["warnings"])


# Beta p1-lucia-I10, p5-elena-I13: plan.md's header is checked against the CLI.
def _plan_md(data_dir, kcal, in_deficit="true"):
    (data_dir / "plan.md").write_text(
        f"Date: 2026-04-01\ntarget_kcal: {kcal}\nin_deficit: {in_deficit}\n\n## Training week\n",
        encoding="utf-8",
    )


def test_plan_check_matches_the_cli(capsys, data_dir):
    _, macros = run(capsys, data_dir, "macros")
    _plan_md(data_dir, macros["kcal"])
    code, out = run(capsys, data_dir, "plan", "check")
    assert code == 0 and out["ok"] is True and out["problems"] == []
    # A target agreed at /review differs from a fresh estimate: a note, not a problem.
    _plan_md(data_dir, macros["kcal"] + 300)
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is True and any("fresh estimate" in n for n in out["notes"])
    # A deficit the safety rules now forbid is a problem.
    run(capsys, data_dir, "profile", "set", "screening.cardiac_symptoms", "true")
    _plan_md(data_dir, macros["kcal"])
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is False and any("safety rules" in p for p in out["problems"])


def test_reexport_in_pounds_is_not_a_conflict(capsys, data_dir, tmp_path):
    kg = tmp_path / "kg.csv"
    kg.write_text(
        "date,exercise,weight_kg,reps\n2025-07-24 11:25,Bench Press,100,8\n", encoding="utf-8"
    )
    run(capsys, data_dir, "import", str(kg))
    lbs = tmp_path / "lbs.csv"
    lbs.write_text(
        "date,exercise,weight_lbs,reps\n2025-07-24 11:25,Bench Press,220.46,8\n", encoding="utf-8"
    )
    _, out = run(capsys, data_dir, "import", str(lbs))
    assert out["duplicates"] == 1 and out["conflicts"] == 0


def test_plan_check_reports_a_missing_header(capsys, data_dir):
    (data_dir / "plan.md").write_text("# My plan\n", encoding="utf-8")
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is False and any("Date" in p for p in out["problems"])


def test_progress_star_range_counts_as_given(capsys, data_dir):
    _deadlifts(data_dir)
    _, out = run(capsys, data_dir, "strength", "progress", "--rep-range", "*=3-6")
    assert out["rep_range_source"]["Deadlift (Barbell)"] == "given"
    assert out["rep_range_notes"] == {}


def test_plan_sets_lists_untrained_muscles_below_reference(capsys, data_dir):
    plan = data_dir / "week.yaml"
    plan.write_text(
        "sessions:\n  - exercises:\n      - {exercise: Bench Press (Barbell), sets: 12}\n",
        encoding="utf-8",
    )
    _, out = run(capsys, data_dir, "strength", "plan-sets", str(plan))
    assert "chest" not in out["below_reference"] and "quads" in out["below_reference"]


@pytest.mark.parametrize("text", ["sessions: [oops", "- just a list\n", "sessions: [Push]\n"])
def test_plan_sets_rejects_broken_yaml(capsys, data_dir, text):
    plan = data_dir / "week.yaml"
    plan.write_text(text, encoding="utf-8")
    code, out = run(capsys, data_dir, "strength", "plan-sets", str(plan))
    assert code == 2 and out["error"] == "invalid"


def test_plan_check_accepts_the_kcal_as_macros_kcal_prints_it(capsys, data_dir):
    _, macros = run(capsys, data_dir, "macros")
    _plan_md(data_dir, f"{float(macros['kcal'])}")  # `coach macros --kcal` prints 2081.0
    _, out = run(capsys, data_dir, "plan", "check")
    assert out["ok"] is True, out["problems"]
