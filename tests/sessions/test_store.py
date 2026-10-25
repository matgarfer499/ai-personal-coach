from datetime import date, datetime

import pytest

from coach.sessions.model import ExerciseSet, group_sessions
from coach.sessions.store import StoreError, append, read_sets

T1 = datetime(2026, 3, 2, 18, 30)
T2 = datetime(2026, 3, 4, 7, 15)


def s(start=T1, exercise="Bench Press (Barbell)", exercise_index=0, set_index=0, **kw):
    return ExerciseSet(
        source="hevy_csv",
        start_time=start,
        exercise=exercise,
        exercise_index=exercise_index,
        set_index=set_index,
        **({"weight_kg": 60.0, "reps": 8} | kw),
    )


def test_derived_fields():
    one = s()
    assert one.date == date(2026, 3, 2)
    assert one.session_id == "hevy_csv:2026-03-02T18:30:00"


def test_append_and_read_round_trip(tmp_path):
    path = tmp_path / "sessions.csv"
    sets = [
        s(set_index=0, set_type="warmup", weight_kg=40.0, reps=10),
        s(set_index=1, rir=2.0, notes='paused, "slow"\nsecond line'),
        s(exercise="Pull Up", exercise_index=1, weight_kg=None, reps=8, rpe=8.5),
        s(
            start=T2,
            exercise="Running",
            weight_kg=None,
            reps=None,
            distance_km=5.2,
            duration_s=1800,
        ),
    ]
    result = append(sets, path)
    assert (result.added, result.duplicates) == (4, 0)
    assert read_sets(path) == sets


def test_overlapping_export_counts_duplicates(tmp_path):
    path = tmp_path / "sessions.csv"
    append([s(set_index=0), s(set_index=1)], path)
    result = append([s(set_index=1), s(set_index=2)], path)
    assert (result.added, result.duplicates) == (1, 1)
    assert [x.set_index for x in read_sets(path)] == [0, 1, 2]


def test_duplicates_within_one_batch(tmp_path):
    result = append([s(), s()], tmp_path / "sessions.csv")
    assert (result.added, result.duplicates) == (1, 1)


def test_same_exercise_twice_in_one_session_is_not_a_duplicate(tmp_path):
    path = tmp_path / "sessions.csv"
    first_block = [s(exercise_index=0, set_index=i) for i in range(2)]
    second_block = [s(exercise_index=3, set_index=i, weight_kg=50.0) for i in range(2)]
    result = append(first_block + second_block, path)
    assert (result.added, result.duplicates) == (4, 0)


def test_existing_row_wins_on_same_key(tmp_path):
    path = tmp_path / "sessions.csv"
    append([s(weight_kg=60.0)], path)
    result = append([s(weight_kg=62.5)], path)
    assert (result.added, result.duplicates) == (0, 1)
    assert read_sets(path)[0].weight_kg == 60.0


def test_rows_are_stored_in_time_order(tmp_path):
    path = tmp_path / "sessions.csv"
    append([s(start=T2)], path)
    append([s(start=T1)], path)
    assert [x.start_time for x in read_sets(path)] == [T1, T2]


def test_missing_file_reads_empty(tmp_path):
    assert read_sets(tmp_path / "none.csv") == []


def test_group_sessions():
    sessions = group_sessions([s(start=T2), s(set_index=1), s(set_index=0)])
    assert [x.start_time for x in sessions] == [T1, T2]
    assert [x.set_index for x in sessions[0].sets] == [0, 1]
    assert sessions[0].session_id == "hevy_csv:2026-03-02T18:30:00"


def test_store_with_bom_still_deduplicates(tmp_path):
    path = tmp_path / "sessions.csv"
    append([s()], path)
    path.write_bytes(b"\xef\xbb\xbf" + path.read_bytes())
    assert read_sets(path)[0].source == "hevy_csv"
    assert append([s()], path).duplicates == 1


def test_store_refuses_a_changed_header(tmp_path):
    path = tmp_path / "sessions.csv"
    append([s()], path)
    text = path.read_text()
    path.write_text(text.replace("notes", "notes,my_column", 1).replace("\n", ",x\n", 2)[:-2])
    with pytest.raises(StoreError, match="my_column"):
        read_sets(path)


def test_store_bad_line_names_file_and_line(tmp_path):
    path = tmp_path / "sessions.csv"
    append([s()], path)
    path.write_text(path.read_text().replace(",0,0,", ",0,5.0,", 1))
    with pytest.raises(StoreError, match="line 2"):
        read_sets(path)
