from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.recipe_note import RecipeNoteORM
from app.models.recipe_scope import RecipeScope

if TYPE_CHECKING:
    from app.models.user import UserORM


class RecipeORM(Base):
    """
    Recipe composition.

    Example:
    "Camp pilaf"
    """

    __tablename__ = "recipes"
    __table_args__ = (
        CheckConstraint(
            "scope IN ('club', 'personal')",
            name="ck_recipes_supported_scope",
        ),
        CheckConstraint(
            "(scope = 'club' AND owner_user_id IS NULL) OR "
            "(scope = 'personal' AND owner_user_id IS NOT NULL)",
            name="ck_recipes_scope_owner_shape",
        ),
    )

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True,
    )

    scope: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=RecipeScope.CLUB.value,
        server_default=RecipeScope.CLUB.value,
    )

    owner_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    owner: Mapped["UserORM | None"] = relationship(foreign_keys=[owner_user_id])

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
