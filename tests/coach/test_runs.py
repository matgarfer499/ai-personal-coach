from datetime import date, timedelta

import pytest

from coach import runs
from coach.profile import Profile
from coach.runs import Run, append_runs, read_runs, spikes, taper, week
from coach.safety import flags
from coach.zones import hr_zones

TODAY = date(2026, 4, 1)


def zones_for(**kw):
    profile = Profile(
        **({"birth_date": date(1986, 1, 1), "screening": {"parq_any_yes": False}} | kw)
    )
    return profile, flags(profile, TODAY)


def test_append_and_read_round_trip(tmp_path):
    path = tmp_path / "runs.csv"
    first = Run(date(2026, 3, 30), 10.0, 55.5, avg_hr=148, max_hr=165, rpe=13, notes="tempo")
    assert append_runs([first], path).added == 1
    assert read_runs(path) == [first]


def test_the_same_run_twice_is_a_duplicate(tmp_path):
    path = tmp_path / "runs.csv"
    run = Run(date(2026, 3, 30), 10.0, 55.5)
    append_runs([run], path)
    again = Run(date(2026, 3, 30), 10.0, 55.5, source="generic_runs_csv")
    result = append_runs([again, Run(date(2026, 3, 31), 5.0, 30)], path)
    assert (result.added, result.duplicates) == (1, 1)
    assert len(read_runs(path)) == 2


@pytest.mark.parametrize(
    "kw,message",
    [
        ({"km": 0}, "km"),
        ({"km": 400}, "km"),
        ({"minutes": 0.5}, "minutes"),
        ({"avg_hr": 20}, "avg_hr"),
        ({"max_hr": 250}, "max_hr"),
        ({"avg_hr": 170, "max_hr": 160}, "avg_hr"),
        ({"rpe": 21}, "rpe"),
        ({"rpe": 5}, "rpe"),
    ],
)
def test_implausible_values_are_refused(kw, message):
    with pytest.raises(ValueError, match=message):
        runs.check(Run(**({"date": TODAY, "km": 10.0, "minutes": 60.0} | kw)))


# cardio-health.md "Running load progression: cap single-run spikes, not just weekly totals":
# a run more than about 10% longer than the longest run of the previous 30 days.
def test_spike_against_the_longest_run_of_the_previous_30_days():
    logged = [
        Run(date(2026, 3, 1), 14.0, 80),  # 31 days before the 1 April run: outside
        Run(date(2026, 3, 10), 10.0, 60),
        Run(date(2026, 3, 20), 11.0, 65),  # exactly 10% longer: not a spike
        Run(date(2026, 4, 1), 12.2, 72),  # over 11 x 1.1 = 12.1: a spike
    ]
    found = spikes(logged, date(2026, 3, 2), TODAY)
    assert [s["date"] for s in found] == [date(2026, 4, 1)]
    assert found[0]["longest_previous_km"] == 11.0
    assert found[0]["cap_km"] == pytest.approx(12.1)


def test_spike_note_states_the_rule_numbers():
    logged = [Run(date(2026, 3, 20), 11.0, 65), Run(date(2026, 4, 1), 12.2, 72)]
    profile, f = zones_for()
    notes = week(logged, TODAY, hr_zones(profile, f, today=TODAY), [])["notes"]
    assert any("about 10% longer" in n and "previous 30 days" in n for n in notes)


def test_no_spike_without_an_earlier_run():
    assert spikes([Run(TODAY, 20.0, 120)], TODAY - timedelta(days=6), TODAY) == []


def test_week_totals_and_the_next_long_run_cap():
    logged = [
        Run(date(2026, 3, 24), 8.0, 50),  # the week before
        Run(date(2026, 3, 26), 6.0, 36),
        Run(date(2026, 3, 29), 12.0, 75),
        Run(date(2026, 4, 1), 5.0, 30),
    ]
    profile, f = zones_for()
    result = week(logged, TODAY, hr_zones(profile, f, today=TODAY), [])
    assert result["week"] == {"start": date(2026, 3, 26), "end": TODAY}
    assert (result["runs"], result["km"], result["minutes"]) == (3, 23.0, 141)
    assert result["longest_km"] == 12.0
    assert result["previous_week"] == {"km": 8.0, "runs": 1}
    assert result["change_pct"] == pytest.approx(187.5)
    assert result["long_run_cap_km"] == pytest.approx(13.2)


