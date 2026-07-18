from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.dish_meal_role import DishMealRoleORM
    from app.models.dish_recipe_variant import DishRecipeVariantORM


class DishORM(Base):
    """
    Dish used in meal plan.
    """

    __tablename__ = "dishes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    recipe_id: Mapped[str] = mapped_column(
        ForeignKey("recipes.id"),
        nullable=False,
    )

    recipe = relationship("RecipeORM", foreign_keys=[recipe_id])
    recipe_variants: Mapped[list["DishRecipeVariantORM"]] = relationship(
        back_populates="dish",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DishRecipeVariantORM.position",
    )
    meal_roles: Mapped[list["DishMealRoleORM"]] = relationship(
        "DishMealRoleORM",
        back_populates="dish",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DishMealRoleORM.role",
    )
