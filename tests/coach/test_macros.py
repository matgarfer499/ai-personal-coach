from datetime import date

import pytest

from coach.macros import macro_targets
from coach.profile import Profile, ProfileIncomplete

TODAY = date(2026, 1, 1)


def lifter(**kw):
    base = dict(
        sex="male",
        birth_date=date(1996, 1, 1),
        height_cm=180,
        weight_kg=80,
        screening={"scoff_positive": False},
    )
    return Profile(**(base | kw))


def macros(profile, kcal, **kw):
    return macro_targets(profile, kcal, today=TODAY, **kw)


# nutrition.md "Daily protein target for people who lift": default 1.6 g/kg
def test_maintenance_protein_is_1_6():
    result = macros(lifter(), 2600)
    assert result.protein_g == pytest.approx(128)
    assert result.protein_g_per_kg == pytest.approx(1.6)


# nutrition.md "Protein during fat loss": 1.8-2.2 g/kg
def test_deficit_protein_midpoint_2_0():
    assert macros(lifter(), 2081, in_deficit=True).protein_g == pytest.approx(160)


# nutrition.md "Older adults: protein targets": 1.2-1.6 g/kg when lifting
def test_older_adult_protein():
    old = lifter(birth_date=date(1956, 1, 1))
    assert macros(old, 2200).protein_g_per_kg == pytest.approx(1.4)
    assert macros(old, 2000, in_deficit=True).protein_g_per_kg == pytest.approx(1.4)


# nutrition.md "GLP-1 users: protein, training and red flags": 1.2-1.6 g/kg
def test_glp1_protein():
    assert macros(lifter(medications=["glp1"]), 2000).protein_g_per_kg == pytest.approx(1.4)


def test_obesity_uses_reference_weight():
    # BMI 38: protein from the weight at BMI 25 for this height (convention).
    big = lifter(height_cm=170, weight_kg=110)
    result = macros(big, 2400, in_deficit=True)
    assert result.protein_g == pytest.approx(2.0 * 25 * 1.7**2)
    assert any("convention" in n for n in result.notes)


# nutrition.md "Minimum dietary fat" (>= 20% energy, >= 0.5 g/kg) and "EU label rules and
# tolerances" (4/4/9 kcal per g)
def test_fat_carbs_fibre():
    result = macros(lifter(), 2081, in_deficit=True)
    assert result.fat_g == pytest.approx(2081 * 0.25 / 9)
    assert result.carbs_g == pytest.approx((2081 - 160 * 4 - 2081 * 0.25) / 4)
    assert result.fibre_g == 25
    energy_from_macros = result.protein_g * 4 + result.fat_g * 9 + result.carbs_g * 4
    assert energy_from_macros == pytest.approx(2081)


def test_fat_never_below_half_gram_per_kg():
    heavy = lifter(weight_kg=100, height_cm=200)  # BMI 25: no reference weight
    result = macros(heavy, 1500, in_deficit=True)
    assert result.fat_g == pytest.approx(50)


def test_carbs_never_negative():
    result = macros(lifter(sex="female", weight_kg=110, height_cm=210), 1200, in_deficit=True)
    assert result.carbs_g == 0
    assert any("protein and fat" in n for n in result.notes)


@pytest.mark.parametrize("missing", ["weight_kg", "sex", "birth_date", "height_cm"])
def test_partial_profile_names_the_missing_field(missing):
    with pytest.raises(ProfileIncomplete) as err:
        macros(lifter(**{missing: None}), 2000)
    assert err.value.field == missing


# nutrition.md "Low- and very-low-calorie diets need clinical supervision"
def test_kcal_below_floor_is_raised():
    result = macros(lifter(), 900)
    assert result.kcal == 1500
    assert any("Low- and very-low-calorie diets" in n for n in result.notes)


def test_deficit_protein_refused_after_positive_screen():
    flagged = lifter(sex="female", screening={"scoff_positive": True})
    result = macros(flagged, 1800, in_deficit=True)
    assert result.protein_g_per_kg == pytest.approx(1.6)
    assert any("Eating-disorder screening" in n for n in result.notes)


# nutrition.md "Minimum dietary fat": at least about 20% of energy and 0.5 g/kg.
def test_fat_minimum():
    assert macros(lifter(), 2700).fat_min_g == pytest.approx(2700 * 0.20 / 9)
    heavy = lifter(weight_kg=100, height_cm=200)
    assert macros(heavy, 1500, in_deficit=True).fat_min_g == pytest.approx(50)


# Beta p5-elena-I4: no cliff at BMI 30; from BMI 25 protein uses the weight at BMI 25.
def test_protein_is_continuous_across_bmi_30():
    woman = dict(sex="female", height_cm=168, experience="intermediate")
    at_84 = macros(lifter(weight_kg=84, **woman), 1700, in_deficit=True).protein_g
    at_85 = macros(lifter(weight_kg=85, **woman), 1700, in_deficit=True).protein_g
    assert abs(at_84 - at_85) < 1


def test_overweight_uses_the_reference_weight():
    result = macros(lifter(weight_kg=90), 2400, in_deficit=True)  # BMI 27.8
    assert result.protein_g == pytest.approx(2.0 * 25 * 1.8**2)


# Beta p5-elena-I5: an overweight novice in a deficit gets the beginner band (1.6-2.0).
def test_overweight_novice_in_a_deficit_gets_the_beginner_band():
    novice = lifter(sex="female", height_cm=168, weight_kg=78, experience="novice")
    result = macros(novice, 1700, in_deficit=True)
    assert result.protein_g_per_kg == pytest.approx(1.8)
    assert result.protein_g == pytest.approx(1.8 * 25 * 1.68**2)


# Beta p5-elena-I6: the output says the dose per kg of body weight too.
def test_protein_per_kg_of_body_weight_is_reported():
    big = lifter(height_cm=170, weight_kg=110)
    result = macros(big, 2400, in_deficit=True)
    assert result.protein_g_per_kg_body == pytest.approx(result.protein_g / 110)
    assert any(
        f"{result.protein_g_per_kg_body:.2f} g per kg of body weight" in n for n in result.notes
    )


# Beta p4-sara-I1: the rule's range is exposed; menus pass from its low end.
def test_protein_range_follows_the_rule():
    result = macros(lifter(), 2081, in_deficit=True)
    assert result.protein_min_g == pytest.approx(1.6 * 80)  # "Protein during fat loss": 1.6-2.2
    assert result.protein_max_g == pytest.approx(2.2 * 80)
    maintenance = macros(lifter(), 2600)
    assert maintenance.protein_min_g == pytest.approx(1.4 * 80)  # "...people who lift": 1.4-2.2
