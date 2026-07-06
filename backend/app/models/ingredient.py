from sqlalchemy import ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class IngredientORM(Base):
    """
    Ingredient usage inside recipe.

    Example:

    Pilaf:
        rice 120g/person
        meat 100g/person
    """

    __tablename__ = "ingredients"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    recipe_id: Mapped[str] = mapped_column(
        ForeignKey("recipes.id"),
        nullable=False
    )

    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"),
        nullable=False
    )

    amount_per_person: Mapped[int] = mapped_column(
        Integer,
        nullable=False
    )


    product = relationship(
        "ProductORM"
    )