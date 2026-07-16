import pytest
from sqlalchemy import select

from app.models.recipe import RecipeORM
from app.models.recipe_equipment_requirement import RecipeEquipmentRequirementORM
from app.services.recipe_equipment_service import RecipeEquipmentService


class FailingRecipeEquipmentRefresh:
    def refresh_affected_meal_plans(self, recipe_id: str) -> None:
        raise RuntimeError(f"refresh failed for {recipe_id}")


def test_recipe_requirement_change_rolls_back_when_refresh_fails(db_session):
    recipe = RecipeORM(id="rollback-recipe", name="Rollback recipe")
    db_session.add(recipe)
    db_session.commit()

    service = RecipeEquipmentService(db_session, FailingRecipeEquipmentRefresh())

    with pytest.raises(RuntimeError, match="refresh failed"):
        service.add(recipe.id, equipment_name="Pot", quantity=2)

    statement = select(RecipeEquipmentRequirementORM).where(
        RecipeEquipmentRequirementORM.recipe_id == recipe.id
    )
    assert db_session.scalar(statement) is None
