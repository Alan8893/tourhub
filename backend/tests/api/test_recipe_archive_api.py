import pytest

from app.main import app
from app.models.dish import DishORM
from app.models.recipe import RecipeORM
from app.modules.api.recipe_router import get_recipe_command_service
from app.services.recipe_command_service import RecipeCommandService


def test_recipe_archive_restore_and_delete(client):
    create_response = client.post("/api/v1/recipes", json={"name": "Архивный суп"})
    assert create_response.status_code == 201
    recipe_id = create_response.json()["id"]
    assert create_response.json()["is_archived"] is False

    archive_response = client.post(f"/api/v1/recipes/{recipe_id}/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["is_archived"] is True

    active_list = client.get("/api/v1/recipes")
    assert active_list.status_code == 200
    assert active_list.json()["items"] == []

    archived_list = client.get("/api/v1/recipes?include_archived=true")
    assert archived_list.status_code == 200
    assert archived_list.json()["items"][0]["is_archived"] is True

    detail_response = client.get(f"/api/v1/recipes/{recipe_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["is_archived"] is True

    restore_response = client.post(f"/api/v1/recipes/{recipe_id}/restore")
    assert restore_response.status_code == 200
    assert restore_response.json()["is_archived"] is False

    delete_response = client.delete(f"/api/v1/recipes/{recipe_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/recipes/{recipe_id}").status_code == 404


def test_recipe_delete_is_blocked_when_used_by_dish(db_session):
    recipe = RecipeORM(id="recipe-linked", name="Связанный рецепт")
    dish = DishORM(id="dish-linked", name="Блюдо", recipe_id=recipe.id)
    db_session.add_all([recipe, dish])
    db_session.commit()

    service = RecipeCommandService(db_session)

    with pytest.raises(ValueError, match="Recipe is used by a dish"):
        service.delete_recipe(recipe.id)

    assert db_session.get(RecipeORM, recipe.id) is not None


def test_recipe_delete_conflict_is_exposed_by_api(client):
    class ConflictService:
        def delete_recipe(self, recipe_id: str) -> None:
            raise ValueError("Recipe is used by a dish and cannot be deleted")

    app.dependency_overrides[get_recipe_command_service] = ConflictService

    response = client.delete("/api/v1/recipes/recipe-linked")

    assert response.status_code == 409
    assert response.json()["error"] == "Recipe is used by a dish and cannot be deleted"
