from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, PrimaryKeyConstraint, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.dish import DishORM
    from app.models.recipe import RecipeORM


class DishRecipeVariantORM(Base):
    __tablename__ = "dish_recipe_variants"
    __table_args__ = (
        PrimaryKeyConstraint("dish_id", "recipe_id", name="pk_dish_recipe_variants"),
    )

    dish_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("dishes.id", ondelete="CASCADE"),
        nullable=False,
    )
    recipe_id: Mapped[str] = mapped_column(
        String,
        ForeignKey("recipes.id", ondelete="RESTRICT"),
        nullable=False,
    )

    dish: Mapped["DishORM"] = relationship(back_populates="recipe_variants")
    recipe: Mapped["RecipeORM"] = relationship()
