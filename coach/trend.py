"""Weight trend from weigh-ins, and TDEE recalibration from the trend.

Method (nutrition.md: "Read the scale with weekly averages"): compare weekly means, never single
weigh-ins. The rate is the change between the mean of the earliest week and the mean of the
latest week in the window, divided by the time between those weeks' mean dates. With one weigh-in
a week this is a same-weekday comparison.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import date, timedelta
from statistics import fmean

from coach.safety import SafetyFlags, weight_block_reason

# convention: at least 7 weigh-ins covering 14 days (chosen when the coach was designed), built on
# nutrition.md: "Read the scale with weekly averages" ("never adjust calories from one or two
# weigh-ins") and "Recalibrate TDEE from the weight trend" ("after 2 weeks, check only the
# direction").
MIN_POINTS = 7
MIN_DAYS = 14
# nutrition.md: "Recalibrate TDEE from the weight trend": compute observed TDEE after 4+ weeks.
RECALIBRATE_DAYS = 28
# nutrition.md: "Read the scale with weekly averages": compare weekly means across 2-4 weeks.
# convention: the window is the last 4 weeks, stretched back to include 7 weigh-ins for clients
# who weigh less often ("allow more weeks" with weekly weighing), but never beyond 8 weeks, so old
# weigh-ins cannot stand in for recent ones.
WINDOW_DAYS = 28
MAX_WINDOW_DAYS = 56
WEEK = 7
# nutrition.md: "Expected weight change: the 3500 kcal rule is wrong": 7700 kcal/kg is rough
# arithmetic, and the rule asks for an energy density "well below" it in early weeks and for lean
# clients, without giving a figure. convention (judgment call): keep 7700 as the default because
# a higher density is the cautious error both ways: when losing, it raises the observed TDEE (more
# food, a smaller deficit); when gaining, it lowers it (a smaller surplus, which the surplus rule
# warns tends to drift upward). Callers may pass a lower value.
ENERGY_DENSITY_KCAL_PER_KG = 7700


@dataclass
class Trend:
    status: str  # ok | insufficient_data | disabled
    rate_kg_week: float | None = None
    rate_pct_week: float | None = None
    weight_kg: float | None = None  # mean of the latest week
    points: int = 0
    days: int = 0  # calendar days covered by the window
    start: date | None = None  # first and last weigh-in in the window
    end: date | None = None
    can_recalibrate: bool = False
    notes: list[str] = field(default_factory=list)


def _daily_means(points: list[tuple[date, float]]) -> list[tuple[date, float]]:
    by_day: dict[date, list[float]] = defaultdict(list)
    for day, kg in points:
        by_day[day].append(kg)
    return sorted((day, fmean(values)) for day, values in by_day.items())


def _ordinal_mean(days: list[date]) -> float:
    return fmean(d.toordinal() for d in days)


def weight_trend(points: list[tuple[date, float]], flags: SafetyFlags | None = None) -> Trend:
    if flags is not None and flags.no_weight_targets:
        return Trend(
            status="disabled",
            notes=[weight_block_reason(flags)],
        )
    series = _daily_means(points)
    if not series:
        return Trend(status="insufficient_data", notes=["no weigh-ins"])
    last = series[-1][0]
    start = last - timedelta(WINDOW_DAYS - 1)
    if len(series) >= MIN_POINTS:
        start = max(min(start, series[-MIN_POINTS][0]), last - timedelta(MAX_WINDOW_DAYS - 1))
    window = [(d, kg) for d, kg in series if d >= start]
    days = (last - window[0][0]).days + 1
    if len(window) < MIN_POINTS or days < MIN_DAYS:
        return Trend(
            status="insufficient_data",
            points=len(window),
            days=days,
            start=window[0][0],
            end=last,
            notes=[f"need at least {MIN_POINTS} weigh-ins covering {MIN_DAYS} days"],
        )
    first_day = window[0][0]
    first_week = [(d, kg) for d, kg in window if d < first_day + timedelta(WEEK)]
    last_week = [(d, kg) for d, kg in window if d > last - timedelta(WEEK)]
    weeks_apart = (
        _ordinal_mean([d for d, _ in last_week]) - _ordinal_mean([d for d, _ in first_week])
    ) / WEEK
    current = fmean(kg for _, kg in last_week)
    rate = (current - fmean(kg for _, kg in first_week)) / weeks_apart
    return Trend(
        status="ok",
        rate_kg_week=rate,
        rate_pct_week=rate / current * 100,
        weight_kg=current,
        points=len(window),
        days=days,
        start=first_day,
        end=last,
        can_recalibrate=days >= RECALIBRATE_DAYS,
    )


def recalibrate_tdee(
    trend: Trend, intake_kcal: float, energy_density: float = ENERGY_DENSITY_KCAL_PER_KG
) -> float:
    """Observed TDEE = mean logged intake - (trend weight change x energy density / days).

    nutrition.md: "Recalibrate TDEE from the weight trend". `intake_kcal` is the mean logged
    intake over the same window, in "logged-calorie units".
    """
    if trend.status != "ok":
        raise ValueError(f"cannot recalibrate: trend status is {trend.status}")
    if not trend.can_recalibrate:
        raise ValueError(
            f"cannot recalibrate: {trend.days} days of weigh-ins, need 4 weeks "
            f"({RECALIBRATE_DAYS} days); before that, check only the direction"
        )
    return intake_kcal - trend.rate_kg_week * energy_density / WEEK
