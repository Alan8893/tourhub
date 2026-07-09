from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MealSlotDishORM(Base):
    """
    Dish attached to a meal slot.

    Allows one meal to contain multiple dishes.
    """

    __tablename__ = "meal_slot_dishes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    meal_slot_id: Mapped[str] = mapped_column(
        ForeignKey("meal_slots.id"),
        nullable=False,
    )

    dish_id: Mapped[str] = mapped_column(
        ForeignKey("dishes.id"),
        nullable=False,
    )

    order: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    slot = relationship(
        "MealSlotORM",
        back_populates="dishes",
    )

    dish = relationship(
        "DishORM",
    )
