def _create_published_club_recipe(client, name: str) -> str:
    create_response = client.post("/api/v1/recipes", json={"name": name})
    assert create_response.status_code == 201
    recipe_id = create_response.json()["id"]
    assert client.post(f"/api/v1/recipes/{recipe_id}/submit").status_code == 200
    publish_response = client.post(f"/api/v1/recipes/{recipe_id}/publish")
    assert publish_response.status_code == 200
    assert publish_response.json()["scope"] == "club"
    assert publish_response.json()["lifecycle_status"] == "published"
    return recipe_id


def _publication_created_dish(client, name: str = "Тестовое блюдо") -> str:
    recipe_id = _create_published_club_recipe(client, name)
    response = client.get("/api/v1/dishes")
    assert response.status_code == 200
    dish = next(
        item
        for item in response.json()["items"]
        if item["recipe"]["id"] == recipe_id
    )
    assert dish["name"] == name
    assert dish["meal_roles"] == []
    assert dish["recipe"]["is_default"] is True
    assert [recipe["id"] for recipe in dish["recipes"]] == [recipe_id]
    return dish["id"]


def test_dish_catalog_create_update_and_list(client):
    first_recipe_id = _create_published_club_recipe(client, "Каша базовая")
    second_recipe_id = _create_published_club_recipe(client, "Каша улучшенная")

    create_response = client.post(
        "/api/v1/dishes",
        json={
            "name": "Гречневая каша",
            "recipe_id": first_recipe_id,
            "recipe_ids": [first_recipe_id, second_recipe_id],
        },
    )
    assert create_response.status_code == 201
    dish_id = create_response.json()["id"]
    assert create_response.json()["recipe"]["name"] == "Каша базовая"
    assert create_response.json()["recipe"]["scope"] == "club"
    assert create_response.json()["recipe"]["is_default"] is True
    assert [recipe["name"] for recipe in create_response.json()["recipes"]] == [
        "Каша базовая",
        "Каша улучшенная",
    ]
    assert create_response.json()["meal_roles"] == []

    update_response = client.put(
        f"/api/v1/dishes/{dish_id}",
        json={
            "name": "Каша с грибами",
            "recipe_id": second_recipe_id,
            "recipe_ids": [second_recipe_id, first_recipe_id],
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Каша с грибами"
    assert update_response.json()["recipe"]["name"] == "Каша улучшенная"
    assert update_response.json()["recipe"]["is_default"] is True

    list_response = client.get("/api/v1/dishes")
    assert list_response.status_code == 200
    listed = next(
        item for item in list_response.json()["items"] if item["id"] == dish_id
    )
    assert listed == update_response.json()

    detail_response = client.get(f"/api/v1/dishes/{dish_id}")
    assert detail_response.status_code == 200
    assert detail_response.json() == update_response.json()


def test_dish_meal_roles_are_replaced_and_exposed(client):
    dish_id = _publication_created_dish(client, "Бутерброды")

    first_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={
            "roles": [
                {
                    "role": "snack",
                    "is_repeatable": False,
                    "allowed_meal_types": ["snack"],
                },
                {
                    "role": "addition",
                    "is_repeatable": True,
                    "allowed_meal_types": ["dinner", "breakfast", "lunch"],
                },
            ]
        },
    )

    assert first_response.status_code == 200
    assert first_response.json()["meal_roles"] == [
        {
            "role": "addition",
            "is_repeatable": True,
            "allowed_meal_types": ["breakfast", "lunch", "dinner"],
        },
        {
            "role": "snack",
            "is_repeatable": False,
            "allowed_meal_types": ["snack"],
        },
    ]

    replacement_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={
            "roles": [
                {
                    "role": "main",
                    "is_repeatable": False,
                    "allowed_meal_types": ["breakfast"],
                }
            ]
        },
    )

    assert replacement_response.status_code == 200
    expected_roles = [
        {
            "role": "main",
            "is_repeatable": False,
            "allowed_meal_types": ["breakfast"],
        }
    ]
    assert replacement_response.json()["meal_roles"] == expected_roles
    assert client.get(f"/api/v1/dishes/{dish_id}").json()["meal_roles"] == expected_roles
    listed = next(
        item
        for item in client.get("/api/v1/dishes").json()["items"]
        if item["id"] == dish_id
    )
    assert listed["meal_roles"] == expected_roles

    clear_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={"roles": []},
    )
    assert clear_response.status_code == 200
    assert clear_response.json()["meal_roles"] == []


