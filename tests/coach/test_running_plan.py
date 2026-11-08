"""Beta 3 p6-james-N3, N8, N9, p6-james-I5 (b2), p6-james-I7 (b1): race goal pace, a running
deload in km, and a long-run cap after an injury that never returns to the spike."""

import json
from datetime import date, timedelta

import pytest

from coach.cli import main
from coach.profile import Profile, save_profile
from coach.runs import Run, append_runs, week
from coach.safety import flags
from coach.zones import hr_zones

TODAY = date(2026, 11, 8)


@pytest.fixture
def data_dir(tmp_path):
    save_profile(
        Profile(
            sex="male",
            birth_date=date(1992, 5, 1),
            height_cm=178,
            weight_kg=72,
            goal="maintenance",
            activity_level="desk_training",
            sport="running",
            experience="intermediate",
            hr_max=191,
            hr_rest=48,
            race_date=date(2026, 12, 20),
            race_km=21.1,
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
    code = main(["--data-dir", str(data_dir), "--today", TODAY.isoformat(), *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def log(data_dir, *runs):
    append_runs(
        [Run(TODAY - timedelta(days=d), km, km * 6) for d, km in runs], data_dir / "runs.csv"
    )


def test_goal_time_gives_the_race_pace(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "race_goal_time", "1:55:00")
    log(data_dir, (3, 10.0))
    _, out = run(capsys, data_dir, "runs", "plan")
    assert out["race"]["goal_time"] == "1:55:00"
    assert out["race"]["goal_pace_per_km"] == "5:27"


def test_goal_time_is_validated(capsys, data_dir):
    code, _ = run(capsys, data_dir, "profile", "set", "race_goal_time", "fast")
    assert code == 2
    code, _ = run(capsys, data_dir, "profile", "set", "race_goal_time", "1:75:00")
    assert code == 2


def test_a_recent_race_predicts_the_half_with_riegel(capsys, data_dir):
    log(data_dir, (3, 10.0))
    _, out = run(capsys, data_dir, "runs", "plan", "--recent-km", "10", "--recent-time", "50:00")
    # 50:00 x (21.1 / 10) ** 1.07 = 6670 s = 1:51:10
    assert out["race"]["predicted_time"] == "1:51:10"


def test_no_riegel_prediction_for_a_marathon(capsys, data_dir):
    run(capsys, data_dir, "profile", "set", "race_km", "42.2")
    log(data_dir, (3, 10.0))
    _, out = run(capsys, data_dir, "runs", "plan", "--recent-km", "10", "--recent-time", "50:00")
    assert out["race"]["predicted_time"] is None
    assert any("marathon" in n for n in out["notes"])


def test_a_running_deload_cuts_last_weeks_km(capsys, data_dir):
    log(data_dir, (1, 10.0), (3, 8.0), (5, 12.0))
    code, out = run(capsys, data_dir, "runs", "deload", "--signs", "performance_stall,poor_sleep")
    assert code == 0, out
    assert out["last_week_km"] == 30.0
    assert out["deload_week_km"] == [15.0, 21.0]


def test_no_deload_while_training_is_stopped(capsys, data_dir):
    run(capsys, data_dir, "checkin", "add", "--symptoms", "unusual_fatigue")
    for command in (["runs", "deload"], ["strength", "deload"]):
        code, out = run(capsys, data_dir, *command, "--signs", "performance_stall,poor_sleep")
        assert code == 2 and "on hold" in out["message"]


def test_the_cap_after_an_injury_stays_below_the_spike_that_preceded_it():
    profile = Profile(sex="male", birth_date=date(1992, 5, 1), hr_max=191, hr_rest=48)
    f = flags(profile, TODAY)
    shown = hr_zones(profile, f, 48, 191, TODAY)
    logged = [Run(TODAY - timedelta(days=10), 14.0, 84), Run(TODAY - timedelta(days=2), 16.0, 96)]
    result = week(logged, TODAY, shown, [], TODAY, hold_progression=True)
    assert result["long_run_cap_km"] == pytest.approx(14.0 * 1.10)


@pytest.mark.parametrize(
    "recent", [("-5", "25:00"), ("0", "25:00"), ("42.2", "3:30:00"), ("10", None), (None, "50:00")]
)
def test_a_recent_race_must_be_a_shorter_race_given_in_full(capsys, data_dir, recent):
    log(data_dir, (3, 10.0))
    km, time = recent
    args = (["--recent-km", km] if km else []) + (["--recent-time", time] if time else [])
    code, out = run(capsys, data_dir, "runs", "plan", *args)
    assert code == 2, out


def test_a_recent_time_over_an_hour_may_be_typed_as_minutes(capsys, data_dir):
    log(data_dir, (3, 10.0))
    _, out = run(capsys, data_dir, "runs", "plan", "--recent-km", "10", "--recent-time", "75:00")
    _, same = run(capsys, data_dir, "runs", "plan", "--recent-km", "10", "--recent-time", "1:15:00")
    assert out["race"]["predicted_time"] == same["race"]["predicted_time"] is not None


def test_no_running_deload_while_running_is_paused_unassessed(capsys, data_dir):
    log(data_dir, (1, 10.0))
    run(capsys, data_dir, "injury", "add", "rodilla", "--exercises", "running")
    code, out = run(capsys, data_dir, "runs", "deload", "--signs", "performance_stall,poor_sleep")
    assert code == 2 and "running is paused" in out["message"]


def test_a_running_deload_cuts_the_last_logged_week(capsys, data_dir):
    log(data_dir, (10, 10.0), (12, 10.0))
    _, out = run(capsys, data_dir, "runs", "deload", "--signs", "performance_stall,poor_sleep")
    assert out["last_week_km"] == 20.0


def test_a_chain_of_spikes_never_lifts_the_cap_under_a_hold():
    profile = Profile(sex="male", birth_date=date(1992, 5, 1), hr_max=191, hr_rest=48)
    shown = hr_zones(profile, flags(profile, TODAY), 48, 191, TODAY)
    logged = [
        Run(TODAY - timedelta(days=12), 10.0, 60),
        Run(TODAY - timedelta(days=8), 12.0, 72),
        Run(TODAY - timedelta(days=4), 14.0, 84),
    ]
    result = week(logged, TODAY, shown, [], TODAY, hold_progression=True)
    assert result["long_run_cap_km"] == pytest.approx(10.0 * 1.10 * 1.10)
