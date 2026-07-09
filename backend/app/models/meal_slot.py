from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MealSlotORM(Base):
    """
    A logical meal inside a hiking day.

    One slot can contain multiple dishes.
    """

    __tablename__ = "meal_slots"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    meal_plan_day_id: Mapped[str] = mapped_column(
        ForeignKey("meal_plan_days.id"),
        nullable=False,
    )

    meal_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    name: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    day = relationship(
        "MealPlanDayORM",
        back_populates="slots",
    )

    dishes = relationship(
        "MealSlotDishORM",
        back_populates="slot",
        cascade="all, delete-orphan",
        order_by="MealSlotDishORM.order",
    )
