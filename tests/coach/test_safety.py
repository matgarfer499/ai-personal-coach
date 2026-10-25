import re
from datetime import date

import pytest

from coach import knowledge
from coach.profile import Profile
from coach.safety import SafetyFlags, flags

SCREENED_OK = {"scoff_positive": False, "parq_any_yes": False}


def _rules(result: SafetyFlags) -> set[str]:
    return {re.match(r'(\S+\.md): "([^"]+)"', r).group(0) for r in result.reasons}


def test_clean_screen_raises_no_flags():
    result = flags(Profile(sex="male", screening=SCREENED_OK))
    assert result.screened
    assert not any(
        [
            result.no_deficit,
            result.no_weight_targets,
            result.use_rpe_not_hr,
            result.prescriber_owns_weight,
            result.refer_gp,
            result.hold_deficit,
        ]
    )
    assert result.reasons == []


def test_unanswered_screen_is_reported():
    assert not flags(Profile()).screened


def test_positive_scoff_blocks_deficit_and_weight_targets_and_refers():
    result = flags(Profile(screening={"scoff_positive": True}))
    assert result.no_deficit and result.no_weight_targets and result.refer_gp
    assert 'nutrition.md: "Eating-disorder screening: brief questions as a prompt"' in _rules(
        result
    )


@pytest.mark.parametrize("count", [0, 1])
def test_fewer_than_two_scoff_yes_answers_is_a_clean_screen(count):
    result = flags(Profile(screening={"scoff_yes_count": count, "parq_any_yes": False}))
    assert result.screened
    assert not (result.no_deficit or result.no_weight_targets or result.refer_gp)
    assert result.reasons == []


@pytest.mark.parametrize("count", [2, 5])
def test_two_or_more_scoff_yes_answers_is_a_positive_screen(count):
    result = flags(Profile(screening={"scoff_yes_count": count, "parq_any_yes": False}))
    assert result.no_deficit and result.no_weight_targets and result.refer_gp
    assert 'nutrition.md: "Eating-disorder screening: brief questions as a prompt"' in _rules(
        result
    )


def test_a_warning_sign_is_positive_whatever_the_count():
    result = flags(Profile(screening={"scoff_yes_count": 1, "scoff_positive": True}))
    assert result.no_deficit and result.no_weight_targets and result.refer_gp


def test_glp1_hands_weight_plan_to_prescriber():
    result = flags(Profile(medications=["glp1"], screening=SCREENED_OK))
    assert result.no_deficit and result.prescriber_owns_weight
    assert not result.refer_gp
    assert 'nutrition.md: "GLP-1 users: protein, training and red flags"' in _rules(result)


def test_glp1_planning_pregnancy_refers_back_to_prescriber():
    result = flags(
        Profile(medications=["glp1"], conditions=["planning_pregnancy"], screening=SCREENED_OK)
    )
    assert result.refer_gp
    assert any("prescriber" in r for r in result.reasons)


def test_beta_blocker_switches_to_rpe():
    result = flags(Profile(medications=["beta_blocker"], screening=SCREENED_OK))
    assert result.use_rpe_not_hr
    assert not result.no_deficit
    assert 'cardio-health.md: "Beta-blockers: no formula-based HR zones"' in _rules(result)


def test_pregnancy_overrides():
    result = flags(Profile(sex="female", conditions=["pregnant"], screening=SCREENED_OK))
    assert result.no_deficit and result.no_weight_targets and result.prescriber_owns_weight
    assert result.use_rpe_not_hr and result.refer_gp
    rules = _rules(result)
    assert 'nutrition.md: "Pregnancy"' in rules
    assert (
        'recovery-habits.md: "Gauge intensity by talk test and RPE, not a heart-rate cap"' in rules
    )


def test_new_irregular_cycle_holds_deficit_and_refers():
    result = flags(Profile(sex="female", screening=SCREENED_OK | {"menstrual": "irregular_new"}))
    assert result.hold_deficit and result.refer_gp
    assert not result.no_deficit


def test_absent_periods_stop_the_deficit():
    result = flags(Profile(sex="female", screening=SCREENED_OK | {"menstrual": "absent"}))
    assert result.no_deficit and result.refer_gp
    assert 'nutrition.md: "Menstrual dysfunction: stop and refer"' in _rules(result)


@pytest.mark.parametrize(
    "answer,rule",
    [
        ("parq_followup_yes", 'recovery-habits.md: "PAR-Q+ 2023 as the default entry screen"'),
        ("cardiac_symptoms", 'recovery-habits.md: "Cardiac warning symptoms: stop and refer"'),
    ],
)
def test_screen_answers_that_refer(answer, rule):
    result = flags(Profile(screening=SCREENED_OK | {answer: True}))
    assert result.refer_gp
    assert rule in _rules(result)


