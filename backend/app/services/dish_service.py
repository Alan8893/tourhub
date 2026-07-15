from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.models.dish import DishORM
from app.models.recipe import RecipeORM
from app.services.dish_recipe_recalculation_service import (
    DishRecipeRecalculationService,
)


class DishService:
    def __init__(self, session: Session):
        self.session = session

    def list_dishes(self) -> list[DishORM]:
        statement = select(DishORM).options(joinedload(DishORM.recipe)).order_by(DishORM.name)
        return list(self.session.scalars(statement).all())

    def get_dish(self, dish_id: str) -> DishORM:
        statement = (
            select(DishORM)
            .options(joinedload(DishORM.recipe))
            .where(DishORM.id == dish_id)
        )
        dish = self.session.scalar(statement)
        if dish is None:
            raise LookupError("Dish not found")
        return dish

    def create_dish(self, name: str, recipe_id: str) -> DishORM:
        normalized_name = name.strip()
        self._ensure_name_available(normalized_name)
        recipe = self._get_selectable_recipe(recipe_id)
        dish = DishORM(id=str(uuid4()), name=normalized_name, recipe_id=recipe.id)
        self.session.add(dish)
        self._commit()
        return self.get_dish(dish.id)

    def update_dish(self, dish_id: str, name: str, recipe_id: str) -> DishORM:
        dish = self.get_dish(dish_id)
        normalized_name = name.strip()
        self._ensure_name_available(normalized_name, exclude_id=dish_id)
        recipe = self._get_selectable_recipe(recipe_id)
        recipe_changed = dish.recipe_id != recipe.id
        dish.name = normalized_name
        dish.recipe_id = recipe.id

        try:
            self.session.flush()
            if recipe_changed:
                self.session.expire(dish, ["recipe"])
                DishRecipeRecalculationService(
                    self.session
                ).refresh_affected_meal_plans(dish_id)
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        return self.get_dish(dish.id)

    def _get_selectable_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self.session.get(RecipeORM, recipe_id)
        if recipe is None:
            raise LookupError("Recipe not found")
        if recipe.is_archived:
            raise ValueError("Archived recipe cannot be assigned to a dish")
        return recipe

    def _ensure_name_available(self, name: str, exclude_id: str | None = None) -> None:
        statement = select(DishORM).where(DishORM.name == name)
        existing = self.session.scalar(statement)
        if existing is not None and existing.id != exclude_id:
            raise ValueError("Dish name must be unique")

    def _commit(self) -> None:
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
