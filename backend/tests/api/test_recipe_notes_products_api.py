from app.models.recipe import RecipeORM


def test_create_product_and_reject_duplicate_name(client):
    payload = {
        "name": "Сушёные овощи",
        "category": "Овощи",
        "unit": "gram",
        "package_size": 200,
    }

    created = client.post("/api/v1/products", json=payload)

    assert created.status_code == 201
    assert created.json()["name"] == "Сушёные овощи"
    assert created.json()["package_size"] == 200

    duplicate = client.post("/api/v1/products", json=payload)

    assert duplicate.status_code == 409
    assert duplicate.json()["error"] == "Product name already exists"


def test_update_product_preserves_recipe_component_amount_and_unit(client):
    created = client.post(
        "/api/v1/products",
        json={
            "name": "Крупа тестовая",
            "category": "Крупы",
            "unit": "gram",
            "package_size": 500,
        },
    )
    assert created.status_code == 201
    product_id = created.json()["id"]

    recipe = client.post("/api/v1/recipes", json={"name": "Тестовый рецепт продукта"})
    assert recipe.status_code == 201
    recipe_id = recipe.json()["id"]
    component = client.post(
        f"/api/v1/recipes/{recipe_id}/components",
        json={
            "product_id": product_id,
            "component_type": "base",
            "amount": 75,
            "unit": "gram",
            "calculation_type": "per_person",
            "people_count": None,
        },
    )
    assert component.status_code == 201

    updated = client.put(
        f"/api/v1/products/{product_id}",
        json={
            "name": "Крупа обновлённая",
            "category": "Бакалея",
            "unit": "package",
            "package_size": 900,
        },
    )

    assert updated.status_code == 200
    assert updated.json() == {
        "id": product_id,
        "name": "Крупа обновлённая",
        "category": "Бакалея",
        "unit": "package",
        "package_size": 900,
    }

    detail = client.get(f"/api/v1/recipes/{recipe_id}")
    assert detail.status_code == 200
    persisted_component = detail.json()["components"][0]
    assert persisted_component["amount"] == 75
    assert persisted_component["unit"] == "gram"
    assert persisted_component["product"]["name"] == "Крупа обновлённая"
    assert persisted_component["product"]["unit"] == "package"
    assert persisted_component["product"]["package_size"] == 900


def test_update_product_rejects_duplicate_prohibited_and_missing_targets(client):
    first = client.post(
        "/api/v1/products",
        json={"name": "Первый продукт", "category": None, "unit": "gram", "package_size": None},
    ).json()
    second = client.post(
        "/api/v1/products",
        json={"name": "Второй продукт", "category": None, "unit": "gram", "package_size": None},
    ).json()

    duplicate = client.put(
        f"/api/v1/products/{first['id']}",
        json={
            "name": second["name"],
            "category": None,
            "unit": "gram",
            "package_size": None,
        },
    )
    assert duplicate.status_code == 409
    assert duplicate.json()["error"] == "Product name already exists"

    prohibited = client.put(
        f"/api/v1/products/{first['id']}",
        json={
            "name": "Вино красное",
            "category": "Напитки",
            "unit": "liter",
            "package_size": 1,
        },
    )
    assert prohibited.status_code == 422

    missing = client.put(
        "/api/v1/products/missing-product",
        json={
            "name": "Неизвестный продукт",
            "category": None,
            "unit": "gram",
            "package_size": None,
        },
    )
    assert missing.status_code == 404
    assert missing.json()["error"] == "Product not found"


def test_recipe_note_create_update_delete_workflow(client, db_session):
    recipe = RecipeORM(id="recipe-notes", name="Суп с заметками")
    db_session.add(recipe)
    db_session.commit()

    created = client.post(
        "/api/v1/recipes/recipe-notes/notes",
        json={
            "type": "cooking_tip",
            "text": "Добавить воду постепенно.",
            "priority": 20,
        },
    )

    assert created.status_code == 201
    note_id = created.json()["id"]

    updated = client.put(
        f"/api/v1/recipes/recipe-notes/notes/{note_id}",
        json={
            "type": "expedition_tip",
            "text": "Воду заранее нагреть.",
            "priority": 5,
        },
    )

    assert updated.status_code == 200
    assert updated.json()["type"] == "expedition_tip"
    assert updated.json()["text"] == "Воду заранее нагреть."
    assert updated.json()["priority"] == 5

    listed = client.get("/api/v1/recipes/recipe-notes/notes")

    assert listed.status_code == 200
    assert [item["id"] for item in listed.json()["items"]] == [note_id]

    deleted = client.delete(f"/api/v1/recipes/recipe-notes/notes/{note_id}")

    assert deleted.status_code == 204
    assert client.get("/api/v1/recipes/recipe-notes/notes").json()["items"] == []


def test_recipe_note_rejects_unknown_type(client, db_session):
    db_session.add(RecipeORM(id="recipe-invalid-note", name="Рецепт"))
    db_session.commit()

    response = client.post(
        "/api/v1/recipes/recipe-invalid-note/notes",
        json={"type": "unknown", "text": "Текст", "priority": 0},
    )

    assert response.status_code == 422
    assert response.json()["error"] == "Validation Error"
