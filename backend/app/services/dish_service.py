from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.dish import DishORM
from app.models.dish_meal_role import DishMealRoleORM
from app.models.recipe import RecipeORM
from app.modules.domain.meal_role import MEAL_ROLE_VALUES
from app.services.dish_recipe_recalculation_service import (
    DishRecipeRecalculationService,
)


class DishService:
    def __init__(self, session: Session):
        self.session = session

    def list_dishes(self) -> list[DishORM]:
        statement = (
            select(DishORM)
            .options(
                joinedload(DishORM.recipe),
                selectinload(DishORM.meal_roles),
            )
            .order_by(DishORM.name)
        )
        return list(self.session.scalars(statement).all())

    def get_dish(self, dish_id: str) -> DishORM:
        statement = (
            select(DishORM)
            .options(
                joinedload(DishORM.recipe),
                selectinload(DishORM.meal_roles),
            )
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

    def replace_meal_roles(
        self,
        dish_id: str,
        roles: list[tuple[str, bool]],
    ) -> DishORM:
        requested_roles = self._validate_meal_roles(roles)
        dish = self.get_dish(dish_id)
        existing_roles = {assignment.role: assignment for assignment in dish.meal_roles}

        for role, current_assignment in existing_roles.items():
            if role not in requested_roles:
                dish.meal_roles.remove(current_assignment)

        for role, is_repeatable in requested_roles.items():
            existing_assignment = existing_roles.get(role)
            if existing_assignment is None:
                dish.meal_roles.append(
                    DishMealRoleORM(
                        dish_id=dish.id,
                        role=role,
                        is_repeatable=is_repeatable,
                    )
                )
            else:
                existing_assignment.is_repeatable = is_repeatable

        self._commit()
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

    @staticmethod
    def _validate_meal_roles(roles: list[tuple[str, bool]]) -> dict[str, bool]:
        normalized_roles: dict[str, bool] = {}
        for role, is_repeatable in roles:
            if role not in MEAL_ROLE_VALUES:
                raise ValueError(f"Unsupported meal role: {role}")
            if role in normalized_roles:
                raise ValueError("Meal roles must be unique")
            normalized_roles[role] = is_repeatable
        return normalized_roles

    def _commit(self) -> None:
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
