import json
from datetime import date

import pytest
import yaml

from coach.cli import main
from coach.profile import Profile, save_profile

TODAY = "2026-10-25"


@pytest.fixture
def data_dir(tmp_path):
    save_profile(
        Profile(
            sex="female",
            birth_date=date(1992, 3, 10),
            height_cm=165,
            weight_kg=62,
            goal="maintenance",
            activity_level="desk",
            language="es",
            region="es",
            screening={"scoff_positive": False},
        ),
        tmp_path / "profile.yaml",
    )
    return tmp_path


def run(capsys, data_dir, *args):
    code = main(["--data-dir", str(data_dir), "--today", TODAY, *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def save_menu(data_dir):
    """A saved menu written directly (synthetic recipes, written fresh for the tests)."""
    document = {
        "saved_on": date(2026, 10, 25),
        "days": [
            {
                "date": date(2026, 10, 26),
                "meals": [
                    {
                        "meal": "Comida",
                        "dishes": [
                            {
                                "dish": "Lentejas con verduras",
                                "source": "https://example.org/lentejas",
                                "servings": 4,
                                "steps": ["Sofreír", "Cocer 25 min"],
                                "seasoning": ["pimentón"],
                                "items": ["lentejas, cocidas=200", "zanahoria=80"],
                            },
                            {
                                "dish": "Tortilla de calabacín",
                                "source": "https://example.org/tortilla",
                                "steps": ["Pochar", "Cuajar"],
                                "items": ["huevo=120", "calabacín=150"],
                            },
                        ],
                    }
                ],
            }
        ],
    }
    path = data_dir / "menus" / "2026-10-26.yaml"
    path.parent.mkdir(parents=True)
    path.write_text(yaml.safe_dump(document, allow_unicode=True, sort_keys=False))


def recipe_files(data_dir):
    return sorted(p.name for p in (data_dir / "recipes").glob("*.yaml"))


def test_rating_a_dish_loved_saves_its_recipe_from_the_saved_menu(capsys, data_dir):
    save_menu(data_dir)
    code, out = run(capsys, data_dir, "tastes", "rate", "lentejas con verduras", "loved")
    assert code == 0 and out["recipe_saved"] == "recipes/lentejas-con-verduras.yaml"
    saved = yaml.safe_load((data_dir / "recipes" / "lentejas-con-verduras.yaml").read_text())
    assert saved["dish"] == "Lentejas con verduras"  # the menu's own spelling
    assert saved["source"] == "https://example.org/lentejas" and saved["servings"] == 4
    assert saved["steps"] == ["Sofreír", "Cocer 25 min"]
    assert saved["items"] == ["lentejas, cocidas=200", "zanahoria=80"]
    assert saved["saved_on"] == date(2026, 10, 25)
    assert "kcal" not in saved and "totals" not in saved  # numbers always come from the CLI
    assert recipe_files(data_dir) == ["lentejas-con-verduras.yaml"]


def test_a_disliked_dish_is_not_saved(capsys, data_dir):
    save_menu(data_dir)
    _, out = run(capsys, data_dir, "tastes", "rate", "Tortilla de calabacín", "disliked")
    assert out["recipe_saved"] is None and not (data_dir / "recipes").exists()


def test_a_rated_dish_outside_the_menus_keeps_its_source_only(capsys, data_dir):
    _, out = run(
        capsys, data_dir, "tastes", "rate", "Gazpacho", "liked", "--source", "https://example.org/g"
    )
    assert out["recipe_saved"] == "recipes/gazpacho.yaml"
    saved = yaml.safe_load((data_dir / "recipes" / "gazpacho.yaml").read_text())
    assert saved == {
        "dish": "Gazpacho",
        "source": "https://example.org/g",
        "saved_on": date(2026, 10, 25),
    }
    _, out = run(capsys, data_dir, "tastes", "rate", "Sin enlace ni menú", "loved")
    assert out["recipe_saved"] is None


def test_list_and_search_show_the_rating_and_hide_never_again(capsys, data_dir):
    save_menu(data_dir)
    run(capsys, data_dir, "tastes", "rate", "Lentejas con verduras", "loved")
    run(capsys, data_dir, "tastes", "rate", "Tortilla de calabacín", "liked")
    _, out = run(capsys, data_dir, "recipes", "list")
    assert [(r["dish"], r["rating"]) for r in out["recipes"]] == [
        ("Lentejas con verduras", "loved"),
        ("Tortilla de calabacín", "liked"),
    ]
    _, found = run(capsys, data_dir, "recipes", "search", "calabacin")  # ingredient, no accent
    assert [r["dish"] for r in found["recipes"]] == ["Tortilla de calabacín"]
    _, found = run(capsys, data_dir, "recipes", "search", "lent", "verdu")  # word starts
    assert [r["dish"] for r in found["recipes"]] == ["Lentejas con verduras"]
    _, found = run(capsys, data_dir, "recipes", "search", "pimentón")  # seasoning
    assert len(found["recipes"]) == 1
    # a later never_again keeps the file but takes the dish out of searches
    run(capsys, data_dir, "tastes", "rate", "Lentejas con verduras", "never_again")
    _, found = run(capsys, data_dir, "recipes", "search", "lentejas")
    assert found["recipes"] == []
    _, out = run(capsys, data_dir, "recipes", "list")
    assert {r["dish"]: r["rating"] for r in out["recipes"]} == {
        "Lentejas con verduras": "never_again",
        "Tortilla de calabacín": "liked",
    }


def test_rerating_updates_the_saved_recipe_in_place(capsys, data_dir):
    save_menu(data_dir)
    run(capsys, data_dir, "tastes", "rate", "Lentejas con verduras", "liked")
    run(
        capsys,
        data_dir,
        "tastes",
        "rate",
        "lentejas con verduras",
        "loved",
        "--source",
        "https://x.org/y",
    )
    assert recipe_files(data_dir) == ["lentejas-con-verduras.yaml"]


def test_list_orders_loved_before_liked(capsys, data_dir):
    save_menu(data_dir)
    run(capsys, data_dir, "tastes", "rate", "Tortilla de calabacín", "loved")
    run(capsys, data_dir, "tastes", "rate", "Lentejas con verduras", "liked")
    _, out = run(capsys, data_dir, "recipes", "list")
    assert [r["dish"] for r in out["recipes"]] == ["Tortilla de calabacín", "Lentejas con verduras"]


def test_save_a_dish_by_hand_and_show_and_remove_it(capsys, data_dir):
    save_menu(data_dir)
    code, out = run(capsys, data_dir, "recipes", "save", "Tortilla de calabacín")
    assert code == 0 and out["saved"] == "recipes/tortilla-de-calabacin.yaml"
    _, shown = run(capsys, data_dir, "recipes", "show", "tortilla de calabacin")
    assert shown["recipe"]["items"] == ["huevo=120", "calabacín=150"]
    code, out = run(capsys, data_dir, "recipes", "save", "Plato que no existe")
    assert code == 2 and "saved menu" in out["message"]
    code, out = run(capsys, data_dir, "recipes", "remove", "Tortilla de calabacín")
    assert code == 0 and recipe_files(data_dir) == []
    code, out = run(capsys, data_dir, "recipes", "show", "Tortilla de calabacín")
    assert code == 2 and "not in the library" in out["message"]


def test_the_library_lives_in_the_gitignored_data_dir(data_dir):
    from pathlib import Path

    ignore = (Path(__file__).parent.parent.parent / ".gitignore").read_text()
    assert "data/*" in ignore  # recipes/ is under data/, never committed
