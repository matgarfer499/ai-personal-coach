from datetime import date

import pytest

from coach.profile import Profile, ProfileIncomplete, load_profile, save_profile


def test_round_trip(tmp_path):
    path = tmp_path / "profile.yaml"
    profile = Profile(
        sex="female",
        birth_date=date(1990, 5, 17),
        height_cm=165.0,
        weight_kg=62.5,
        goal="fat_loss",
        experience="novice",
        activity_level="desk",
        language="es",
        region="es",
        medications=["beta_blocker"],
        conditions=["hypertension"],
        screening={"scoff_positive": False, "menstrual": "normal"},
    )
    save_profile(profile, path)
    assert load_profile(path) == profile
    assert load_profile(path).research_reminder_months == 6


def test_partial_profile_loads_and_require_names_the_missing_field(tmp_path):
    path = tmp_path / "profile.yaml"
    path.write_text("language: es\nweight_kg: 80\n")
    profile = load_profile(path)
    assert profile.weight_kg == 80
    with pytest.raises(ProfileIncomplete) as err:
        profile.require("sex")
    assert err.value.field == "sex"
    assert "sex" in str(err.value)


def test_missing_file_is_an_empty_profile(tmp_path):
    assert load_profile(tmp_path / "nope.yaml") == Profile()


def test_unknown_key_is_rejected(tmp_path):
    path = tmp_path / "profile.yaml"
    path.write_text("wieght_kg: 80\n")
    with pytest.raises(ValueError, match="wieght_kg"):
        load_profile(path)


@pytest.mark.parametrize(
    "field,value",
    [("sex", "other"), ("goal", "shred"), ("experience", "elite"), ("activity_level", "lazy")],
)
def test_invalid_enum_values_are_rejected(tmp_path, field, value):
    path = tmp_path / "profile.yaml"
    path.write_text(f"{field}: {value}\n")
    with pytest.raises(ValueError, match=field):
        load_profile(path)


def test_unknown_medication_is_kept_but_not_a_token():
    profile = Profile(medications=["metoprolol", "glp1"])
    assert profile.has_medication("glp1")
    assert not profile.has_medication("beta_blocker")
    assert "metoprolol" in profile.medications


def test_age_uses_given_day():
    profile = Profile(birth_date=date(1960, 3, 1))
    assert profile.age(date(2026, 2, 28)) == 65
    assert profile.age(date(2026, 3, 1)) == 66
    with pytest.raises(ProfileIncomplete, match="birth_date"):
        Profile().age(date(2026, 1, 1))


def test_bmi():
    assert Profile(height_cm=180, weight_kg=81).bmi() == pytest.approx(25.0)
    with pytest.raises(ProfileIncomplete, match="height_cm"):
        Profile(weight_kg=80).bmi()


@pytest.mark.parametrize(
    "text,message",
    [
        ("sex: [female\n", "not valid YAML"),
        ("height_cm: abc\n", "height_cm"),
        ('birth_date: "1990-01-01"\n', "birth_date"),
        ("research_reminder_months: true\n", "research_reminder_months"),
        ("screening:\n  bp_systolic: true\n", "bp_systolic"),
        ("medications: bisoprolol\n", "medications"),
    ],
)
def test_hand_edited_profile_errors_are_clear(tmp_path, text, message):
    path = tmp_path / "profile.yaml"
    path.write_text(text)
    with pytest.raises(ValueError, match=message):
        load_profile(path)


def test_injuries_round_trip(tmp_path):
    path = tmp_path / "profile.yaml"
    profile = Profile(
        injuries=[
            {
                "area": "right shoulder",
                "status": "active",
                "since": date(2026, 10, 1),
                "professional": "physiotherapist",
                "exercises": ["Bench Press (Barbell)", "Overhead Press"],
            },
            {"area": "left ankle", "status": "cleared", "cleared_on": date(2026, 9, 1)},
        ]
    )
    save_profile(profile, path)
    assert load_profile(path) == profile


@pytest.mark.parametrize(
    "injury,message",
    [
        ({"status": "active"}, "area"),
        ({"area": "knee", "status": "sore"}, "status"),
        ({"area": "knee", "status": "cleared"}, "cleared_on"),
        ({"area": "knee", "status": "active", "since": "last week"}, "since"),
        ({"area": "knee", "status": "active", "exercises": "Squat"}, "exercises"),
        ({"area": "knee", "status": "active", "pain": 3}, "pain"),
        ({"area": "  ", "status": "active"}, "area"),
        (
            {
                "area": "knee",
                "status": "cleared",
                "since": date(2026, 5, 1),
                "cleared_on": date(2026, 4, 1),
            },
            "cleared_on",
        ),
    ],
)
def test_invalid_injuries_are_rejected(tmp_path, injury, message):
    path = tmp_path / "profile.yaml"
    with pytest.raises(ValueError, match=message):
        save_profile(Profile(injuries=[injury]), path)


def test_vigorous_review_is_a_screening_outcome(tmp_path):
    path = tmp_path / "profile.yaml"
    save_profile(Profile(screening={"vigorous_reviewed": True}), path)
    assert load_profile(path).screening["vigorous_reviewed"] is True


@pytest.mark.parametrize(
    "text",
    ["injuries:\nmedications:\n", "injuries:\n- area: knee\n  status: active\n  exercises:\n"],
)
def test_empty_lists_in_a_hand_edited_profile_are_empty(tmp_path, text):
    path = tmp_path / "profile.yaml"
    path.write_text(text)
    profile = load_profile(path)
    assert profile.medications == []
    assert all(i.get("exercises", []) == [] for i in profile.injuries)
    assert profile.active_injuries() == profile.injuries


def test_language_is_one_the_coach_speaks(tmp_path):
    with pytest.raises(ValueError, match="language must be one of es, en"):
        save_profile(Profile(language="pt"), tmp_path / "profile.yaml")


@pytest.mark.parametrize("number", ["112", "911", "000", "999"])
def test_emergency_number_is_kept(tmp_path, number):
    save_profile(Profile(emergency_number=number), tmp_path / "profile.yaml")
    assert load_profile(tmp_path / "profile.yaml").emergency_number == number


@pytest.mark.parametrize("number", ["9-1-1", "call 112", "1", "1234567"])
def test_emergency_number_must_be_digits(tmp_path, number):
    with pytest.raises(ValueError, match="emergency_number"):
        save_profile(Profile(emergency_number=number), tmp_path / "profile.yaml")
