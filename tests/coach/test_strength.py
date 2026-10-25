from dataclasses import dataclass
from datetime import date, timedelta

import pytest

from coach.safety import Pause, SafetyFlags
from coach.strength import (
    deload,
    e1rm,
    hard_set,
    load_muscle_map,
    lookup,
    parse_rep_range,
    progression,
    rep_range_for,
    unmapped_exercises,
    weekly_hard_sets,
)

D0 = date(2026, 3, 2)


@dataclass
class S:
    exercise: str
    weight_kg: float | None
    reps: int | None
    date: date = D0
    set_type: str = "normal"
    rir: float | None = None
    rpe: float | None = None


# convention: Epley, e1RM = load x (1 + reps / 30), with RIR added to reps
def test_e1rm_epley():
    assert e1rm(100, 10) == pytest.approx(100 * (1 + 10 / 30))
    assert e1rm(100, 8, rir=2) == pytest.approx(e1rm(100, 10))
    assert e1rm(100, 1) == 100
    with pytest.raises(ValueError):
        e1rm(100, 0)
    with pytest.raises(ValueError, match="negative"):
        e1rm(100, 1, rir=-3)


# strength-hypertrophy.md "Target reps in reserve": warm-ups don't count; 5+ RIR is too easy
def test_hard_set():
    assert hard_set(S("bench press", 60, 10))
    assert hard_set(S("bench press", 60, 10, rir=4))
    assert not hard_set(S("bench press", 60, 10, rir=5))
    assert not hard_set(S("bench press", 40, 10, set_type="warmup"))
    assert hard_set(S("bench press", 60, 10, rpe=8))
    assert not hard_set(S("bench press", 60, 10, rpe=5))


def test_lookup_ignores_equipment_suffix_and_case():
    muscle_map = load_muscle_map()
    assert lookup("Bench Press (Barbell)", muscle_map)["muscles"]["chest"] == 1
    assert lookup("BENCH PRESS", muscle_map)["muscles"]["triceps"] == 0.5
    assert lookup("Zercher Carry", muscle_map) is None
    assert lookup("Press Banca", muscle_map)["muscles"]["chest"] == 1
    assert lookup("Sentadilla (Barra)", muscle_map)["lower_body"]


# strength-hypertrophy.md "Default counting rule" and "Pressing: chest 1, triceps and front
# delts 0.5": 12 bench sets is about 6 triceps sets, not 12.
def test_weekly_hard_sets_fractional():
    sets = [S("Bench Press (Barbell)", 60, 8) for _ in range(12)]
    totals = weekly_hard_sets(sets, load_muscle_map())
    assert totals["chest"] == 12
    assert totals["triceps"] == 6
    assert "side_delts" not in totals


def test_weekly_hard_sets_skips_warmups_and_easy_sets_and_reports_unmapped():
    sets = [
        S("Squat (Barbell)", 40, 10, set_type="warmup"),
        S("Squat (Barbell)", 100, 5, rir=2),
        S("Squat (Barbell)", 100, 5, rir=6),
        S("Lat Pulldown (Cable)", 50, 10),
        S("Zercher Carry", 80, None),
    ]
    muscle_map = load_muscle_map()
    totals = weekly_hard_sets(sets, muscle_map)
    assert totals["quads"] == 1 and totals["glutes"] == 0.5
    assert "hamstrings" not in totals
    assert totals["biceps"] == 0.5
    assert unmapped_exercises(sets, muscle_map) == ["Zercher Carry"]


def session(day, weight, reps, n=3, exercise="Bench Press (Barbell)", rir=2):
    return [S(exercise, weight, reps, date=day, rir=rir) for _ in range(n)]


# strength-hypertrophy.md "Double progression": beat the top of the range by 1-2 reps on all
# work sets, then add a small increment (2-10%).
def test_progression_increase_load_upper_body():
    history = session(D0, 60, 13)
    suggestion = progression(history, today=D0 + timedelta(3))
    assert suggestion.action == "increase_load"
    assert suggestion.load_kg == pytest.approx(61.5)  # +2.5%, rounded to 0.5 kg
    assert 'strength-hypertrophy.md: "Double progression"' in suggestion.reasons[0]