def test_time_per_zone_from_average_heart_rate():
    profile, f = zones_for()
    shown = hr_zones(profile, f, hr_rest=48, hr_max=191, today=TODAY)
    logged = [
        Run(TODAY - timedelta(days=1), 10.0, 60, avg_hr=140),  # 64% HRR: vigorous
        Run(TODAY, 5.0, 35, avg_hr=118),  # 49%: moderate
        Run(TODAY, 3.0, 20),
    ]
    result = week(logged, TODAY, shown, shown.zones)
    assert result["zone_minutes"]["vigorous"] == 60
    assert result["zone_minutes"]["moderate"] == 35
    assert result["zone_minutes"]["no_hr"] == 20


def test_capped_client_still_sees_minutes_above_moderate():
    profile, f = zones_for(screening={"parq_any_yes": True})
    shown = hr_zones(profile, f, hr_rest=48, hr_max=191, today=TODAY)
    every = runs.zones_to_describe(profile, f, 48, 191, TODAY)
    logged = [Run(TODAY, 10.0, 60, avg_hr=186)]
    result = week(logged, TODAY, shown, every)
    assert result["zone_minutes"]["near_maximal"] == 60
    assert any("PAR-Q+ specific thresholds" in n for n in result["notes"])


def test_no_time_per_zone_when_zones_are_rpe_only():
    profile, f = zones_for(medications=["beta_blocker"])
    shown = hr_zones(profile, f, hr_rest=48, hr_max=191, today=TODAY)
    every = runs.zones_to_describe(profile, f, 48, 191, TODAY)
    result = week([Run(TODAY, 10.0, 60, avg_hr=150)], TODAY, shown, every)
    assert result["zone_minutes"] is None
    assert any("RPE" in n for n in result["notes"])


# cardio-health.md "HRmax: formulas and setting the anchor": use an observed higher peak.
def test_a_higher_logged_peak_is_pointed_out():
    profile, f = zones_for()
    shown = hr_zones(profile, f, hr_rest=48, hr_max=180, today=TODAY)
    result = week([Run(TODAY, 5.0, 25, max_hr=188)], TODAY, shown, shown.zones)
    assert any("hr_max 188" in n for n in result["notes"])


# cardio-health.md "Taper before a goal race": about 2 weeks (up to 3), weekly distance cut by
# about 41-60%, intensity and runs per week kept.
def test_taper_inside_the_window():
    logged = [Run(date(2026, 3, 30), 20.0, 120), Run(date(2026, 3, 27), 10.0, 60)]
    result = taper(date(2026, 4, 12), TODAY, logged)
    assert result["in_window"] is True
    assert (result["weeks"], result["max_weeks"]) == (2, 3)
    assert result["distance_cut"] == (0.41, 0.60)
    assert result["starts_on"] == date(2026, 3, 29)
    assert result["reference_week_km"] == 10.0  # one logged week before the taper starts
    assert result["taper_week_km"] == (pytest.approx(4.0), pytest.approx(5.9))


def test_taper_far_from_the_race_gives_its_dates():
    result = taper(date(2026, 6, 1), TODAY, [])
    assert result["in_window"] is False
    assert result["starts_on"] == date(2026, 5, 18)
    assert result["earliest_start"] == date(2026, 5, 11)


def test_taper_refuses_a_past_race():
    with pytest.raises(ValueError, match="before today"):
        taper(date(2026, 3, 1), TODAY, [])


# coach/safety.py no_training (cardiac symptoms) and heart disease: no zones, so no time per
# zone and no cap for a next run.
@pytest.mark.parametrize(
    "kw", [{"screening": {"cardiac_symptoms": True}}, {"conditions": ["heart_disease"]}]
)
def test_no_zones_means_no_time_per_zone_and_no_next_run_cap(kw):
    profile, f = zones_for(**kw)
    shown = hr_zones(profile, f, hr_rest=48, hr_max=191, today=TODAY)
    every = runs.zones_to_describe(profile, f, 48, 191, TODAY)
    result = week([Run(TODAY, 10.0, 60, avg_hr=150)], TODAY, shown, every)
    assert result["zone_minutes"] is None and result["notes"]
    if f.no_training:
        assert result["long_run_cap_km"] is None


