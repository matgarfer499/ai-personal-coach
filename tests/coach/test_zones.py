from datetime import date
from itertools import pairwise

import pytest

from coach.profile import Profile, ProfileIncomplete
from coach.safety import flags
from coach.zones import hr_zones, tanaka

TODAY = date(2026, 1, 1)


def person(**kw):
    screening = {"parq_any_yes": False}
    return Profile(**({"birth_date": date(1986, 1, 1), "screening": screening} | kw))  # age 40


def zones(profile, **kw):
    return hr_zones(profile, flags(profile, TODAY), today=TODAY, **kw)


def band(result, name):
    return next(z for z in result.zones if z.name == name)


# cardio-health.md "HRmax: formulas and setting the anchor": Tanaka 208 - 0.7 x age
def test_tanaka():
    assert tanaka(40) == pytest.approx(180)


# cardio-health.md "ACSM intensity bands"
def test_hrmax_percent_zones_without_resting_hr():
    result = zones(person())
    assert result.method == "hrmax"
    assert result.hr_max == 180 and result.hr_max_source == "tanaka"
    moderate = band(result, "moderate")
    assert moderate.bpm == (round(0.64 * 180), round(0.76 * 180))
    assert moderate.rpe == (12, 13)
    assert band(result, "vigorous").rpe == (14, 17)
    assert band(result, "light").rpe == (9, 11)
    assert any("20+" in n for n in result.notes)


def test_karvonen_with_resting_hr_and_vigorous_cap_at_84():
    result = zones(person(), hr_rest=60)
    assert result.method == "hrr"
    moderate = band(result, "moderate")
    assert moderate.bpm == (round(60 + 0.40 * 120), round(60 + 0.59 * 120))
    vigorous = band(result, "vigorous")
    assert vigorous.bpm == (round(60 + 0.60 * 120), round(60 + 0.84 * 120))


def test_measured_hr_max_wins():
    result = zones(person(), hr_max=192)
    assert result.hr_max == 192 and result.hr_max_source == "measured"


def test_invalid_heart_rates():
    with pytest.raises(ValueError):
        zones(person(), hr_rest=200)
    with pytest.raises(ValueError):
        zones(person(), hr_rest=60, hr_max=55)


def test_needs_age_for_tanaka_only():
    with pytest.raises(ProfileIncomplete, match="birth_date"):
        zones(Profile())
    assert zones(Profile(), hr_max=185).hr_max == 185


# cardio-health.md "Beta-blockers: no formula-based HR zones" and "RPE as the anchor under
# beta-blockade": RPE only, moderate 12-13, no sustained vigorous work without clearance.
def test_beta_blocker_gets_rpe_only_and_no_vigorous_zone():
    result = zones(person(medications=["beta_blocker"]), hr_rest=60, hr_max=180)
    assert result.method == "rpe"
    assert result.hr_max is None
    assert all(z.bpm is None for z in result.zones)
    assert [z.name for z in result.zones] == ["light", "moderate"]
    assert band(result, "moderate").rpe == (12, 13)
    assert any("Beta-blockers" in r for r in result.notes)


# recovery-habits.md "Gauge intensity by talk test and RPE, not a heart-rate cap" (moderate
# RPE 13-14) and "Vigorous work: avoid near-maximal efforts" (never RPE 18 or more)
def test_pregnancy_uses_its_own_rpe_band():
    result = zones(person(sex="female", conditions=["pregnant"]), hr_rest=60)
    assert result.method == "rpe"
    assert band(result, "moderate").rpe == (13, 14)
    assert max(z.rpe[1] for z in result.zones) < 18


def test_pregnancy_bands_leave_no_gap():
    result = zones(person(sex="female", conditions=["pregnant"]))
    bands = [z.rpe for z in result.zones]
    assert all(low == prev_high + 1 for (_, prev_high), (low, _) in pairwise(bands))


def test_pregnancy_plus_beta_blocker_keeps_the_beta_blocker_ceiling():
    profile = person(sex="female", conditions=["pregnant"], medications=["beta_blocker"])
    result = zones(profile)
    assert [z.name for z in result.zones] == ["light", "moderate"]
    assert band(result, "moderate").rpe == (13, 13)
    assert max(z.rpe[1] for z in result.zones) <= 13
    assert any("RPE 14 or more" in n for n in result.notes)


def test_heart_disease_defers_to_cardiac_team():
    result = zones(person(conditions=["heart_disease"]), hr_rest=60)
    assert result.method == "cardiac_team"
    assert result.zones == []
    assert any("cardiac team" in n for n in result.notes)


def test_talk_test_on_every_zone():
    for zone in zones(person()).zones:
        assert zone.talk_test


def test_bp_cap_removes_the_vigorous_zone():
    profile = person(screening={"bp_systolic": 165, "bp_diastolic": 85})
    result = zones(profile, hr_rest=60)
    assert [z.name for z in result.zones] == ["light", "moderate"]
    assert any("Resting BP" in n for n in result.notes)


def test_bp_no_training_returns_no_zones():
    result = zones(person(screening={"bp_systolic": 185, "bp_diastolic": 85}), hr_rest=60)
    assert result.method == "no_training" and result.zones == []


def test_cardiac_symptoms_say_why_there_are_no_zones():
    result = zones(person(screening={"cardiac_symptoms": True}), hr_rest=60)
    assert result.method == "no_training" and result.zones == []
    assert any("Cardiac warning symptoms" in n for n in result.notes)


# recovery-habits.md "PAR-Q+ specific thresholds": a review before vigorous work, so no
# vigorous zone until it has happened.
def test_vigorous_zone_waits_for_the_review_after_a_parq_yes():
    result = zones(person(screening={"parq_any_yes": True}), hr_rest=60)
    assert [z.name for z in result.zones] == ["light", "moderate"]
    assert any("PAR-Q+ specific thresholds" in n for n in result.notes)
    reviewed = person(screening={"parq_any_yes": True, "vigorous_reviewed": True})
    assert band(zones(reviewed, hr_rest=60), "vigorous")


def test_over_45_gets_no_vigorous_zone_until_reviewed():
    result = zones(person(birth_date=date(1975, 1, 1)), hr_rest=60)
    assert [z.name for z in result.zones] == ["light", "moderate"]
    reviewed = {"parq_any_yes": False, "vigorous_reviewed": True}
    assert band(zones(person(birth_date=date(1975, 1, 1), screening=reviewed)), "vigorous")


def test_parq_note_shows_even_when_rpe_zones_have_no_vigorous_band():
    screening = {"parq_any_yes": True}
    result = zones(person(medications=["beta_blocker"], screening=screening))
    assert any("PAR-Q+ specific thresholds" in n for n in result.notes)
