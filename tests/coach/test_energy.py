from datetime import date

import pytest

from coach import energy
from coach.energy import calorie_target, rmr_mifflin, tdee
from coach.profile import Profile, ProfileIncomplete
from coach.safety import flags

TODAY = date(2026, 1, 1)
OK = {"scoff_positive": False}


def man(**kw):
    base = dict(
        sex="male",
        birth_date=date(1996, 1, 1),
        height_cm=180,
        weight_kg=80,
        activity_level="desk",
        goal="fat_loss",
        screening=OK,
    )
    return Profile(**(base | kw))


def woman(**kw):
    base = dict(
        sex="female",
        birth_date=date(1996, 1, 1),
        height_cm=165,
        weight_kg=60,
        activity_level="desk",
        goal="fat_loss",
        screening=OK,
    )
    return Profile(**(base | kw))


def target(profile, **kw):
    return calorie_target(profile, flags(profile), today=TODAY, **kw)


# nutrition.md "Default RMR equation: Mifflin-St Jeor": 10 kg + 6.25 cm - 5 age (+5 / -161)
def test_rmr_mifflin_men_and_women():
    assert rmr_mifflin(man(), today=TODAY) == pytest.approx(800 + 1125 - 150 + 5)
    assert rmr_mifflin(woman(), today=TODAY) == pytest.approx(600 + 1031.25 - 150 - 161)


@pytest.mark.parametrize("missing", ["sex", "birth_date", "height_cm", "weight_kg"])
def test_rmr_names_missing_field(missing):
    with pytest.raises(ProfileIncomplete) as err:
        rmr_mifflin(man(**{missing: None}), today=TODAY)
    assert err.value.field == missing


# nutrition.md "Activity multipliers (PAL)": desk 1.4-1.5, desk + training 1.6-1.75, active 1.7-1.9
@pytest.mark.parametrize("level,pal", [("desk", 1.45), ("desk_training", 1.675), ("active", 1.8)])
def test_tdee_uses_band_midpoint(level, pal):
    assert tdee(man(activity_level=level), today=TODAY) == pytest.approx(1780 * pal)


def test_tdee_explicit_multiplier_and_limits():
    assert tdee(man(), multiplier=1.5, today=TODAY) == pytest.approx(1780 * 1.5)
    with pytest.raises(ValueError, match="1.2"):
        tdee(man(), multiplier=1.2, today=TODAY)
    with pytest.raises(ValueError, match="2.0"):
        tdee(man(), multiplier=2.2, today=TODAY)


def test_tdee_needs_activity_level():
    with pytest.raises(ProfileIncomplete, match="activity_level"):
        tdee(man(activity_level=None), today=TODAY)


# nutrition.md "Deficit size for weight loss" (500-750) and "Deficit size when keeping or
# building muscle" (at most 500): the coach uses 500.
def test_fat_loss_deficit_is_500():
    result = target(man())
    assert result.maintenance == pytest.approx(1780 * 1.45)
    assert result.deficit == 500
    assert result.kcal == round(1780 * 1.45 - 500)
    assert not result.clamped


# nutrition.md "Low- and very-low-calorie diets need clinical supervision": 1,200 / 1,500 floors
def test_floor_clamps_and_flags_women():
    result = target(woman(), tdee_kcal=1400)
    assert result.kcal == 1200 and result.clamped
    assert any("Low- and very-low-calorie diets" in n for n in result.notes)


def test_floor_clamps_men():
    result = target(man(), tdee_kcal=1900)
    assert result.kcal == 1500 and result.clamped
    assert result.deficit == 400


def test_maintenance_below_floor_is_clamped_up():
    result = target(woman(goal="maintenance"), tdee_kcal=1150)
    assert result.kcal == 1200 and result.clamped and result.deficit == -50


def test_unscreened_fat_loss_raises():
    with pytest.raises(ProfileIncomplete) as err:
        target(man(screening={}))
    assert err.value.field == "screening.scoff_yes_count"


def test_unscreened_maintenance_is_fine():
    assert target(man(goal="maintenance", screening={})).deficit == 0


@pytest.mark.parametrize(
    "changes",
    [
        {"screening": {"scoff_positive": True}},
        {"medications": ["glp1"]},
        {"conditions": ["pregnant"]},
        {"screening": OK | {"menstrual": "absent"}},
    ],
)
def test_no_deficit_overrides(changes):
    profile = woman(**changes)
    result = target(profile)
    assert result.deficit == 0
    assert result.kcal == round(result.maintenance)
    assert flags(profile).reasons
    assert all(reason in result.notes for reason in flags(profile).reasons)