def test_progression_increase_load_lower_body_bigger_step():
    history = session(D0, 100, 13, exercise="Squat (Barbell)")
    assert progression(history, today=D0 + timedelta(3)).load_kg == pytest.approx(105)


def test_progression_small_load_still_goes_up():
    for load in (8, 10):
        suggestion = progression(session(D0, load, 13), today=D0 + timedelta(3))
        assert suggestion.load_kg == load + 0.5


def test_bodyweight_progress_is_measured_in_reps():
    history = []
    for i, reps in enumerate([6, 7, 8, 9, 10]):
        history += session(D0 + timedelta(3 * i), None, reps, exercise="Pull Up")
    suggestion = progression(history, today=D0 + timedelta(14))
    assert suggestion.action == "add_reps"
    assert suggestion.load_kg is None


def test_bodyweight_stall_and_top_of_range():
    stalled = []
    for i in range(4):
        stalled += session(D0 + timedelta(3 * i), None, 8, exercise="Pull Up")
    assert progression(stalled, today=D0 + timedelta(10)).action == "stalled"
    top = progression(session(D0, None, 13, exercise="Pull Up"), today=D0 + timedelta(2))
    assert top.action == "increase_load" and top.load_kg is None
    assert "harder variation" in top.reasons[0]


def test_progression_add_reps_when_not_at_top():
    history = session(D0, 60, 10)
    suggestion = progression(history, today=D0 + timedelta(3))
    assert suggestion.action == "add_reps"
    assert suggestion.load_kg == 60


def test_progression_one_set_below_top_means_add_reps():
    history = session(D0, 60, 13, n=2) + [S("Bench Press (Barbell)", 60, 11, rir=2)]
    assert progression(history, today=D0 + timedelta(3)).action == "add_reps"


def test_progression_too_easy():
    suggestion = progression(session(D0, 40, 10, rir=6), today=D0 + timedelta(3))
    assert suggestion.action == "too_easy"


# strength-hypertrophy.md "When progress stalls": no gain in load or reps for about 3 sessions
def test_progression_stalled():
    history = []
    for i in range(4):
        history += session(D0 + timedelta(3 * i), 60, 10)
    suggestion = progression(history, today=D0 + timedelta(10))
    assert suggestion.action == "stalled"
    assert 'strength-hypertrophy.md: "When progress stalls"' in suggestion.reasons[0]


def test_progression_not_stalled_when_reps_rise():
    history = []
    for i, reps in enumerate([9, 10, 10, 11]):
        history += session(D0 + timedelta(3 * i), 60, reps)
    assert progression(history, today=D0 + timedelta(10)).action == "add_reps"


# strength-hypertrophy.md "Short breaks cost little": under about 2 weeks off, about 90%; longer,
# 10-20% below.
def test_progression_after_short_break():
    suggestion = progression(session(D0, 100, 10), today=D0 + timedelta(10))
    assert suggestion.action == "restart"
    assert suggestion.load_kg == pytest.approx(90)


def test_progression_after_long_break():
    suggestion = progression(session(D0, 100, 10), today=D0 + timedelta(30))
    assert suggestion.action == "restart"
    assert suggestion.load_kg == pytest.approx(85)


def test_progression_without_history():
    assert progression([], today=D0).action == "no_data"
    only_warmups = [S("Bench Press (Barbell)", 20, 10, set_type="warmup")]
    assert progression(only_warmups, today=D0).action == "no_data"


def test_progression_rejects_mixed_exercises():
    history = session(D0, 60, 10) + session(D0, 100, 5, exercise="Squat (Barbell)")
    with pytest.raises(ValueError, match="one exercise"):
        progression(history, today=D0)


# strength-hypertrophy.md "Deloads": two or more of the four signs persisting together
def test_deload():
    assert deload({"performance_stall"}) is None
    result = deload({"performance_stall", "poor_sleep"})
    assert result.volume_cut == (0.3, 0.5)
    assert result.extra_rest_days == (0, 0)
    assert result.stop_rir == 3


