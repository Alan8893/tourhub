def _create_dish(client, name: str = "Тестовое блюдо") -> str:
    recipe_id = client.post(
        "/api/v1/recipes",
        json={"name": f"Рецепт: {name}"},
    ).json()["id"]
    response = client.post(
        "/api/v1/dishes",
        json={"name": name, "recipe_id": recipe_id},
    )
    assert response.status_code == 201
    assert response.json()["meal_roles"] == []
    return response.json()["id"]


def test_dish_catalog_create_update_and_list(client):
    first_recipe = client.post("/api/v1/recipes", json={"name": "Каша базовая"})
    second_recipe = client.post("/api/v1/recipes", json={"name": "Каша улучшенная"})
    first_recipe_id = first_recipe.json()["id"]
    second_recipe_id = second_recipe.json()["id"]

    create_response = client.post(
        "/api/v1/dishes",
        json={"name": "Гречневая каша", "recipe_id": first_recipe_id},
    )
    assert create_response.status_code == 201
    dish_id = create_response.json()["id"]
    assert create_response.json()["recipe"]["name"] == "Каша базовая"
    assert create_response.json()["meal_roles"] == []

    update_response = client.put(
        f"/api/v1/dishes/{dish_id}",
        json={"name": "Каша с грибами", "recipe_id": second_recipe_id},
    )
    assert update_response.status_code == 200
    assert update_response.json()["name"] == "Каша с грибами"
    assert update_response.json()["recipe"]["name"] == "Каша улучшенная"

    list_response = client.get("/api/v1/dishes")
    assert list_response.status_code == 200
    assert list_response.json()["items"] == [update_response.json()]

    detail_response = client.get(f"/api/v1/dishes/{dish_id}")
    assert detail_response.status_code == 200
    assert detail_response.json() == update_response.json()


def test_dish_meal_roles_are_replaced_and_exposed(client):
    dish_id = _create_dish(client, "Бутерброды")

    first_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={
            "roles": [
                {"role": "snack", "is_repeatable": False},
                {"role": "addition", "is_repeatable": True},
            ]
        },
    )

    assert first_response.status_code == 200
    assert first_response.json()["meal_roles"] == [
        {"role": "addition", "is_repeatable": True},
        {"role": "snack", "is_repeatable": False},
    ]

    replacement_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={"roles": [{"role": "main", "is_repeatable": False}]},
    )

    assert replacement_response.status_code == 200
    assert replacement_response.json()["meal_roles"] == [
        {"role": "main", "is_repeatable": False}
    ]
    assert client.get(f"/api/v1/dishes/{dish_id}").json()["meal_roles"] == [
        {"role": "main", "is_repeatable": False}
    ]
    assert client.get("/api/v1/dishes").json()["items"][0]["meal_roles"] == [
        {"role": "main", "is_repeatable": False}
    ]

    clear_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={"roles": []},
    )
    assert clear_response.status_code == 200
    assert clear_response.json()["meal_roles"] == []


def test_duplicate_dish_meal_roles_are_rejected_atomically(client):
    dish_id = _create_dish(client, "Чай")
    initial_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={"roles": [{"role": "drink", "is_repeatable": True}]},
    )
    assert initial_response.status_code == 200

    duplicate_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={
            "roles": [
                {"role": "snack", "is_repeatable": False},
                {"role": "snack", "is_repeatable": True},
            ]
        },
    )

    assert duplicate_response.status_code == 422
    assert duplicate_response.json()["error"] == "Meal roles must be unique"
    assert client.get(f"/api/v1/dishes/{dish_id}").json()["meal_roles"] == [
        {"role": "drink", "is_repeatable": True}
    ]


def test_invalid_or_unknown_dish_meal_roles_are_rejected(client):
    dish_id = _create_dish(client, "Суп")

    invalid_role_response = client.put(
        f"/api/v1/dishes/{dish_id}/meal-roles",
        json={"roles": [{"role": "soup", "is_repeatable": False}]},
    )
    assert invalid_role_response.status_code == 422

    missing_dish_response = client.put(
        "/api/v1/dishes/unknown/meal-roles",
        json={"roles": []},
    )
    assert missing_dish_response.status_code == 404
    assert missing_dish_response.json()["error"] == "Dish not found"


def test_dish_name_must_be_unique(client):
    recipe_id = client.post("/api/v1/recipes", json={"name": "Суп рецепт"}).json()["id"]
    payload = {"name": "Суп", "recipe_id": recipe_id}

    assert client.post("/api/v1/dishes", json=payload).status_code == 201
    response = client.post("/api/v1/dishes", json=payload)

    assert response.status_code == 409
    assert response.json()["error"] == "Dish name must be unique"


def test_archived_recipe_cannot_be_newly_assigned(client):
    recipe_id = client.post("/api/v1/recipes", json={"name": "Архивный рецепт"}).json()["id"]
    dish_response = client.post(
        "/api/v1/dishes",
        json={"name": "Историческое блюдо", "recipe_id": recipe_id},
    )
    assert dish_response.status_code == 201
    dish_id = dish_response.json()["id"]

    assert client.post(f"/api/v1/recipes/{recipe_id}/archive").status_code == 200

    detail_response = client.get(f"/api/v1/dishes/{dish_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["recipe"]["is_archived"] is True

    create_response = client.post(
        "/api/v1/dishes",
        json={"name": "Новое блюдо", "recipe_id": recipe_id},
    )
    assert create_response.status_code == 422
    assert create_response.json()["error"] == "Archived recipe cannot be assigned to a dish"


def test_dish_endpoints_return_not_found(client):
    assert client.get("/api/v1/dishes/unknown").status_code == 404
    response = client.post(
        "/api/v1/dishes",
        json={"name": "Без рецепта", "recipe_id": "missing"},
    )
    assert response.status_code == 404
    assert response.json()["error"] == "Recipe not found"
