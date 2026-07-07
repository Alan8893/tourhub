from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MealPlanItemORM(Base):
    """
    Single meal inside a meal plan day.

    Example:

    Day 1:

    breakfast:
    Oatmeal

    dinner:
    Camp pilaf
    """

    __tablename__ = "meal_plan_items"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    meal_plan_day_id: Mapped[str] = mapped_column(
        ForeignKey("meal_plan_days.id"),
        nullable=False,
    )

    dish_id: Mapped[str] = mapped_column(
        ForeignKey("dishes.id"),
        nullable=False,
    )

    meal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    day = relationship(
        "MealPlanDayORM",
        back_populates="items",
    )

    dish = relationship(
        "DishORM",
    )