# The next run comes after today, so its cap counts the 30 days back from today, not from the
# reviewed week's end: after a break with no run in 30 days there is no baseline to cap from.
def test_next_long_run_cap_counts_back_from_today():
    profile, f = zones_for()
    shown = hr_zones(profile, f, today=TODAY)
    old = TODAY - timedelta(days=40)
    result = week([Run(old, 20.0, 120)], old, shown, [], today=TODAY)
    assert result["long_run_cap_km"] is None
    recent = [Run(TODAY - timedelta(days=10), 10.0, 60)]
    assert week(recent, TODAY - timedelta(days=10), shown, [], today=TODAY)[
        "long_run_cap_km"
    ] == pytest.approx(11.0)


# docs/safety.md hold_progression: no added load or intensity, so the long run does not grow.
def test_no_longer_long_run_while_progression_is_on_hold():
    profile, f = zones_for()
    shown = hr_zones(profile, f, today=TODAY)
    result = week([Run(TODAY, 10.0, 60)], TODAY, shown, [], hold_progression=True)
    assert result["long_run_cap_km"] == pytest.approx(10.0)
    assert any("on hold" in n for n in result["notes"])


# docs/safety.md: an injury that lists running pauses it, so there is no next run to cap.
def test_a_running_pause_gives_no_cap_and_no_hold_note():
    profile, f = zones_for()
    shown = hr_zones(profile, f, today=TODAY)
    result = week([Run(TODAY, 10.0, 60)], TODAY, shown, [], hold_progression=True, paused=True)
    assert result["long_run_cap_km"] is None
    assert not any("on hold" in n for n in result["notes"])


# Two identical runs in one log (a morning and an evening 5 km) are two runs; re-importing the
# same log adds neither again.
def test_identical_runs_in_one_batch_are_both_stored(tmp_path):
    path = tmp_path / "runs.csv"
    twice = [Run(TODAY, 5.0, 30), Run(TODAY, 5.0, 30)]
    assert (append_runs(twice, path).added, len(read_runs(path))) == (2, 2)
    result = append_runs(twice, path)
    assert (result.added, result.duplicates) == (0, 2)


def test_an_average_below_the_resting_floor_is_very_light_not_no_hr():
    profile, f = zones_for()
    shown = hr_zones(profile, f, hr_rest=60, hr_max=190, today=TODAY)
    result = week([Run(TODAY, 3.0, 30, avg_hr=58)], TODAY, shown, shown.zones)
    assert result["zone_minutes"]["very_light"] == 30
    assert result["zone_minutes"]["no_hr"] == 0


# PR 7 (beta 2): RPE-aware zone minutes, a stable taper reference, a race in the profile.
def _hrr_zones():
    profile = Profile(birth_date=date(1992, 1, 1), hr_rest=48, hr_max=191)
    shown = hr_zones(profile, flags(profile), 48, 191)
    return shown, runs.zones_to_describe(profile, flags(profile), 48, 191, TODAY)


def test_a_run_with_rpe_counts_in_its_rpe_zone_and_a_disagreement_is_flagged():
    shown, every = _hrr_zones()
    easy = Run(TODAY, 10.0, 60.0, avg_hr=150, rpe=12)  # HR says vigorous, RPE says moderate
    out = week([easy], TODAY, shown, every)
    assert out["zone_minutes"]["moderate"] == 60.0 and out["zone_minutes"]["vigorous"] == 0.0
    assert out["hr_rpe_disagree"] == [
        {"date": TODAY, "hr_zone": "vigorous", "rpe_zone": "moderate"}
    ]


def test_taper_reference_is_the_mean_of_the_four_weeks_before_it():
    race = date(2026, 5, 3)
    logged = [Run(race - timedelta(days=d), km, 60.0) for d, km in
              ((20, 40.0), (27, 30.0), (34, 30.0), (41, 20.0))]  # fmt: skip
    out = taper(race, race - timedelta(days=16), logged)
    assert out["reference_week_km"] == 30.0  # (40 + 30 + 30 + 20) / 4
    moved = taper(race + timedelta(days=7), race - timedelta(days=9), logged)
    assert moved["reference_week_km"] != 40.0  # never one week alone


def test_taper_reference_does_not_count_a_one_day_oldest_week_as_a_whole_week():
    # first run 7 days before the reference ends: 8 days of data are one week, not two
    logged = [Run(date(2026, 3, 21), 5.0, 30), Run(date(2026, 3, 24), 15.0, 90),
              Run(date(2026, 3, 27), 20.0, 120)]  # fmt: skip
    out = taper(date(2026, 4, 12), TODAY, logged)
    assert out["reference_week_km"] == 35.0
