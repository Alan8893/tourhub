from sqlalchemy.orm import Session, joinedload

from app.models.dish import DishORM
from app.models.ingredient import IngredientORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM


class MealPlanRepository:
    """Repository for meal plan persistence."""

    def __init__(self, session: Session):
        self.session = session

    def add(self, meal_plan: MealPlanORM) -> None:
        self.session.add(meal_plan)

    def add_day(self, day: MealPlanDayORM) -> None:
        self.session.add(day)

    def add_item(self, item: MealPlanItemORM) -> None:
        self.session.add(item)

    def add_slot(self, slot: MealSlotORM) -> None:
        self.session.add(slot)

    def add_slot_dish(self, slot_dish: MealSlotDishORM) -> None:
        self.session.add(slot_dish)

    def flush(self) -> None:
        self.session.flush()

    def commit(self) -> None:
        self.flush()
        self.session.commit()

    def get_by_project_id(self, project_id: int) -> MealPlanORM | None:
        return (
            self.session.query(MealPlanORM)
            .filter(MealPlanORM.project_id == project_id)
            .first()
        )

    def get_with_details(self, meal_plan_id: str) -> MealPlanORM | None:
        item_recipe = joinedload(MealPlanORM.days).joinedload(MealPlanDayORM.items)
        slot_recipe = (
            joinedload(MealPlanORM.days)
            .joinedload(MealPlanDayORM.slots)
            .joinedload(MealSlotORM.dishes)
        )
        return (
            self.session.query(MealPlanORM)
            .options(
                item_recipe.joinedload(MealPlanItemORM.dish)
                .joinedload(DishORM.recipe)
                .joinedload(RecipeORM.ingredients)
                .joinedload(IngredientORM.product),
                item_recipe.joinedload(MealPlanItemORM.recipe)
                .joinedload(RecipeORM.ingredients)
                .joinedload(IngredientORM.product),
                item_recipe.joinedload(MealPlanItemORM.recipe)
                .joinedload(RecipeORM.components)
                .joinedload(RecipeComponentORM.product),
                slot_recipe.joinedload(MealSlotDishORM.dish)
                .joinedload(DishORM.recipe)
                .joinedload(RecipeORM.ingredients)
                .joinedload(IngredientORM.product),
                slot_recipe.joinedload(MealSlotDishORM.recipe)
                .joinedload(RecipeORM.ingredients)
                .joinedload(IngredientORM.product),
                slot_recipe.joinedload(MealSlotDishORM.recipe)
                .joinedload(RecipeORM.components)
                .joinedload(RecipeComponentORM.product),
            )
            .filter(MealPlanORM.id == meal_plan_id)
            .first()
        )
