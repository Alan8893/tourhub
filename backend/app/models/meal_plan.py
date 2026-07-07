from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MealPlanORM(Base):
    """
    Meal plan for a hiking project.

    Represents generated menu for a trip.

    Example:

    Altai trip
    10 participants
    5 days
    """

    __tablename__ = "meal_plans"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    participants: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    days_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    days = relationship(
        "MealPlanDayORM",
        back_populates="meal_plan",
        cascade="all, delete-orphan",
        order_by="MealPlanDayORM.day_number",
    )