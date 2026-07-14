from app.models.recipe import RecipeORM


def test_create_recipe_note(client, db_session):
    recipe = RecipeORM(id="recipe-1", name="Solyanka")
    db_session.add(recipe)
    db_session.commit()

    response = client.post(
        "/api/v1/recipes/recipe-1/notes",
        json={
            "type": "cooking_tip",
            "text": "Add lemon at the end.",
            "priority": 100,
        },
    )

    assert response.status_code == 201

    data = response.json()
    assert data["recipe_id"] == "recipe-1"
    assert data["type"] == "cooking_tip"
    assert data["text"] == "Add lemon at the end."
    assert data["priority"] == 100
    assert "id" in data
    assert "created_at" in data


def test_create_recipe_note_not_found(client):
    response = client.post(
        "/api/v1/recipes/unknown/notes",
        json={
            "type": "cooking_tip",
            "text": "Add lemon at the end.",
            "priority": 100,
        },
    )

    assert response.status_code == 404

    data = response.json()
    assert "detail" in data or "error" in data
