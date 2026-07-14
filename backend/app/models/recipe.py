from sqlalchemy import Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.recipe_note import RecipeNoteORM


class RecipeORM(Base):
    """
    Recipe composition.

    Example:
    "Camp pilaf"
    """

    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
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

    notes = relationship(
        "RecipeNoteORM",
        back_populates="recipe",
        cascade="all, delete-orphan",
        order_by=RecipeNoteORM.priority,
    )
