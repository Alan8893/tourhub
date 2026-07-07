from sqlalchemy.orm import Session

from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM


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