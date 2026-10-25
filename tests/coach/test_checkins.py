from datetime import date

import pytest

from coach.checkins import Checkin, append_checkin, read_checkins, weigh_ins


def test_append_and_read_round_trip(tmp_path):
    path = tmp_path / "checkins.csv"
    first = Checkin(date(2026, 3, 2), weight_kg=80.4, intake_kcal=2100, sleep_hours=7.5)
    second = Checkin(date(2026, 3, 3), waist_cm=88.0, notes="tired, slept badly")
    append_checkin(first, path)
    append_checkin(second, path)
    assert read_checkins(path) == [first, second]
    assert path.read_text().splitlines()[0].startswith("date,weight_kg")


def test_missing_file_reads_empty(tmp_path):
    assert read_checkins(tmp_path / "none.csv") == []


def test_same_day_checkin_overrides_only_the_fields_it_gives(tmp_path):
    path = tmp_path / "checkins.csv"
    append_checkin(Checkin(date(2026, 3, 2), weight_kg=80.4, notes="morning"), path)
    append_checkin(Checkin(date(2026, 3, 2), weight_kg=80.1), path)
    append_checkin(Checkin(date(2026, 3, 2), sleep_hours=7.0, notes="evening"), path)
    assert read_checkins(path) == [
        Checkin(date(2026, 3, 2), weight_kg=80.1, sleep_hours=7.0, notes="morning; evening")
    ]


def test_weigh_ins_skip_rows_without_weight():
    rows = [Checkin(date(2026, 3, 2), weight_kg=80.0), Checkin(date(2026, 3, 3), waist_cm=88)]
    assert weigh_ins(rows) == [(date(2026, 3, 2), 80.0)]


def test_rejects_implausible_weight(tmp_path):
    with pytest.raises(ValueError, match="weight_kg"):
        append_checkin(Checkin(date(2026, 3, 2), weight_kg=8000), tmp_path / "c.csv")


def test_reads_a_file_saved_with_a_bom(tmp_path):
    path = tmp_path / "checkins.csv"
    path.write_text("﻿date,weight_kg,waist_cm,intake_kcal,sleep_hours,notes\n2026-03-02,80,,,,\n")
    assert read_checkins(path)[0].weight_kg == 80


def test_a_file_without_a_date_column_is_a_clear_error(tmp_path):
    path = tmp_path / "checkins.csv"
    path.write_text("day,weight\n2026-03-02,80\n")
    with pytest.raises(ValueError, match="date"):
        read_checkins(path)


@pytest.mark.parametrize(
    "field,value",
    [("sleep_hours", -3), ("sleep_hours", 30), ("intake_kcal", -500), ("waist_cm", 0)],
)
def test_rejects_impossible_values(tmp_path, field, value):
    with pytest.raises(ValueError, match=field):
        append_checkin(Checkin(date(2026, 3, 2), **{field: value}), tmp_path / "c.csv")
