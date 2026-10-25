import json
from datetime import date

import pytest
import yaml

from coach import catalogue, mealplan
from coach.cli import main
from coach.profile import Profile, save_profile

TODAY = "2026-10-25"
SKYR = "Skyr de prueba"
# Synthetic catalogue product: 2,000 kcal of it alone meets every floor of a 2,000 kcal day.
TEST_FOOD = catalogue.CatalogueProduct(
    barcode="8400000000017",
    product_name="Comida de prueba",
    brand="Marca Prueba",
    chain="Mercadona",
    per="100 g",
    kcal=100,
    protein_g=8,
    carbs_g=12,
    fat_g=2.5,
    fibre_g=2,
    allergens=(),
    url="https://world.openfoodfacts.org/product/8400000000017",
    fetched_on=date(2026, 10, 25),
)


SKYR_PRODUCT = catalogue.CatalogueProduct(
    barcode="8400000000024",
    product_name=SKYR,
    brand="Marca Prueba",
    chain="Eroski",
    per="100 g",
    kcal=50,
    protein_g=8,
    carbs_g=4.1,
    fat_g=0.2,
    fibre_g=None,
    allergens=(),
    url="https://world.openfoodfacts.org/product/8400000000024",
    fetched_on=date(2026, 10, 25),
)


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
    catalogue.save([TEST_FOOD, SKYR_PRODUCT], tmp_path)
    return tmp_path


def day(when, *dishes):
    return {
        "date": when,
        "meals": [
            {
                "meal": "Comida",
                "dishes": [
                    {
                        "dish": name,
                        "source": "https://example.org/receta",
                        "steps": ["Calentar", "Servir"],
                        "seasoning": ["pimentón"],
                        "items": items,
                    }
                    for name, items in dishes
                ],
            }
        ],
    }


def three_days():
    return {
        "days": [
            day(
                date(2026, 10, 26),
                ("Plato A", ["Comida de prueba=1900"]),
                ("Lentejas", ["lentejas, cocidas=100"]),
            ),
            day(date(2026, 10, 27), ("Plato B", ["8400000000017=1960", f"{SKYR}=150"])),
            day(date(2026, 10, 28), ("Plato C", ["Comida de prueba=2040"])),
        ]
    }


def write(data_dir, draft, name="menu-draft.yaml"):
    path = data_dir / name
    path.write_text(yaml.safe_dump(draft, allow_unicode=True, sort_keys=False), encoding="utf-8")
    return path


def run(capsys, data_dir, *args):
    code = main(["--data-dir", str(data_dir), "--today", TODAY, *args, "--json"])
    return code, json.loads(capsys.readouterr().out)


def test_check_runs_the_menu_check_on_every_day(capsys, data_dir):
    path = write(data_dir, three_days())
    code, out = run(capsys, data_dir, "mealplan", "check", str(path), "--kcal", "2000")
    assert code == 0 and out["ok"] is True and out["repeats"] == []
    assert [d["date"] for d in out["days"]] == ["2026-10-26", "2026-10-27", "2026-10-28"]
    assert [d["totals"]["kcal"] for d in out["days"]] == [2016, 2035, 2040]
    assert all(d["ok"] and set(d["check"].values()) == {"ok"} for d in out["days"])
    # The skyr has no fibre value: listed, and the floor is still met without it.
    assert out["days"][1]["totals"]["missing"] == {"fibre_g": [SKYR]}
    _, single = run(
        capsys, data_dir, "menu", "--item", "8400000000017=1960", "--item", f"{SKYR}=150",
        "--targets", "--kcal", "2000",
    )  # fmt: skip
    assert single["totals"] == out["days"][1]["totals"] and out["targets"] == single["targets"]


def test_check_reports_a_day_that_fails(capsys, data_dir):
    draft = three_days()
    draft["days"][2]["meals"][0]["dishes"][0]["items"] = ["Comida de prueba=1500", "ñoquis=100"]
    _, out = run(
        capsys, data_dir, "mealplan", "check", str(write(data_dir, draft)), "--kcal", "2000"
    )
    assert out["ok"] is False
    assert out["days"][2]["check"]["kcal"] == "under"
    assert out["days"][2]["totals"]["unknown"] == ["ñoquis"]


