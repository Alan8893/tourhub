from sqlalchemy.orm import Session, joinedload

from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM
from app.models.dish import DishORM
from app.models.recipe import RecipeORM
from app.models.ingredient import IngredientORM


class MealPlanRepository:
    """
    Repository for meal plan persistence.
    """

    def __init__(
        self,
        session: Session,
    ):
        self.session = session

    def add(
        self,
        meal_plan: MealPlanORM,
    ) -> None:
        self.session.add(meal_plan)

    def add_day(
        self,
        day: MealPlanDayORM,
    ) -> None:
        self.session.add(day)

    def add_item(
        self,
        item: MealPlanItemORM,
    ) -> None:
        self.session.add(item)

    def commit(self) -> None:
        self.session.flush()
        self.session.commit()

    def get_with_details(
        self,
        meal_plan_id: str,
    ) -> MealPlanORM | None:
        """
        Load meal plan with full nutrition graph.

        Required for:

        MealPlan
            ↓
        Dish
            ↓
        Recipe
            ↓
        Ingredient
            ↓
        Product
        """

        return (
            self.session.query(
                MealPlanORM
            )
            .options(
                joinedload(
                    MealPlanORM.days
                )
                .joinedload(
                    MealPlanDayORM.items
                )
                .joinedload(
                    MealPlanItemORM.dish
                )
                .joinedload(
                    DishORM.recipe
                )
                .joinedload(
                    RecipeORM.ingredients
                )
                .joinedload(
                    IngredientORM.product
                )
            )
            .filter(
                MealPlanORM.id == meal_plan_id
            )
            .first()
        )