def test_deload_overreaching_adds_rest_days():
    # Performance dropping despite rest, plus poor sleep or mood.
    assert deload({"drop_despite_rest", "low_mood"}).extra_rest_days == (1, 3)
    assert deload({"drop_despite_rest", "poor_sleep"}).extra_rest_days == (1, 3)
    # Mood alone is not one of the four deload signs.
    assert deload({"low_mood", "joint_aches"}) is None


def test_deload_rejects_unknown_signs():
    with pytest.raises(ValueError, match="tired"):
        deload({"tired"})


def test_aliases_are_unique_and_do_not_shadow_names():
    muscle_map = load_muscle_map()
    seen = set(muscle_map)
    for entry in muscle_map.values():
        for alias in entry.get("aliases", []):
            assert alias == alias.lower() and alias not in seen, alias
            seen.add(alias)


# recovery-habits.md "PAR-Q+ 2023 as the default entry screen": pause any progression of
# intensity; "Resting BP thresholds to defer or refer": GP review before progressing.
def test_progression_holds_when_safety_says_so():
    held = SafetyFlags(hold_progression=True, reasons=["PAR-Q+ follow-up YES"])
    suggestion = progression(session(D0, 60, 13), today=D0 + timedelta(3), flags=held)
    assert suggestion.action == "hold" and suggestion.load_kg == 60
    assert "PAR-Q+ follow-up YES" in suggestion.reasons


def test_progression_still_restarts_lower_when_held():
    held = SafetyFlags(hold_progression=True)
    suggestion = progression(session(D0, 100, 10), today=D0 + timedelta(10), flags=held)
    assert suggestion.action == "restart" and suggestion.load_kg == pytest.approx(90)


def test_progression_under_no_training_prescribes_nothing():
    stop = SafetyFlags(no_training=True, hold_progression=True)
    suggestion = progression(session(D0, 60, 13), today=D0 + timedelta(3), flags=stop)
    assert suggestion.action == "no_training" and suggestion.load_kg is None


def test_spanish_aliases_resolve_to_their_lift():
    muscle_map = load_muscle_map()
    assert lookup("Press banca", muscle_map) is muscle_map["bench press"]
    assert lookup("jalon al pecho", muscle_map) is muscle_map["lat pulldown"]  # accents optional


# convention: an active injury's listed exercises keep their last load; the professional managing
# it decides when they progress ("Some pain during exercise is acceptable in chronic, assessed
# pain").
PAUSED = SafetyFlags(
    paused_exercises={"bench press": Pause(["shoulder injury, physiotherapist"], assessed=True)}
)
UNASSESSED = SafetyFlags(paused_exercises={"bench press": Pause(["shoulder injury"], False)})


def test_paused_exercise_keeps_its_load_instead_of_stalling():
    history = []
    for i in range(4):
        history += session(D0 + timedelta(3 * i), 60, 10)
    suggestion = progression(history, today=D0 + timedelta(10), flags=PAUSED)
    assert suggestion.action == "paused" and suggestion.load_kg == 60
    assert suggestion.reasons == ["shoulder injury, physiotherapist"]


def test_a_pause_never_prints_more_than_a_restart_after_a_break():
    # "Short breaks cost little": after 2+ weeks off, restart 10-20% below.
    paused = progression(session(D0, 60, 13), today=D0 + timedelta(20), flags=PAUSED)
    assert paused.action == "paused" and paused.load_kg == pytest.approx(51)


def test_an_unassessed_injury_gets_no_load_at_all():
    # "Some pain during exercise is acceptable in chronic, assessed pain": acute or unassessed
    # pain is referred, not loaded.
    paused = progression(session(D0, 60, 13), today=D0 + timedelta(3), flags=UNASSESSED)
    assert paused.action == "paused" and paused.load_kg is None