@pytest.mark.parametrize("gap, repeated", [(6, True), (7, False)])
def test_a_dish_does_not_repeat_within_seven_days(capsys, data_dir, gap, repeated):
    first = date(2026, 10, 26)
    draft = {
        "days": [
            day(first, ("Plato A", ["Comida de prueba=2040"])),
            day(date.fromordinal(first.toordinal() + gap), ("plato a", ["Comida de prueba=2040"])),
        ]
    }
    _, out = run(
        capsys, data_dir, "mealplan", "check", str(write(data_dir, draft)), "--kcal", "2000"
    )
    assert bool(out["repeats"]) is repeated and out["ok"] is not repeated
    if repeated:
        assert out["repeats"] == [{"dish": "Plato A", "dates": ["2026-10-26", "2026-11-01"]}]


def test_save_writes_the_checked_plan(capsys, data_dir):
    path = write(data_dir, three_days())
    code, out = run(capsys, data_dir, "mealplan", "save", str(path), "--kcal", "2000")
    assert code == 0 and out["saved"] == "menus/2026-10-26.yaml"
    saved = yaml.safe_load((data_dir / "menus" / "2026-10-26.yaml").read_text(encoding="utf-8"))
    assert saved["saved_on"] == date(2026, 10, 25) and saved["targets"]["kcal"] == 2000
    assert saved["days"][0]["meals"][0]["dishes"][0]["steps"] == ["Calentar", "Servir"]
    assert saved["days"][0]["check"]["kcal"] == "ok" and saved["days"][0]["totals"]["kcal"] == 2016
    code, out = run(capsys, data_dir, "mealplan", "save", str(path), "--kcal", "2000")
    assert code == 2 and "--replace" in out["message"]
    code, _ = run(capsys, data_dir, "mealplan", "save", str(path), "--kcal", "2000", "--replace")
    assert code == 0
    _, listed = run(capsys, data_dir, "mealplan", "list")
    assert listed == {
        "menus": [{"file": "menus/2026-10-26.yaml", "start": "2026-10-26", "days": 3}]
    }


def test_save_refuses_a_plan_that_is_not_ok(capsys, data_dir):
    draft = three_days()
    draft["days"][1]["meals"][0]["dishes"][0]["items"] = ["Comida de prueba=500"]
    code, out = run(
        capsys, data_dir, "mealplan", "save", str(write(data_dir, draft)), "--kcal", "2000"
    )
    assert code == 2 and "2026-10-27" in out["message"]
    assert not (data_dir / "menus").exists()


@pytest.mark.parametrize(
    "draft, message",
    [
        ({}, "days"),
        ({"days": []}, "days"),
        ({"days": [{"date": "2026-10-26", "meals": []}]}, "date"),
        ({"days": [{"date": date(2026, 10, 26), "meals": [{"meal": "Comida"}]}]}, "dishes"),
        ({"days": [day(date(2026, 10, 26), ("A", []))]}, "items"),
        ({"days": [day(date(2026, 10, 26), ("A", ["arroz"]))]}, "NAME=GRAMS"),
        ({"days": [day(date(2026, 10, 26), ("", ["arroz=10"]))]}, "dish"),
        (
            {
                "days": [
                    day(date(2026, 10, 27), ("A", ["x=1"])),
                    day(date(2026, 10, 26), ("B", ["x=1"])),
                ]
            },
            "order",
        ),
    ],
)
def test_draft_is_validated(tmp_path, draft, message):
    with pytest.raises(ValueError, match=message):
        mealplan.load_draft(write(tmp_path, draft))


def test_shopping_list_sums_grams_by_chain(capsys, data_dir):
    run(capsys, data_dir, "mealplan", "save", str(write(data_dir, three_days())), "--kcal", "2000")
    code, out = run(capsys, data_dir, "shopping")
    assert code == 0 and out["menu"] == "menus/2026-10-26.yaml" and out["days"] == 3
    assert out["chains"] == {
        "Eroski": [{"name": SKYR, "grams": 150}],
        "Mercadona": [{"name": "Comida de prueba", "grams": 5900}],
        "any": [{"name": "lentejas, cocidas", "grams": 100}],
    }
    assert out["unknown"] == [] and "form" in out["note"]