def test_parq_any_yes_alone_does_not_refer():
    # PAR-Q+: any YES leads to follow-up questions; only a follow-up YES refers.
    assert not flags(Profile(screening=SCREENED_OK | {"parq_any_yes": True})).refer_gp


def test_every_reason_names_a_real_knowledge_rule():
    profile = Profile(
        sex="female",
        medications=["glp1", "beta_blocker"],
        conditions=["pregnant", "planning_pregnancy"],
        screening={
            "scoff_positive": True,
            "menstrual": "absent",
            "parq_followup_yes": True,
            "cardiac_symptoms": True,
        },
    )
    rules = _rules(flags(profile))
    assert len(rules) >= 7
    for rule in rules:
        file, heading = re.match(r'(\S+\.md): "([^"]+)"', rule).groups()
        knowledge.section(file, heading)  # raises SectionNotFound if the rule was renamed


# recovery-habits.md "Resting BP thresholds to defer or refer"
@pytest.mark.parametrize(
    "systolic,diastolic,no_training,cap_moderate,refer",
    [
        (125, 80, False, False, False),
        (145, 85, False, True, True),  # 140-159 with diastolic below 90: moderate, GP check
        (150, 95, False, True, True),  # diastolic 90-109: GP review, light-to-moderate only
        (170, 85, False, True, True),  # 160-179
        (185, 85, True, False, True),  # 180-199: no training until a GP review
        (205, 85, True, False, True),  # 200 or more: no exercise
        (130, 112, True, False, True),  # diastolic 110 or more
    ],
)
def test_resting_bp_bands(systolic, diastolic, no_training, cap_moderate, refer):
    profile = Profile(screening=SCREENED_OK | {"bp_systolic": systolic, "bp_diastolic": diastolic})
    result = flags(profile)
    assert (result.no_training, result.cap_moderate, result.refer_gp) == (
        no_training,
        cap_moderate,
        refer,
    )
    if refer:
        assert 'recovery-habits.md: "Resting BP thresholds to defer or refer"' in _rules(result)


def test_hypertension_with_unknown_bp_caps_intensity_and_refers():
    result = flags(Profile(conditions=["hypertension"], screening=SCREENED_OK))
    assert result.cap_moderate and result.refer_gp and not result.no_training
    assert any("BP unknown" in r for r in result.reasons)


def test_no_bp_and_no_hypertension_is_fine():
    assert not flags(Profile(screening=SCREENED_OK)).cap_moderate


def test_cardiac_symptoms_stop_training_until_cleared():
    result = flags(Profile(screening=SCREENED_OK | {"cardiac_symptoms": True}))
    assert result.no_training and result.hold_progression and result.refer_gp


@pytest.mark.parametrize(
    "screening,hold",
    [
        ({"parq_followup_yes": True}, True),  # "PAR-Q+ 2023": pause any progression of intensity
        ({"parq_any_yes": True}, False),
        ({"bp_systolic": 145, "bp_diastolic": 85}, False),  # 140-159: moderate, GP check only
        ({"bp_systolic": 150, "bp_diastolic": 95}, True),  # GP review before progressing
        ({"bp_systolic": 170, "bp_diastolic": 85}, True),
        ({"bp_systolic": 185, "bp_diastolic": 85}, True),  # no training at all
        ({}, False),
    ],
)
def test_hold_progression(screening, hold):
    assert flags(Profile(screening=SCREENED_OK | screening)).hold_progression is hold


def test_hypertension_with_unknown_bp_holds_progression():
    assert flags(Profile(conditions=["hypertension"], screening=SCREENED_OK)).hold_progression


def test_bp_reason_with_one_number_does_not_print_zero():
    result = flags(Profile(screening=SCREENED_OK | {"bp_diastolic": 95}))
    assert not any("0/95" in r for r in result.reasons)


# nutrition.md "Under-18s" and recovery-habits.md "Adolescents: no deficits": out of scope, no
# calorie targets, deficits or weigh-ins; refer to a paediatric professional.
def test_under_18s_get_no_calorie_targets_and_a_referral():
    minor = Profile(birth_date=date(2011, 6, 1), screening=SCREENED_OK)
    result = flags(minor, today=date(2026, 10, 24))
    assert result.no_calorie_targets and result.no_deficit and result.no_weight_targets
    assert result.refer_gp
    assert any('"Under-18s"' in r for r in result.reasons)
    adult = flags(minor, today=date(2029, 6, 1))  # 18th birthday
    assert not adult.no_calorie_targets


# recovery-habits.md "PAR-Q+ specific thresholds": anyone over 45, or with any PAR-Q+ YES, gets a
# qualified exercise professional or clinician review before vigorous or maximal work; all-out
# sprint formats need every PAR-Q+ answer NO.
PARQ_THRESHOLDS = 'recovery-habits.md: "PAR-Q+ specific thresholds"'


