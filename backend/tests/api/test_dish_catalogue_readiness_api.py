def _create_dish(client, name: str) -> tuple[str, str]:
    recipe_response = client.post(
        "/api/v1/recipes",
        json={"name": f"Рецепт: {name}"},
    )
    assert recipe_response.status_code == 201
    recipe_id = recipe_response.json()["id"]

    dish_response = client.post(
        "/api/v1/dishes",
        json={"name": name, "recipe_id": recipe_id},
    )
    assert dish_response.status_code == 201
    return dish_response.json()["id"], recipe_id


def _replace_roles(client, dish_id: str, roles: list[dict]) -> None:
    response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={"roles": roles},
    )
    assert response.status_code == 200


def _coverage_by_key(payload: dict) -> dict[tuple[str, str], dict]:
    return {
        (item["meal_type"], item["role"]): item
        for item in payload["coverage"]
    }


def test_empty_catalogue_is_not_ready(client):
    response = client.get("/api/v1/dishes/catalogue-readiness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ready"] is False
    assert payload["active_dish_count"] == 0
    assert payload["classified_dish_count"] == 0
    assert payload["unclassified_dish_count"] == 0
    assert [
        (item["meal_type"], item["role"], item["required"])
        for item in payload["coverage"]
    ] == [
        ("breakfast", "main", True),
        ("breakfast", "addition", False),
        ("breakfast", "drink", False),
        ("snack", "snack", True),
        ("lunch", "main", True),
        ("lunch", "addition", False),
        ("lunch", "drink", False),
        ("dinner", "main", True),
        ("dinner", "addition", False),
        ("dinner", "drink", False),
    ]
    assert all(item["candidate_count"] == 0 for item in payload["coverage"])
    assert all(item["minimum_required"] == 1 for item in payload["coverage"])


def test_required_coverage_makes_catalogue_ready_without_optional_roles(client):
    main_dish_id, _ = _create_dish(client, "Основное универсальное")
    snack_dish_id, _ = _create_dish(client, "Перекус")
    _create_dish(client, "Без классификации")
    archived_dish_id, archived_recipe_id = _create_dish(client, "Архивное блюдо")

    _replace_roles(
        client,
        main_dish_id,
        [
            {
                "role": "main",
                "is_repeatable": False,
                "allowed_meal_types": ["breakfast", "lunch", "dinner"],
            }
        ],
    )
    _replace_roles(
        client,
        snack_dish_id,
        [
            {
                "role": "snack",
                "is_repeatable": False,
                "allowed_meal_types": ["snack"],
            }
        ],
    )
    _replace_roles(
        client,
        archived_dish_id,
        [
            {
                "role": "main",
                "is_repeatable": False,
                "allowed_meal_types": ["breakfast", "lunch", "dinner"],
            },
            {
                "role": "addition",
                "is_repeatable": True,
                "allowed_meal_types": ["breakfast", "lunch", "dinner"],
            },
            {
                "role": "drink",
                "is_repeatable": True,
                "allowed_meal_types": ["breakfast", "lunch", "dinner"],
            },
        ],
    )
    assert client.post(
        f"/api/v1/recipes/{archived_recipe_id}/archive"
    ).status_code == 200

    response = client.get("/api/v1/dishes/catalogue-readiness")

    assert response.status_code == 200
    payload = response.json()
    assert payload["ready"] is True
    assert payload["active_dish_count"] == 3
    assert payload["classified_dish_count"] == 2
    assert payload["unclassified_dish_count"] == 1

    coverage = _coverage_by_key(payload)
    for key in [
        ("breakfast", "main"),
        ("snack", "snack"),
        ("lunch", "main"),
        ("dinner", "main"),
    ]:
        assert coverage[key]["required"] is True
        assert coverage[key]["candidate_count"] == 1
        assert coverage[key]["ready"] is True

    for meal_type in ["breakfast", "lunch", "dinner"]:
        for role in ["addition", "drink"]:
            assert coverage[(meal_type, role)]["required"] is False
            assert coverage[(meal_type, role)]["candidate_count"] == 0
            assert coverage[(meal_type, role)]["ready"] is False


def test_partial_required_coverage_reports_missing_meal_types(client):
    breakfast_dish_id, _ = _create_dish(client, "Каша")
    _replace_roles(
        client,
        breakfast_dish_id,
        [
            {
                "role": "main",
                "is_repeatable": False,
                "allowed_meal_types": ["breakfast"],
            }
        ],
    )

    payload = client.get("/api/v1/dishes/catalogue-readiness").json()
    coverage = _coverage_by_key(payload)

    assert payload["ready"] is False
    assert coverage[("breakfast", "main")]["ready"] is True
    assert coverage[("snack", "snack")]["ready"] is False
    assert coverage[("lunch", "main")]["ready"] is False
    assert coverage[("dinner", "main")]["ready"] is False
