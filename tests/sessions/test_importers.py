from datetime import datetime
from pathlib import Path

import pytest

from coach.sessions.importers import base, generic_csv, hevy_csv
from coach.sessions.importers.base import ImporterError, detect, get
from coach.sessions.store import append, read_sets

FIXTURES = Path(__file__).parent.parent / "fixtures"
HEVY = FIXTURES / "hevy"
GENERIC = FIXTURES / "generic"


def by_key(sets):
    return {(s.exercise, s.exercise_index, s.set_index): s for s in sets}


# Review Focus 2: "24 Jul 2025, 11:25" dates, warm-up sets, empty weight for bodyweight
def test_hevy_basic():
    sets = hevy_csv.HevyCsv().read(HEVY / "basic.csv")
    assert len(sets) == 8
    first = sets[0]
    assert first.source == "hevy_csv"
    assert first.start_time == datetime(2025, 7, 24, 11, 25)
    assert first.session_title == "Push A"
    assert first.set_type == "warmup"
    rows = by_key(sets)
    assert rows[("Bench Press (Barbell)", 0, 1)].weight_kg == 62.5
    assert rows[("Bench Press (Barbell)", 0, 1)].rpe == 8
    assert rows[("Bench Press (Barbell)", 0, 1)].notes == "Paused reps, slow"
    pull_up = rows[("Pull Up", 1, 0)]
    assert pull_up.weight_kg is None and pull_up.reps == 9
    assert pull_up.notes == "Line one\nline two, with a comma"
    assert rows[("Pull Up", 1, 1)].set_type == "normal"  # lower-cased
    assert rows[("Lateral Raise (Dumbbell)", 2, 0)].set_type == "mystery"  # kept
    assert rows[("Lateral Raise (Dumbbell)", 2, 0)].weight_kg == 8.25
    run = rows[("Running", 0, 0)]
    assert run.start_time == datetime(2025, 7, 26, 7, 5)
    assert (run.distance_km, run.duration_s, run.reps) == (5.2, 1800, None)


# Review Focus 2: BOM
def test_hevy_bom():
    sets = hevy_csv.HevyCsv().read(HEVY / "bom.csv")
    assert [s.exercise for s in sets] == ["Squat (Barbell)"] * 2
    assert hevy_csv.HevyCsv().can_read(HEVY / "bom.csv")


# Review Focus 2: kg vs lbs exports
def test_hevy_lbs_and_miles_convert_to_metric():
    sets = hevy_csv.HevyCsv().read(HEVY / "lbs.csv")
    assert sets[0].weight_kg == pytest.approx(135 * 0.45359237)
    assert sets[1].distance_km == pytest.approx(2 * 1.609344)


# Review Focus 2: duplicate rows across overlapping exports
def test_hevy_overlapping_exports(tmp_path):
    store = tmp_path / "sessions.csv"
    importer = hevy_csv.HevyCsv()
    first = append(importer.read(HEVY / "overlap_a.csv"), store)
    second = append(importer.read(HEVY / "overlap_b.csv"), store)
    assert (first.added, first.duplicates) == (2, 0)
    # overlap_b repeats both sets of 5 Aug and adds one set on 8 Aug.
    assert (second.added, second.duplicates) == (1, 2)
    assert len(read_sets(store)) == 3


def test_hevy_same_exercise_twice_in_a_session():
    sets = hevy_csv.HevyCsv().read(HEVY / "repeat_exercise.csv")
    assert [(s.exercise, s.exercise_index, s.set_index) for s in sets] == [
        ("Bench Press (Barbell)", 0, 0),
        ("Bench Press (Barbell)", 0, 1),
        ("Squat (Barbell)", 1, 0),
        ("Bench Press (Barbell)", 2, 0),
        ("Bench Press (Barbell)", 2, 1),
    ]
    assert len({s.key for s in sets}) == 5


def test_hevy_iso_dates():
    sets = hevy_csv.HevyCsv().read(HEVY / "iso_dates.csv")
    assert sets[0].start_time == datetime(2025, 8, 12, 18, 30)


def test_hevy_bad_date_names_the_value():
    with pytest.raises(ImporterError, match="yesterday evening"):
        hevy_csv.HevyCsv().read(HEVY / "bad_date.csv")


def test_every_english_month_parses():
    months = "Jan Feb Mar Apr May Jun Jul Aug Sep Oct Nov Dec".split()
    for number, month in enumerate(months, start=1):
        assert hevy_csv.parse_datetime(f"3 {month} 2026, 9:05").month == number
    assert hevy_csv.parse_datetime("3 Sept 2026, 9:05").month == 9


