from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RecipeComponentORM(Base):
    """
    Product component used by a recipe.

    Replaces legacy Ingredient semantics gradually.
    Supports base, cooking, optional and serving add-on components.
    """

    __tablename__ = "recipe_components"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    recipe_id: Mapped[str] = mapped_column(
        ForeignKey("recipes.id"),
        nullable=False,
    )

    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )

    component_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="base",
    )

    amount: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="gram",
    )

    calculation_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="per_person",
    )

    people_count: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True,
    )

    product = relationship("ProductORM")

    recipe = relationship(
        "RecipeORM",
        back_populates="components",
    )