def test_duplicate_dish_meal_roles_are_rejected_atomically(client):
    dish_id = _publication_created_dish(client, "Чай")
    initial_roles = [
        {
            "role": "drink",
            "is_repeatable": True,
            "allowed_meal_types": ["breakfast", "lunch", "dinner"],
        }
    ]
    initial_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={"roles": initial_roles},
    )
    assert initial_response.status_code == 200

    duplicate_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={
            "roles": [
                {
                    "role": "snack",
                    "is_repeatable": False,
                    "allowed_meal_types": ["snack"],
                },
                {
                    "role": "snack",
                    "is_repeatable": True,
                    "allowed_meal_types": ["snack"],
                },
            ]
        },
    )

    assert duplicate_response.status_code == 422
    assert duplicate_response.json()["error"] == "Meal roles must be unique"
    assert client.get(f"/api/v1/dishes/{dish_id}").json()["meal_roles"] == initial_roles


def test_meal_type_compatibility_is_validated_atomically(client):
    dish_id = _publication_created_dish(client, "Овсяная каша")
    initial_roles = [
        {
            "role": "main",
            "is_repeatable": False,
            "allowed_meal_types": ["breakfast"],
        }
    ]
    assert client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={"roles": initial_roles},
    ).status_code == 200

    duplicate_meal_type_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={
            "roles": [
                {
                    "role": "main",
                    "is_repeatable": False,
                    "allowed_meal_types": ["breakfast", "breakfast"],
                }
            ]
        },
    )
    assert duplicate_meal_type_response.status_code == 422
    assert duplicate_meal_type_response.json()["error"] == (
        "Meal types must be unique within each meal role"
    )

    incompatible_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={
            "roles": [
                {
                    "role": "main",
                    "is_repeatable": False,
                    "allowed_meal_types": ["snack"],
                }
            ]
        },
    )
    assert incompatible_response.status_code == 422
    assert incompatible_response.json()["error"] == (
        "Meal role main is incompatible with meal type snack"
    )

    empty_compatibility_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={
            "roles": [
                {
                    "role": "main",
                    "is_repeatable": False,
                    "allowed_meal_types": [],
                }
            ]
        },
    )
    assert empty_compatibility_response.status_code == 422
    assert client.get(f"/api/v1/dishes/{dish_id}").json()["meal_roles"] == initial_roles


def test_invalid_or_unknown_dish_meal_roles_are_rejected(client):
    dish_id = _publication_created_dish(client, "Суп")

    invalid_role_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={
            "roles": [
                {
                    "role": "soup",
                    "is_repeatable": False,
                    "allowed_meal_types": ["lunch"],
                }
            ]
        },
    )
    assert invalid_role_response.status_code == 422

    invalid_meal_type_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={
            "roles": [
                {
                    "role": "main",
                    "is_repeatable": False,
                    "allowed_meal_types": ["brunch"],
                }
            ]
        },
    )
    assert invalid_meal_type_response.status_code == 422

    missing_dish_response = client.put(
        "/api/v1/dishes/unknown/meal-roles",
        json={"roles": []},
    )
    assert missing_dish_response.status_code == 404
    assert missing_dish_response.json()["error"] == "Dish not found"


def test_dish_name_must_be_unique(client):
    recipe_id = _create_published_club_recipe(client, "Суп рецепт")
    payload = {"name": "Суп", "recipe_id": recipe_id}

    assert client.post("/api/v1/dishes", json=payload).status_code == 201
    response = client.post("/api/v1/dishes", json=payload)

    assert response.status_code == 409
    assert response.json()["error"] == "Dish name must be unique"


def test_archived_recipe_cannot_be_newly_assigned(client):
    recipe_id = _create_published_club_recipe(client, "Архивный рецепт")
    auto_dish = next(
        item
        for item in client.get("/api/v1/dishes").json()["items"]
        if item["recipe"]["id"] == recipe_id
    )

    assert client.post(f"/api/v1/recipes/{recipe_id}/archive").status_code == 200

    detail_response = client.get(f"/api/v1/dishes/{auto_dish['id']}")
    assert detail_response.status_code == 200
    assert detail_response.json()["recipe"]["is_archived"] is True

    create_response = client.post(
        "/api/v1/dishes",
        json={"name": "Новое блюдо", "recipe_id": recipe_id},
    )
    assert create_response.status_code == 422
    assert create_response.json()["error"] == (
        "Dish default must be an active published club recipe"
    )


def test_dish_endpoints_return_not_found(client):
    assert client.get("/api/v1/dishes/unknown").status_code == 404
    response = client.post(
        "/api/v1/dishes",
        json={"name": "Без рецепта", "recipe_id": "missing"},
    )
    assert response.status_code == 404
    assert response.json()["error"] == "Recipe not found"