def test_shopping_picks_the_newest_menu_or_the_one_named(capsys, data_dir):
    run(capsys, data_dir, "mealplan", "save", str(write(data_dir, three_days())), "--kcal", "2000")
    later = {"days": [day(date(2026, 11, 2), ("Plato D", ["Comida de prueba=2040"]))]}
    run(capsys, data_dir, "mealplan", "save", str(write(data_dir, later)), "--kcal", "2000")
    _, out = run(capsys, data_dir, "shopping")
    assert out["menu"] == "menus/2026-11-02.yaml"
    _, out = run(capsys, data_dir, "shopping", "menus/2026-10-26.yaml")
    assert out["days"] == 3


def test_shopping_without_a_saved_menu(capsys, data_dir):
    code, out = run(capsys, data_dir, "shopping")
    assert code == 2 and "mealplan save" in out["message"]


OAT_DRINK = catalogue.CatalogueProduct(
    barcode="8400000000031",
    product_name="Bebida de avena de prueba",
    brand="Marca Prueba",
    chain="Mercadona",
    per="100 ml",
    kcal=45,
    protein_g=0.6,
    carbs_g=7.4,
    fat_g=1.4,
    fibre_g=0.8,
    allergens=(),
    url="https://world.openfoodfacts.org/product/8400000000031",
    fetched_on=date(2026, 10, 25),
)


def test_shopping_keeps_millilitres_apart_from_grams(capsys, data_dir):
    """A liquid product is bought in ml, a solid in grams: never summed together."""
    catalogue.save([TEST_FOOD, OAT_DRINK], data_dir)
    draft = {
        "days": [
            day(
                date(2026, 10, 26),
                ("Plato A", ["Comida de prueba=1900", "Bebida de avena de prueba=250ml"]),
            ),
            day(date(2026, 10, 27), ("Plato B", ["Comida de prueba=1900", "8400000000031=250ml"])),
        ]
    }
    code, _ = run(
        capsys, data_dir, "mealplan", "save", str(write(data_dir, draft)), "--kcal", "2000"
    )
    assert code == 0
    _, shop = run(capsys, data_dir, "shopping")
    assert shop["chains"]["Mercadona"] == [
        {"name": "Bebida de avena de prueba", "ml": 500},
        {"name": "Comida de prueba", "grams": 3800},
    ]


def meal(name, *dishes, **flags):
    """A meal with (dish name, items[, extra dish keys]) tuples; flags such as tupper=True or
    free=True."""
    entry = {"meal": name} | flags
    if dishes:
        entry["dishes"] = [
            {"dish": d, "steps": ["Calentar"], "seasoning": [], "items": items}
            | (extra[0] if extra else {})
            for d, items, *extra in dishes
        ]
    return entry


def meals_day(when, *meals):
    return {"date": when, "meals": list(meals)}


def check(capsys, data_dir, draft, command="check"):
    return run(capsys, data_dir, "mealplan", command, str(write(data_dir, draft)), "--kcal", "2000")


# --- meals per day and lunchboxes (tupper) ---


def test_meals_vary_by_day_and_a_tupper_is_recorded(capsys, data_dir):
    draft = {
        "days": [
            meals_day(
                date(2026, 10, 26),
                meal("Desayuno", ("D1", ["Comida de prueba=400"])),
                meal("Comida", ("D2", ["Comida de prueba=800"]), tupper=True),
                meal("Merienda", ("D3", ["Comida de prueba=200"])),
                meal("Cena", ("D4", ["Comida de prueba=600"])),
            ),
            meals_day(
                date(2026, 10, 27),
                meal("Desayuno", ("D5", ["Comida de prueba=700"])),
                meal("Comida", ("D6", ["Comida de prueba=700"]), tupper=True),
                meal("Cena", ("D7", ["Comida de prueba=650"])),
            ),
        ]
    }
    code, out = check(capsys, data_dir, draft)
    assert code == 0 and out["ok"] is True
    assert [m["meal"] for m in out["days"][0]["meals"]] == [
        "Desayuno", "Comida", "Merienda", "Cena",
    ]  # fmt: skip
    assert [m["tupper"] for m in out["days"][0]["meals"]] == [False, True, False, False]
    assert len(out["days"][1]["meals"]) == 3 and out["days"][1]["meals"][1]["tupper"] is True
    assert out["days"][1]["meals"][1]["dishes"] == ["D6"]
    code, out = check(capsys, data_dir, draft, "save")
    saved = yaml.safe_load((data_dir / "menus" / "2026-10-26.yaml").read_text(encoding="utf-8"))
    assert saved["days"][0]["meals"][1]["tupper"] is True


