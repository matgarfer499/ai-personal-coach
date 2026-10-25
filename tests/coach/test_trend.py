from datetime import date, timedelta

import pytest

from coach.profile import Profile
from coach.safety import flags
from coach.trend import ENERGY_DENSITY_KCAL_PER_KG, recalibrate_tdee, weight_trend

START = date(2026, 3, 2)  # a Monday


def daily(days, start_kg=80.0, kg_per_day=-0.05, start=START):
    return [(start + timedelta(d), start_kg + kg_per_day * d) for d in range(days)]


def test_steady_daily_loss():
    trend = weight_trend(daily(28))
    assert trend.status == "ok"
    # First-week mean at day 3, last-week mean at day 24: 21 days apart, -0.05 kg/day.
    assert trend.rate_kg_week == pytest.approx(-0.35)
    assert trend.rate_pct_week == pytest.approx(-0.35 / trend.weight_kg * 100)
    assert trend.weight_kg == pytest.approx(80 - 0.05 * 24)
    assert trend.points == 28
    assert trend.can_recalibrate


def test_only_last_four_weeks_count_for_daily_weighers():
    points = daily(28, start=START - timedelta(28), kg_per_day=0.1) + daily(28)
    trend = weight_trend(points)
    assert trend.rate_kg_week == pytest.approx(-0.35)
    assert trend.points == 28


def test_fewer_than_seven_weigh_ins_is_insufficient():
    points = [(START + timedelta(d), 80.0) for d in (0, 3, 6, 9, 12, 14)]
    trend = weight_trend(points)
    assert trend.status == "insufficient_data"
    assert trend.rate_kg_week is None and trend.rate_pct_week is None


def test_less_than_fourteen_days_is_insufficient():
    trend = weight_trend(daily(13))
    assert trend.status == "insufficient_data"


def test_gaps_still_work_with_seven_points_over_fourteen_days():
    points = [(START + timedelta(d), 80.0 - 0.01 * d) for d in (0, 1, 2, 8, 12, 13, 14)]
    trend = weight_trend(points)
    assert trend.status == "ok"
    assert trend.rate_kg_week < 0
    assert not trend.can_recalibrate


def test_weekly_weigher_needs_seven_weeks_of_points():
    weekly = [(START + timedelta(7 * w), 80.0 - 0.3 * w) for w in range(6)]
    assert weight_trend(weekly).status == "insufficient_data"
    weekly.append((START + timedelta(42), 80.0 - 0.3 * 6))
    trend = weight_trend(weekly)
    assert trend.status == "ok"
    assert trend.rate_kg_week == pytest.approx(-0.3)


def test_same_day_readings_are_averaged():
    flat = [(START + timedelta(d), 80.0) for d in range(14)]
    # A second reading of 81.0 on every day of the last week: daily means become 80.5.
    extra = [(START + timedelta(d), 81.0) for d in range(7, 14)]
    trend = weight_trend(flat + extra)
    assert trend.points == 14
    assert trend.weight_kg == pytest.approx(80.5)


def test_old_weigh_ins_cannot_stretch_the_window_beyond_eight_weeks():
    old = [(START + timedelta(d), 85.0) for d in range(6)]
    trend = weight_trend(old + [(START + timedelta(365), 80.0)])
    assert trend.status == "insufficient_data"
    assert trend.points == 1


def test_unsorted_input():
    points = daily(28)
    assert weight_trend(list(reversed(points))) == weight_trend(points)


def test_positive_screen_disables_the_trend():
    profile = Profile(screening={"scoff_positive": True})
    trend = weight_trend(daily(28), flags(profile))
    assert trend.status == "disabled"
    assert trend.rate_kg_week is None
    assert trend.notes and "Eating-disorder" in trend.notes[0]


# nutrition.md "Recalibrate TDEE from the weight trend": observed TDEE = mean intake -
# (trend weight change x energy density / days)
def test_recalibrate_tdee():
    trend = weight_trend(daily(28))
    assert recalibrate_tdee(trend, 2000) == pytest.approx(
        2000 + 0.35 * ENERGY_DENSITY_KCAL_PER_KG / 7
    )
    assert recalibrate_tdee(trend, 2000, energy_density=5000) == pytest.approx(2250)


def test_recalibrate_needs_four_weeks():
    with pytest.raises(ValueError, match="4 weeks"):
        recalibrate_tdee(weight_trend(daily(20)), 2000)
    with pytest.raises(ValueError, match="insufficient_data"):
        recalibrate_tdee(weight_trend(daily(5)), 2000)
