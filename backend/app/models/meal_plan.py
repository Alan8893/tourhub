from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MealPlanORM(Base):
    """
    Meal plan for a hiking project.

    Represents generated menu for a trip.
    """

    __tablename__ = "meal_plans"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    project_id: Mapped[int | None] = mapped_column(
        ForeignKey("projects.id"),
        nullable=True,
        index=True,
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

    project = relationship(
        "ProjectORM",
        back_populates="meal_plans",
    )

    days = relationship(
        "MealPlanDayORM",
        back_populates="meal_plan",
        cascade="all, delete-orphan",
        order_by="MealPlanDayORM.day_number",
    )