def test_any_parq_yes_needs_a_review_before_vigorous_work_and_rules_out_all_out_sprints():
    result = flags(Profile(screening=SCREENED_OK | {"parq_any_yes": True}))
    assert result.review_before_vigorous and result.no_all_out_sprints
    assert PARQ_THRESHOLDS in _rules(result)
    assert not result.refer_gp  # the review is for vigorous work only, not the whole plan


@pytest.mark.parametrize(
    "born,flagged",
    [(date(1982, 1, 1), False), (date(1981, 1, 1), True)],  # aged 44, 45
)
def test_over_45_needs_a_review_before_vigorous_work(born, flagged):
    result = flags(Profile(birth_date=born, screening=SCREENED_OK), today=date(2026, 1, 1))
    assert result.review_before_vigorous is flagged
    assert not result.no_all_out_sprints  # sprints are ruled out by a PAR-Q+ YES, not by age


def test_a_done_review_clears_vigorous_work_but_not_all_out_sprints():
    screening = SCREENED_OK | {"parq_any_yes": True, "vigorous_reviewed": True}
    result = flags(Profile(birth_date=date(1960, 1, 1), screening=screening))
    assert not result.review_before_vigorous
    assert result.no_all_out_sprints


def test_a_followup_yes_alone_counts_as_a_parq_yes():
    # Follow-up questions are reached only through a YES on the first seven.
    result = flags(Profile(screening={"scoff_positive": False, "parq_followup_yes": True}))
    assert result.review_before_vigorous and result.no_all_out_sprints


def test_an_unanswered_parq_rules_out_vigorous_work_and_sprints():
    # "PAR-Q+ specific thresholds": sprints need every answer NO; an unscreened client starts
    # with moderate work ("Choosing HIIT vs MICT vs SIT").
    result = flags(Profile(screening={"scoff_positive": False}))
    assert result.review_before_vigorous and result.no_all_out_sprints
    assert any("PAR-Q+ not answered" in r for r in result.reasons)


def test_all_parq_no_under_45_needs_no_vigorous_review():
    result = flags(
        Profile(birth_date=date(1990, 1, 1), screening=SCREENED_OK | {"parq_any_yes": False}),
        today=date(2026, 1, 1),
    )
    assert not (result.review_before_vigorous or result.no_all_out_sprints)


INJURY_RULE = (
    'recovery-habits.md: "Some pain during exercise is acceptable in chronic, assessed pain"'
)


def _injury(**kw):
    return {"area": "right shoulder", "status": "active"} | kw


def test_an_active_injury_pauses_its_exercises():
    injury = _injury(professional="physiotherapist", exercises=["Bench Press (Barbell)"])
    result = flags(Profile(screening=SCREENED_OK, injuries=[injury]))
    assert list(result.paused_exercises) == ["Bench Press (Barbell)"]
    pause = result.paused_exercises["Bench Press (Barbell)"]
    assert pause.assessed
    assert pause.reasons[0].startswith(INJURY_RULE) and "physiotherapist" in pause.reasons[0]
    assert not result.refer_gp


def test_an_unassessed_injury_refers_before_loading_it():
    result = flags(Profile(screening=SCREENED_OK, injuries=[_injury(exercises=["Squat"])]))
    assert result.refer_gp
    assert INJURY_RULE in _rules(result)
    assert not result.paused_exercises["Squat"].assessed


def test_two_injuries_on_one_lift_keep_both_reasons_and_the_unassessed_wins():
    knee = _injury(area="knee", professional="physio", exercises=["Squat"])
    hip = _injury(area="hip", exercises=["squat"])
    pause = flags(Profile(screening=SCREENED_OK, injuries=[knee, hip])).paused_exercises["Squat"]
    assert len(pause.reasons) == 2 and not pause.assessed


def test_a_cleared_injury_pauses_nothing():
    cleared = _injury(status="cleared", cleared_on=date(2026, 3, 1), exercises=["Squat"])
    result = flags(Profile(screening=SCREENED_OK, injuries=[cleared]))
    assert result.paused_exercises == {} and not result.refer_gp
    assert result.reasons == []


# The emergency number the skills give for chest pain at rest, fainting and other emergencies:
# the client's own, else their region's, else unknown (the skills then ask).
def test_emergency_number_comes_from_the_region():
    assert flags(Profile(region="es", screening=SCREENED_OK)).emergency_number == "112"


def test_the_clients_own_emergency_number_wins():
    profile = Profile(region="es", emergency_number="911", screening=SCREENED_OK)
    assert flags(profile).emergency_number == "911"


def test_no_region_and_no_number_means_unknown():
    assert flags(Profile(screening=SCREENED_OK)).emergency_number is None
