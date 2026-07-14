from app.models.recipe import RecipeORM
from app.models.recipe_note import RecipeNoteORM


def test_get_recipe_notes(client, db_session):
    recipe = RecipeORM(id="recipe-1", name="Solyanka")
    note_low = RecipeNoteORM(
        id="note-1",
        recipe_id="recipe-1",
        text="Add hot pepper if needed.",
        priority=10,
    )
    note_high = RecipeNoteORM(
        id="note-2",
        recipe_id="recipe-1",
        text="Serve with lemon.",
        priority=20,
    )

    db_session.add(recipe)
    db_session.add(note_low)
    db_session.add(note_high)
    db_session.commit()

    response = client.get("/api/v1/recipes/recipe-1/notes")

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 2
    assert data["items"][0]["priority"] == 10
    assert data["items"][1]["priority"] == 20
    assert data["items"][0]["text"] == "Add hot pepper if needed."
    assert data["items"][1]["text"] == "Serve with lemon."
    assert data["items"][0]["recipe_id"] == "recipe-1"
    assert data["items"][1]["recipe_id"] == "recipe-1"


def test_get_recipe_notes_not_found(client):
    response = client.get("/api/v1/recipes/unknown/notes")

    assert response.status_code == 404
    assert response.json()["detail"] == "Recipe not found: unknown"