def test_prescriber_owned_weight_gets_no_surplus_either():
    result = target(woman(goal="muscle_gain", medications=["glp1"]))
    assert result.deficit == 0


# nutrition.md "Menstrual dysfunction: stop and refer": new irregular periods, stop increasing
# the deficit
def test_hold_deficit_never_starts_or_deepens_a_deficit():
    profile = woman(screening=OK | {"menstrual": "irregular_new"})
    result = target(profile)
    assert result.deficit == 0
    assert any("stop increasing the deficit" in n for n in result.notes)
    maintenance = round(result.maintenance)
    held = target(profile, current_kcal=maintenance - 300)
    assert held.deficit == 300
    assert target(profile, current_kcal=maintenance + 200).deficit == 0


# nutrition.md "Resistance training during any diet, especially for older adults"
def test_older_adult_gets_no_deficit_without_obesity_and_condition():
    old = man(birth_date=date(1956, 1, 1))  # 70
    assert target(old).deficit == 0
    obese = man(birth_date=date(1956, 1, 1), weight_kg=100)  # BMI 30.9
    assert target(obese).deficit == 0
    allowed = man(
        birth_date=date(1956, 1, 1), weight_kg=100, conditions=["weight_related_condition"]
    )
    assert target(allowed).deficit == 500


# nutrition.md "Surplus size for muscle gain": 5-20% above maintenance, start at the lower end
def test_muscle_gain_surplus_starts_at_5_percent():
    result = target(man(goal="muscle_gain"))
    assert result.kcal == round(1780 * 1.45 * 1.05)
    assert result.deficit == -round(1780 * 1.45 * 0.05)


@pytest.mark.parametrize("goal", ["maintenance", "recomposition"])
def test_maintenance_and_recomposition_eat_at_maintenance(goal):
    assert target(man(goal=goal)).deficit == 0


def test_glp1_low_intake_note_uses_its_own_threshold():
    # nutrition.md "GLP-1 users": micronutrient flag below 1,800 kcal for men.
    result = target(man(medications=["glp1"]), tdee_kcal=1700)
    assert any("1,800" in n for n in result.notes)
    assert not result.clamped


def test_positive_screen_gets_no_surplus_and_the_referral_note():
    profile = man(goal="muscle_gain", screening={"scoff_positive": True})
    result = target(profile)
    assert result.deficit == 0
    assert any("Eating-disorder screening" in n for n in result.notes)


def test_unknown_goal_is_rejected():
    with pytest.raises(ValueError, match="goal"):
        target(man(), goal="fatloss")


def test_goal_argument_overrides_profile():
    assert target(man(goal="maintenance"), goal="fat_loss").deficit == 500
    with pytest.raises(ProfileIncomplete, match="goal"):
        target(man(goal=None))


def test_constants_named_after_rules():
    assert energy.FLOOR_KCAL == {"female": 1200, "male": 1500}
    assert energy.GLP1_LOW_INTAKE_KCAL == {"female": 1200, "male": 1800}


def test_recalibrated_target_cuts_at_most_one_step_from_current_intake():
    t = target(man(), tdee_kcal=2600, current_kcal=2500, recalibrated=True)
    assert t.kcal == 2500 - energy.RECALIBRATE_STEP_KCAL
    assert any("step" in n for n in t.notes)
    assert not any("starting estimate" in n for n in t.notes)


def test_recalibrated_target_within_one_step_or_upward_applies_at_once():
    assert target(man(), tdee_kcal=2600, current_kcal=2200, recalibrated=True).kcal == 2100
    assert target(man(), tdee_kcal=2600, current_kcal=1800, recalibrated=True).kcal == 2100


def test_recalibrated_step_never_goes_below_the_floor():
    t = target(woman(), tdee_kcal=1500, current_kcal=1300, recalibrated=True)
    assert t.kcal == energy.FLOOR_KCAL["female"] and t.clamped


def test_no_weigh_in_talk_after_a_positive_screen():
    t = target(woman(screening={"scoff_positive": True}))
    assert not any("weigh-in" in n and "recalibrate" in n for n in t.notes)


def test_step_note_never_shows_a_target_below_the_floor():
    t = target(woman(), tdee_kcal=1500, current_kcal=1800, recalibrated=True)
    assert t.kcal == 1600
    assert not any("1000" in n for n in t.notes)
    assert any("1,200" in n or "1200" in n for n in t.notes)


def test_under_18s_get_no_calorie_target():
    minor = woman(birth_date=date(2011, 6, 1))
    with pytest.raises(ValueError, match="Under-18s"):
        calorie_target(minor, flags(minor, today=TODAY), today=TODAY)