@pytest.mark.parametrize("flag", ["tupper", "free"])
def test_meal_flags_must_be_true_or_false(data_dir, flag):
    draft = {
        "days": [meals_day(date(2026, 10, 26), meal("Comida", ("A", ["x=1"]), **{flag: "yes"}))]
    }
    with pytest.raises(ValueError, match=flag):
        mealplan.load_draft(write(data_dir, draft))


# --- free meal ---


def free_day(each, when=date(2026, 10, 26)):
    """Three planned meals of `each` grams of the test food (1 kcal per g) and a free dinner."""
    third = each
    return meals_day(
        when,
        meal("Desayuno", ("D1", [f"Comida de prueba={third}"])),
        meal("Comida", ("D2", [f"Comida de prueba={third}"])),
        meal("Merienda", ("D3", [f"Comida de prueba={third}"])),
        meal("Cena", free=True),
    )


def test_a_free_meal_replaces_one_and_reports_the_remaining_budget(capsys, data_dir):
    code, out = check(capsys, data_dir, {"days": [free_day(600)]})
    day_out = out["days"][0]
    assert code == 0 and out["ok"] is True and day_out["ok"] is True
    assert day_out["totals"]["kcal"] == 1800 and day_out["check"]["kcal"] == "ok"
    free = day_out["free_meal"]
    assert free["meals"] == ["Cena"] and free["planned_meals"] == 3
    assert free["share"] == 0.75 and free["budget"]["kcal"] == 200
    assert day_out["meals"][3] == {"meal": "Cena", "tupper": False, "free": True, "dishes": []}
    assert out["targets"]["kcal"] == 2000  # the full target, never reduced


def test_a_free_meal_never_hides_an_under_target_day(capsys, data_dir):
    # Planned meals must carry their equal share of the target (3 of 4 meals: 75%).
    _, out = check(capsys, data_dir, {"days": [free_day(400)]})
    assert out["ok"] is False and out["days"][0]["check"]["kcal"] == "under"
    # the note must not tell the client the share is met when the check says it is not
    assert "already carry" not in out["days"][0]["free_meal"]["note"]
    _, out = check(capsys, data_dir, {"days": [free_day(500)]})
    assert (
        out["days"][0]["check"]["kcal"] == "ok"
        and out["days"][0]["free_meal"]["budget"]["kcal"] == 500
    )


def test_a_free_meal_cannot_push_the_day_over_the_target(capsys, data_dir):
    _, out = check(capsys, data_dir, {"days": [free_day(660)]})  # 1,980 kcal: 20 left
    assert out["days"][0]["check"]["kcal"] == "ok"
    assert out["days"][0]["free_meal"]["budget"]["kcal"] == 20
    _, out = check(capsys, data_dir, {"days": [free_day(700)]})
    assert out["days"][0]["check"]["kcal"] == "over" and out["ok"] is False


def test_a_free_day_still_needs_its_share_of_protein(capsys, data_dir):
    # 190 g of olive oil: about 1,680 kcal and no protein: the kcal share is met, protein is not.
    draft = {
        "days": [
            meals_day(
                date(2026, 10, 26),
                meal("Desayuno", ("D1", ["aceite de oliva=60"])),
                meal("Comida", ("D2", ["aceite de oliva=70"])),
                meal("Merienda", ("D3", ["aceite de oliva=60"])),
                meal("Cena", free=True),
            )
        ]
    }
    _, out = check(capsys, data_dir, draft)
    checked = out["days"][0]["check"]
    assert checked["kcal"] == "ok" and checked["protein_g"] == "under" and out["ok"] is False
    assert out["days"][0]["free_meal"]["budget"]["protein_g"] > 0


