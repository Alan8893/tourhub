from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM
from app.models.recipe_note import RecipeNoteORM


def test_list_recipes_returns_sorted_summary(client, db_session):
    first = RecipeORM(id="recipe-b", name="Борщ")
    second = RecipeORM(id="recipe-a", name="Каша")
    product = ProductORM(
        id="product-1",
        name="Гречка",
        category="Крупы",
        unit="gram",
        package_size=800,
    )
    component = RecipeComponentORM(
        id="component-1",
        recipe_id="recipe-a",
        product_id="product-1",
        component_type="base",
        amount=80,
        unit="gram",
        calculation_type="per_person",
    )
    note = RecipeNoteORM(
        id="note-1",
        recipe_id="recipe-a",
        type="cooking_tip",
        text="Промыть крупу.",
        priority=10,
    )

    db_session.add_all([first, second, product, component, note])
    db_session.commit()

    response = client.get("/api/v1/recipes")

    assert response.status_code == 200
    assert response.json() == {
        "items": [
            {
                "id": "recipe-b",
                "name": "Борщ",
                "component_count": 0,
                "note_count": 0,
            },
            {
                "id": "recipe-a",
                "name": "Каша",
                "component_count": 1,
                "note_count": 1,
            },
        ]
    }


def test_get_recipe_returns_components_products_and_notes(client, db_session):
    recipe = RecipeORM(id="recipe-1", name="Походная каша")
    product = ProductORM(
        id="product-1",
        name="Гречка",
        category="Крупы",
        unit="gram",
        package_size=800,
    )
    component = RecipeComponentORM(
        id="component-1",
        recipe_id="recipe-1",
        product_id="product-1",
        component_type="base",
        amount=80,
        unit="gram",
        calculation_type="per_person",
        people_count=None,
    )
    note = RecipeNoteORM(
        id="note-1",
        recipe_id="recipe-1",
        type="cooking_tip",
        text="Промыть крупу перед варкой.",
        priority=10,
    )

    db_session.add_all([recipe, product, component, note])
    db_session.commit()

    response = client.get("/api/v1/recipes/recipe-1")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == "recipe-1"
    assert data["name"] == "Походная каша"
    assert data["components"] == [
        {
            "id": "component-1",
            "component_type": "base",
            "amount": 80,
            "unit": "gram",
            "calculation_type": "per_person",
            "people_count": None,
            "product": {
                "id": "product-1",
                "name": "Гречка",
                "category": "Крупы",
                "unit": "gram",
                "package_size": 800,
            },
        }
    ]
    assert len(data["notes"]) == 1
    assert data["notes"][0]["id"] == "note-1"
    assert data["notes"][0]["text"] == "Промыть крупу перед варкой."


def test_get_recipe_returns_404_for_unknown_recipe(client):
    response = client.get("/api/v1/recipes/unknown")

    assert response.status_code == 404
    assert response.json()["error"] == "Recipe not found"
