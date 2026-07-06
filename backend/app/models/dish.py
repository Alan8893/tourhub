from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class DishORM(Base):
    """
    Dish used in meal plan.
    """

    __tablename__ = "dishes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False
    )

    recipe_id: Mapped[str] = mapped_column(
        ForeignKey("recipes.id"),
        nullable=False
    )

    recipe = relationship(
        "RecipeORM"
    )