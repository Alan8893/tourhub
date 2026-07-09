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
        back_populates="recipe",
        cascade="all, delete-orphan",
    )

    components = relationship(
        "RecipeComponentORM",
        back_populates="recipe",
        cascade="all, delete-orphan",
    )