def test_free_meal_rules_are_validated(data_dir):
    two = meals_day(
        date(2026, 10, 26),
        meal("Comida", ("A", ["Comida de prueba=1000"])),
        meal("Merienda", free=True),
        meal("Cena", free=True),
    )
    with pytest.raises(ValueError, match="one free meal"):
        mealplan.load_draft(write(data_dir, {"days": [two]}))
    only_free = meals_day(date(2026, 10, 26), meal("Cena", free=True))
    with pytest.raises(ValueError, match="planned meal"):
        mealplan.load_draft(write(data_dir, {"days": [only_free]}))
    with_dishes = meals_day(
        date(2026, 10, 26),
        meal("Comida", ("A", ["Comida de prueba=1000"])),
        meal("Cena", ("B", ["Comida de prueba=300"]), free=True),
    )
    with pytest.raises(ValueError, match="no dishes"):
        mealplan.load_draft(write(data_dir, {"days": [with_dishes]}))


def test_free_meal_is_saved_and_leaves_the_shopping_list_alone(capsys, data_dir):
    code, out = check(capsys, data_dir, {"days": [free_day(600)]}, "save")
    assert code == 0
    saved = yaml.safe_load((data_dir / "menus" / "2026-10-26.yaml").read_text(encoding="utf-8"))
    assert saved["days"][0]["free_meal"]["budget"]["kcal"] == 200
    assert saved["days"][0]["meals"][3] == {"meal": "Cena", "free": True}
    _, shop = run(capsys, data_dir, "shopping")
    assert shop["chains"]["Mercadona"] == [{"name": "Comida de prueba", "grams": 1800}]


def test_a_free_meal_is_refused_after_a_positive_eating_disorder_screen(capsys, data_dir):
    """nutrition.md "Refeeds and cheat meals": watch for loss-of-control eating."""
    from coach.profile import load_profile

    profile = load_profile(data_dir / "profile.yaml")
    profile.screening["scoff_positive"] = True
    save_profile(profile, data_dir / "profile.yaml")
    code, out = check(capsys, data_dir, {"days": [free_day(600)]})
    assert code == 2 and "free meal" in out["message"] and "eating-disorder" in out["message"]
    # the same plan without a free meal is still checked
    code, _ = check(capsys, data_dir, three_days())
    assert code == 0


# --- batches and repeated dishes (servings) ---

LENTILS = ["lentejas, cocidas=100", "Comida de prueba=1900"]


def oct_(d):
    return date(2026, 10, d) if d <= 31 else date(2026, 11, d - 31)


def lunch_days(*days_and_extras, name="Lentejas"):
    """One lunch per listed (day number, dish extras): the same dish every time. Day numbers
    above 31 run into November."""
    return {
        "days": [
            meals_day(oct_(d), meal("Comida", (name, LENTILS, extra)))
            for d, extra in days_and_extras
        ]
    }


def test_a_batch_dish_may_come_back_within_its_servings(capsys, data_dir):
    batch = {"servings": 3}
    code, out = check(capsys, data_dir, lunch_days((26, batch), (27, batch), (28, batch)))
    assert code == 0 and out["repeats"] == [] and out["ok"] is True
    # the same repeats without a batch mark are an accidental repeat, as before
    _, plain = check(capsys, data_dir, lunch_days((26, {}), (27, {}), (28, {})))
    assert plain["ok"] is False
    assert plain["repeats"] == [
        {"dish": "Lentejas", "dates": ["2026-10-26", "2026-10-27", "2026-10-28"]}
    ]


def test_a_batch_that_runs_out_is_a_repeat(capsys, data_dir):
    batch = {"servings": 2}
    _, out = check(capsys, data_dir, lunch_days((26, batch), (27, batch), (28, batch)))
    assert out["ok"] is False
    assert out["repeats"] == [{"dish": "Lentejas", "dates": ["2026-10-27", "2026-10-28"]}]


def test_a_new_batch_waits_a_week_after_the_last_serving(capsys, data_dir):
    batch = {"servings": 2}
    _, soon = check(capsys, data_dir, lunch_days((26, batch), (27, batch), (33, batch)))
    assert soon["repeats"] == [{"dish": "Lentejas", "dates": ["2026-10-27", "2026-11-02"]}]
    _, later = check(capsys, data_dir, lunch_days((26, batch), (27, batch), (34, batch)))
    assert later["repeats"] == [] and later["ok"] is True


