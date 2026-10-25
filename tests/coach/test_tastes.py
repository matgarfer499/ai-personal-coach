import json
from datetime import date

import pytest

from coach.cli import main
from coach.tastes import ASKED, Rating, Tastes, load_tastes, matches, save_tastes

TODAY = "2026-10-25"


def run(capsys, data_dir, *args):
    code = main(["--data-dir", str(data_dir), "--today", TODAY, *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_missing_file_is_an_empty_profile(tmp_path):
    tastes = load_tastes(tmp_path / "tastes.yaml")
    assert tastes.missing() == list(ASKED)
    assert tastes.ratings == []


def test_empty_list_means_asked_with_no_answer(tmp_path):
    path = tmp_path / "tastes.yaml"
    save_tastes(Tastes(allergies=[], chains=["Mercadona"]), path)
    tastes = load_tastes(path)
    assert tastes.allergies == [] and tastes.chains == ["Mercadona"]
    assert "allergies" not in tastes.missing() and "loved_foods" in tastes.missing()


def test_round_trip_with_ratings(tmp_path):
    path = tmp_path / "tastes.yaml"
    tastes = Tastes(
        cooking_minutes=20,
        cooking_skill="beginner",
        budget="medium",
        postal_code="46001",
        ratings=[Rating(dish="Bowl de pollo", rating="loved", date=date(2026, 10, 1))],
    )
    save_tastes(tastes, path)
    assert load_tastes(path) == tastes


@pytest.mark.parametrize(
    "text, message",
    [
        ("cooking_skill: chef\n", "cooking_skill"),
        ("budget: cheap\n", "budget"),
        ("cooking_minutes: true\n", "cooking_minutes"),
        ("cooking_minutes: 0\n", "cooking_minutes"),
        ("postal_code: 46001\n", "postal_code"),  # unquoted YAML number
        ("postal_code: '46001; drop'\n", "postal_code"),
        ("chains: Mercadona\n", "chains"),
        ("nickname: x\n", "unknown"),
        ("ratings: [{dish: x, rating: meh, date: 2026-10-01}]\n", "rating"),
        ("- a list\n", "field: value"),
    ],
)
def test_hand_edited_file_is_validated(tmp_path, text, message):
    path = tmp_path / "tastes.yaml"
    path.write_text(text, encoding="utf-8")
    with pytest.raises(ValueError, match=message):
        load_tastes(path)


def test_cli_show_lists_missing_fields(capsys, tmp_path):
    code, out = run(capsys, tmp_path, "tastes", "show")
    assert code == 0
    assert out["missing"] == list(ASKED)
    assert out["favoured"] == [] and out["excluded"] == []


def test_cli_set_lists_ints_enums_and_none(capsys, tmp_path):
    run(capsys, tmp_path, "tastes", "set", "loved_foods", "aguacate, salmón ,")
    run(capsys, tmp_path, "tastes", "set", "allergies", "none")
    run(capsys, tmp_path, "tastes", "set", "cooking_minutes", "25")
    code, out = run(capsys, tmp_path, "tastes", "set", "cooking_skill", "intermediate")
    assert code == 0
    assert out["tastes"]["loved_foods"] == ["aguacate", "salmón"]
    assert out["tastes"]["allergies"] == []
    assert out["tastes"]["cooking_minutes"] == 25
    assert "allergies" not in out["missing"] and "budget" in out["missing"]
    assert load_tastes(tmp_path / "tastes.yaml").cooking_skill == "intermediate"


def test_cli_postal_code_none_records_a_refusal(capsys, tmp_path):
    _, out = run(capsys, tmp_path, "tastes", "set", "postal_code", "none")
    assert out["tastes"]["postal_code"] == "" and "postal_code" not in out["missing"]


@pytest.mark.parametrize(
    "field, value, message",
    [
        ("cooking_minutes", "quick", "whole number"),
        ("budget", "cheap", "budget"),
        ("cooking_skill", "none", "cooking_skill"),
        ("ratings", "x", "tastes rate"),
        ("nickname", "x", "unknown"),
    ],
)
def test_cli_set_rejects_bad_values(capsys, tmp_path, field, value, message):
    code, out = run(capsys, tmp_path, "tastes", "set", field, value)
    assert code == 2 and message in out["message"]
    assert not (tmp_path / "tastes.yaml").exists()


def test_cli_rate_replaces_an_earlier_rating_of_the_same_dish(capsys, tmp_path):
    run(capsys, tmp_path, "tastes", "rate", "Bowl de pollo al limón", "liked")
    run(capsys, tmp_path, "tastes", "rate", "Revuelto de setas", "never_again", "--note", "seco")
    _, out = run(
        capsys,
        tmp_path,
        "tastes",
        "rate",
        "bowl de pollo al limon",
        "loved",
        "--source",
        "https://example.org/bowl",
    )
    ratings = out["tastes"]["ratings"]
    assert [r["dish"] for r in ratings] == ["Revuelto de setas", "bowl de pollo al limon"]
    assert ratings[1] == {
        "dish": "bowl de pollo al limon",
        "rating": "loved",
        "date": TODAY,
        "source": "https://example.org/bowl",
        "note": "",
    }
    assert out["favoured"] == ["bowl de pollo al limon"]
    assert out["excluded"] == ["Revuelto de setas"]


def test_cli_rate_rejects_an_unknown_rating(capsys, tmp_path):
    code, out = run(capsys, tmp_path, "tastes", "rate", "Bowl", "meh")
    assert code == 2 and "meh" in out["message"]


@pytest.mark.parametrize(
    "phrase, name, expected",
    [
        ("tomate", "tomate, crudo", True),
        ("tomate", "salsa de tomate", True),
        ("tomate crudo", "tomate, crudo", True),
        ("tomate crudo", "salsa de tomate", False),
        ("tomate crudo", "tomate", True),  # the plain table name is the raw food
        ("tomate fresco", "salsa de tomate", False),
        ("pollo crudo", "pechuga de pollo, cruda", True),  # gender ignored
        ("pollo crudo", "pechuga de pollo, asada", False),
        ("pollo asado", "pollo", False),  # only raw words are implied
        ("crudo tomate", "Tomate, CRUDO", True),  # any order, case ignored
        ("tomates", "salsa de tomate", True),  # plural either way
        ("tomate", "tomates, rojos", True),
        ("limon", "limones", True),
        ("limón", "zumo de limon", True),  # accents ignored
        ("pollo", "repollo, crudo", False),  # whole words only
        ("lactosa", "leche entera", False),  # no synonyms: a miss is never proof
        ("", "tomate", False),
        ("  ", "tomate", False),
    ],
)
def test_a_phrase_matches_whole_words_of_a_food_name(phrase, name, expected):
    assert matches(phrase, name) is expected


def test_a_phrase_may_match_either_language_name():
    assert matches("chicken", "pechuga de pollo, cruda", "chicken breast, raw")
