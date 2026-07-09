from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MealPlanDayORM(Base):
    """
    Single day inside a meal plan.

    Example:

    Day 1
    - breakfast
    - lunch
    - dinner
    """

    __tablename__ = "meal_plan_days"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    meal_plan_id: Mapped[str] = mapped_column(
        ForeignKey("meal_plans.id"),
        nullable=False,
    )

    day_number: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    meal_plan = relationship(
        "MealPlanORM",
        back_populates="days",
    )

    items = relationship(
        "MealPlanItemORM",
        back_populates="day",
        cascade="all, delete-orphan",
        order_by="MealPlanItemORM.meal_type",
    )

    slots = relationship(
        "MealSlotORM",
        back_populates="day",
        cascade="all, delete-orphan",
        order_by="MealSlotORM.order",
    )
