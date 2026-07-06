from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class RecipeORM(Base):
    """
    Recipe composition.

    Example:
    "Camp pilaf"
    """

    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    ingredients = relationship(
        "IngredientORM",
        cascade="all, delete-orphan"
    )