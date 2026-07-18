from sqlalchemy import ForeignKey, Integer, String, event, select
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class MealSlotDishORM(Base):
    """Dish attached to a meal slot with its selected Recipe snapshot."""

    __tablename__ = "meal_slot_dishes"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    meal_slot_id: Mapped[str] = mapped_column(
        ForeignKey("meal_slots.id"), nullable=False
    )
    dish_id: Mapped[str] = mapped_column(ForeignKey("dishes.id"), nullable=False)
    recipe_id: Mapped[str] = mapped_column(
        ForeignKey("recipes.id", ondelete="RESTRICT"), nullable=False
    )
    order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    slot = relationship("MealSlotORM", back_populates="dishes")
    dish = relationship("DishORM")
    recipe = relationship("RecipeORM")


@event.listens_for(MealSlotDishORM, "before_insert")
def _default_slot_recipe(_mapper, connection, target: MealSlotDishORM) -> None:
    if target.recipe_id:
        return
    from app.models.dish import DishORM

    recipe_id = connection.scalar(
        select(DishORM.recipe_id).where(DishORM.id == target.dish_id)
    )
    if recipe_id is None:
        raise ValueError("Dish default recipe not found")
    target.recipe_id = recipe_id