def test_batch_servings_must_be_a_whole_number_of_one_or_more(data_dir):
    for bad in (0, -2, 2.5, "3", True):
        with pytest.raises(ValueError, match="servings"):
            mealplan.load_draft(write(data_dir, lunch_days((26, {"servings": bad}))))


def test_a_batch_dish_has_the_same_items_every_time(data_dir):
    draft = lunch_days((26, {"servings": 2}), (27, {"servings": 2}))
    draft["days"][1]["meals"][0]["dishes"][0]["items"] = ["lentejas, cocidas=150"]
    with pytest.raises(ValueError, match="same items"):
        mealplan.load_draft(write(data_dir, draft))


def test_a_simple_breakfast_repeats_on_purpose(capsys, data_dir):
    days = [
        meals_day(
            oct_(d),
            meal("Desayuno", ("Avena con fruta", ["Comida de prueba=400"], {"servings": 5})),
            meal("Comida", (f"Plato {d}", ["Comida de prueba=1600"])),
        )
        for d in (26, 27, 28, 29, 30)
    ]
    code, out = check(capsys, data_dir, {"days": days})
    assert code == 0 and out["repeats"] == [] and out["ok"] is True


def test_shopping_buys_a_batch_once_at_its_servings(capsys, data_dir):
    batch = {"servings": 3}
    code, _ = check(capsys, data_dir, lunch_days((26, batch), (27, batch)), "save")
    assert code == 0
    _, shop = run(capsys, data_dir, "shopping")
    # per serving: 100 g lentils and 1,900 g of the test food; cooked once for 3 servings
    assert shop["chains"]["any"] == [{"name": "lentejas, cocidas", "grams": 300}]
    assert shop["chains"]["Mercadona"] == [{"name": "Comida de prueba", "grams": 5700}]
    assert shop["batches"] == [
        {"dish": "Lentejas", "servings": 3, "dates": ["2026-10-26", "2026-10-27"], "left_over": 1}
    ]


def test_shopping_counts_a_plain_repeated_item_per_appearance(capsys, data_dir):
    check(capsys, data_dir, three_days(), "save")
    _, shop = run(capsys, data_dir, "shopping")
    assert shop["batches"] == []
    assert shop["chains"]["Mercadona"] == [{"name": "Comida de prueba", "grams": 5900}]


def test_shopping_leaves_out_the_pantry(capsys, data_dir):
    (data_dir / "tastes.yaml").write_text("pantry: [aceite de oliva, comida de prueba]\n")
    items = ["Comida de prueba=1800", "aceite de oliva=10", "lentejas, cocidas=100"]
    draft = {"days": [meals_day(date(2026, 10, 26), meal("Comida", ("A", items)))]}
    code, _ = check(capsys, data_dir, draft, "save")
    assert code == 0
    _, shop = run(capsys, data_dir, "shopping")
    assert shop["chains"] == {"any": [{"name": "lentejas, cocidas", "grams": 100}]}
    assert shop["pantry_skipped"] == ["aceite de oliva", "Comida de prueba"]


def test_tastes_set_pantry(capsys, data_dir):
    code, out = run(capsys, data_dir, "tastes", "set", "pantry", "aceite de oliva, sal")
    assert code == 0 and out["tastes"]["pantry"] == ["aceite de oliva", "sal"]
    assert "pantry" not in out["missing"]  # optional: never asked


# --- tastes cross-checked against the dishes ---


def with_tastes(data_dir, **fields):
    (data_dir / "tastes.yaml").write_text(yaml.safe_dump(fields, allow_unicode=True))


def tomato_day(*extra_items, dish="Plato A", seasoning=None, when=date(2026, 10, 26)):
    entry = meal("Comida", (dish, ["Comida de prueba=1985", *extra_items]))
    if seasoning is not None:
        entry["dishes"][0]["seasoning"] = seasoning
    return {"days": [meals_day(when, entry)]}


def flags(out):
    return [(f["kind"], f["where"], f["entry"], f["text"]) for f in out["taste_flags"]]


