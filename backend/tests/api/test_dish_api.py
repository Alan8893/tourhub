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
