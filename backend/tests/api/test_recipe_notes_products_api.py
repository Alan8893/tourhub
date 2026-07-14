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