def test_a_disliked_food_is_flagged_in_the_items_but_does_not_block(capsys, data_dir):
    with_tastes(data_dir, disliked_foods=["tomate"])
    code, out = check(capsys, data_dir, tomato_day("tomate=100", "salsa de tomate=50"))
    assert code == 0 and out["ok"] is True  # a dislike warns, the client decides
    assert flags(out) == [
        ("disliked", "item", "tomate", "tomate"),
        ("disliked", "item", "tomate", "salsa de tomate"),
    ]
    assert (
        out["taste_flags"][0]["date"] == "2026-10-26" and out["taste_flags"][0]["dish"] == "Plato A"
    )


def test_a_narrower_dislike_does_not_flag_the_sauce(capsys, data_dir):
    with_tastes(data_dir, disliked_foods=["tomate crudo"])
    _, out = check(capsys, data_dir, tomato_day("tomate=100", "salsa de tomate=50"))
    assert flags(out) == [("disliked", "item", "tomate crudo", "tomate")]


def test_dish_names_and_seasoning_are_checked_too(capsys, data_dir):
    with_tastes(data_dir, disliked_foods=["cilantro", "anchoas"])
    draft = tomato_day(dish="Tacos con cilantro", seasoning=["pimienta", "cilantro fresco"])
    _, out = check(capsys, data_dir, draft)
    assert flags(out) == [
        ("disliked", "dish", "cilantro", "Tacos con cilantro"),
        ("disliked", "seasoning", "cilantro", "cilantro fresco"),
    ]


def test_an_untried_food_is_a_note_not_a_dislike(capsys, data_dir):
    with_tastes(data_dir, untried=["tomate"], disliked_foods=[])
    _, out = check(capsys, data_dir, tomato_day("tomate=100"))
    assert out["ok"] is True and flags(out) == [("untried", "item", "tomate", "tomate")]


def test_a_catalogue_product_is_matched_by_its_name_not_its_barcode(capsys, data_dir):
    with_tastes(data_dir, disliked_foods=["comida"])
    _, out = check(
        capsys,
        data_dir,
        {"days": [meals_day(date(2026, 10, 26), meal("C", ("A", ["8400000000017=2000"])))]},
    )
    assert flags(out) == [("disliked", "item", "comida", "8400000000017")]


def test_allergies_and_intolerances_block_the_plan(capsys, data_dir):
    with_tastes(data_dir, allergies=["tomate"], intolerances=["salsa de tomate"])
    code, out = check(capsys, data_dir, tomato_day("tomate=100", "salsa de tomate=50"))
    assert code == 0 and out["ok"] is False
    assert {k for k, *_ in flags(out)} == {"allergy", "intolerance"}
    code, out = check(capsys, data_dir, tomato_day("tomate=100"), "save")
    assert code == 2 and "allergy" in out["message"] and "tomate" in out["message"]
    assert not (data_dir / "menus").exists()


def test_a_never_again_dish_is_flagged(capsys, data_dir):
    path = data_dir / "tastes.yaml"
    path.write_text(
        "ratings:\n- {dish: plato a, rating: never_again, date: 2026-10-20}\n"
        "- {dish: Plato B, rating: loved, date: 2026-10-20}\n"
    )
    _, out = check(capsys, data_dir, tomato_day())
    assert flags(out) == [("never_again", "dish", "plato a", "Plato A")]


def test_without_tastes_nothing_is_flagged(capsys, data_dir):
    _, out = check(capsys, data_dir, tomato_day("tomate=100"))
    assert out["taste_flags"] == [] and out["ok"] is True


def test_save_keeps_the_flags_in_the_saved_plan(capsys, data_dir):
    with_tastes(data_dir, disliked_foods=["tomate"])
    code, out = check(capsys, data_dir, tomato_day("tomate=100"), "save")
    assert code == 0
    saved = yaml.safe_load((data_dir / "menus" / "2026-10-26.yaml").read_text(encoding="utf-8"))
    assert saved["days"][0]["taste_flags"][0]["entry"] == "tomate"


def test_tastes_set_untried(capsys, data_dir):
    code, out = run(capsys, data_dir, "tastes", "set", "untried", "sepia, pulpo")
    assert code == 0 and out["tastes"]["untried"] == ["sepia", "pulpo"]
    assert "untried" not in out["missing"]