def test_pause_spares_other_lifts():
    squat = session(D0, 100, 13, exercise="Squat (Barbell)")
    assert progression(squat, today=D0 + timedelta(3), flags=PAUSED).action == "increase_load"


def test_sessions_inside_a_finished_pause_do_not_count_as_a_stall():
    history = []
    for i in range(4):
        history += session(D0 + timedelta(3 * i), 60, 10)
    resumed = D0 + timedelta(8)  # cleared after the third session
    suggestion = progression(history, today=D0 + timedelta(10), stall_after=resumed)
    assert suggestion.action == "add_reps"
    later = history + session(D0 + timedelta(12), 60, 10) + session(D0 + timedelta(15), 60, 10)
    later += session(D0 + timedelta(18), 60, 10)
    assert progression(later, today=D0 + timedelta(19), stall_after=resumed).action == "stalled"


# strength-hypertrophy.md "Double progression" (pick a rep range, for example 8-12) and "Load range
# for maximal strength" (heavier work in the 3-8 range): the range is chosen per lift.
def test_parse_rep_range():
    assert parse_rep_range("Bench Press (Barbell)=6-8") == ("Bench Press (Barbell)", (6, 8))
    assert parse_rep_range(" squat = 8 - 12 ") == ("squat", (8, 12))


@pytest.mark.parametrize(
    "text, message",
    [
        ("bench press", "EXERCISE=LOW-HIGH"),
        ("bench press=8", "EXERCISE=LOW-HIGH"),
        ("bench press=a-b", "EXERCISE=LOW-HIGH"),
        ("=6-8", "exercise"),
        ("bench press=0-5", "at least 1"),
        ("bench press=8-8", "lower than"),
        ("bench press=12-8", "lower than"),
    ],
)
def test_parse_rep_range_rejects_bad_input(text, message):
    with pytest.raises(ValueError, match=message):
        parse_rep_range(text)


def test_rep_range_for_matches_names_like_the_rest_of_the_coach():
    ranges = [parse_rep_range("bench press=6-8")]
    assert rep_range_for("Bench Press (Barbell)", ranges) == (6, 8)
    assert rep_range_for("Press de banca", ranges) == (8, 12)  # no alias matching: default
    assert rep_range_for("Squat (Barbell)", ranges) == (8, 12)
    assert rep_range_for("Squat", []) == (8, 12)
    # the last range given for a lift wins
    ranges.append(parse_rep_range("BENCH PRESS=5-7"))
    assert rep_range_for("Bench Press (Barbell)", ranges) == (5, 7)


# Hevy catalogue names that were unmapped: curls and calf raises credit the muscle they
# isolate; a carry works the trunk and grip, which are not among the 12 counted muscles.
@pytest.mark.parametrize(
    "logged, key",
    [
        ("EZ Bar Biceps Curl", "bicep curl"),
        ("EZ Bar Biceps Curl (Barbell)", "bicep curl"),
        ("Single Leg Standing Calf Raise", "standing calf raise"),
        ("Single Leg Standing Calf Raise (Dumbbell)", "standing calf raise"),
        ("Suitcase Carry", "suitcase carry"),
        ("Suitcase Carry (Dumbbell)", "suitcase carry"),
    ],
)
def test_real_export_names_resolve(logged, key):
    muscle_map = load_muscle_map()
    assert lookup(logged, muscle_map) is muscle_map[key]


def test_suitcase_carry_is_known_but_credits_no_muscle():
    muscle_map = load_muscle_map()
    sets = [S("Suitcase Carry (Dumbbell)", 24, 10), S("EZ Bar Biceps Curl", 30, 10)]
    assert unmapped_exercises(sets, muscle_map) == []
    assert weekly_hard_sets(sets, muscle_map) == {"biceps": 1}
    calf = [S("Single Leg Standing Calf Raise", None, 12)]
    assert weekly_hard_sets(calf, muscle_map) == {"calves": 1}
    # Zercher Carry has no entry: a carry is mapped by name, not by the word "carry"
    assert unmapped_exercises([S("Zercher Carry", 40, 8)], muscle_map) == ["Zercher Carry"]