def test_month_names_do_not_follow_a_spanish_locale():
    import locale

    previous = locale.setlocale(locale.LC_TIME)
    try:
        locale.setlocale(locale.LC_TIME, "es_ES.UTF-8")
    except locale.Error:
        pytest.skip("es_ES.UTF-8 locale not installed")
    try:
        # "Aug" is not a Spanish abbreviation ("ago"), so strptime("%b") would fail here.
        assert hevy_csv.parse_datetime("24 Aug 2025, 11:25").month == 8
    finally:
        locale.setlocale(locale.LC_TIME, previous)


def test_impossible_date_is_an_importer_error():
    with pytest.raises(ImporterError, match="31 Feb"):
        hevy_csv.parse_datetime("31 Feb 2025, 10:00")


def test_hevy_identical_repeated_block_is_kept():
    sets = hevy_csv.HevyCsv().read(HEVY / "repeat_identical.csv")
    assert [(s.exercise, s.exercise_index) for s in sets] == [
        ("Bench Press (Barbell)", 0),
        ("Squat (Barbell)", 1),
        ("Bench Press (Barbell)", 2),
    ]


def test_hevy_missing_columns(tmp_path):
    path = tmp_path / "x.csv"
    path.write_text("title,start_time\nA,1 Jan 2025, 10:00\n")
    assert not hevy_csv.HevyCsv().can_read(path)
    with pytest.raises(ImporterError, match="exercise_title"):
        hevy_csv.HevyCsv().read(path)


def test_generic_csv():
    sets = generic_csv.GenericCsv().read(GENERIC / "basic.csv")
    assert len(sets) == 5
    assert sets[0].start_time == datetime(2025, 8, 14)
    assert sets[0].rir == 2 and sets[0].weight_kg == 24 and sets[0].set_type == "normal"
    assert [(s.exercise, s.exercise_index, s.set_index) for s in sets[:4]] == [
        ("Goblet Squat", 0, 0),
        ("Goblet Squat", 0, 1),
        ("Push Up", 1, 0),
        ("Goblet Squat", 2, 0),
    ]
    assert sets[2].weight_kg is None
    walk = sets[4]
    assert walk.start_time == datetime(2025, 8, 15, 7, 30) and walk.notes == "park loop, 40 min"


def test_generic_keeps_identical_straight_sets_and_non_contiguous_sessions():
    sets = generic_csv.GenericCsv().read(GENERIC / "straight_sets.csv")
    assert len(sets) == 6
    assert [s.set_index for s in sets[:3]] == [0, 1, 2]
    # The last row belongs to 08-14 again (file sorted oddly): it continues that session's
    # numbering instead of colliding with its first Bench Press block.
    keys = {s.key for s in sets}
    assert len(keys) == 6
    last = sets[-1]
    assert (last.start_time.day, last.exercise_index, last.set_index) == (14, 1, 1)


@pytest.mark.parametrize(
    "row,message",
    [
        ("2025-08-14,Curl,12,5,10", "more fields than the header"),
        ("2025-08-14,Curl,inf,10", "finite"),
        ("2025-08-14,Curl,nan,10", "finite"),
        ("2025-08-14,Curl,12,8.5", "whole number"),
    ],
)
def test_generic_bad_values_name_the_problem(tmp_path, row, message):
    path = tmp_path / "x.csv"
    path.write_text(f"date,exercise,weight_kg,reps\n{row}\n")
    with pytest.raises(ImporterError, match=message):
        generic_csv.GenericCsv().read(path)


def test_generic_lbs():
    sets = generic_csv.GenericCsv().read(GENERIC / "lbs.csv")
    assert sets[0].weight_kg == pytest.approx(225 * 0.45359237)


def test_registry_detects_and_refuses_unknown(tmp_path):
    assert detect(HEVY / "basic.csv").name == "hevy_csv"
    assert detect(GENERIC / "basic.csv").name == "generic_csv"
    assert get("hevy_csv").name == "hevy_csv"
    other = tmp_path / "other.csv"
    other.write_text("foo,bar\n1,2\n")
    with pytest.raises(ImporterError, match="no importer"):
        detect(other)


def test_registry_refuses_ambiguity(tmp_path, monkeypatch):
    class Greedy:
        name = "greedy"

        def can_read(self, path):
            return True

        def read(self, path):
            return []

    monkeypatch.setattr(base, "IMPORTERS", [*base.IMPORTERS, Greedy()])
    with pytest.raises(ImporterError, match="more than one"):
        detect(HEVY / "basic.csv")


def test_hevy_reads_template_leftovers_and_marks_them_empty():
    sets = hevy_csv.HevyCsv().read(HEVY / "template_leftover.csv")
    assert len(sets) == 6
    assert [s.is_empty for s in sets] == [False, False, True, True, False, True]
    plank = next(s for s in sets if s.exercise == "Plank")
    assert plank.duration_s == 60 and not plank.is_empty
