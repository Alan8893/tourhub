from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.recipe_lifecycle_status import RecipeLifecycleStatus
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
            "lifecycle_status IN ('draft', 'submitted', 'rejected', 'published')",
            name="ck_recipes_supported_lifecycle_status",
        ),
        CheckConstraint(
            "(scope = 'club' AND owner_user_id IS NULL) OR "
            "(scope = 'personal' AND owner_user_id IS NOT NULL)",
            name="ck_recipes_scope_owner_shape",
        ),
        CheckConstraint(
            "(scope = 'club' AND lifecycle_status = 'published') OR "
            "(scope = 'personal' AND lifecycle_status IN ('draft', 'submitted', 'rejected'))",
            name="ck_recipes_scope_lifecycle_shape",
        ),
        CheckConstraint(
            "lifecycle_status NOT IN ('submitted', 'rejected') OR "
            "(submitted_by_user_id IS NOT NULL AND submitted_at IS NOT NULL)",
            name="ck_recipes_submission_metadata",
        ),
        CheckConstraint(
            "lifecycle_status <> 'submitted' OR "
            "(reviewed_by_user_id IS NULL AND reviewed_at IS NULL AND review_comment IS NULL)",
            name="ck_recipes_submitted_has_no_decision",
        ),
        CheckConstraint(
            "lifecycle_status <> 'rejected' OR "
            "(reviewed_by_user_id IS NOT NULL AND reviewed_at IS NOT NULL "
            "AND review_comment IS NOT NULL AND length(trim(review_comment)) > 0)",
            name="ck_recipes_rejection_metadata",
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

    lifecycle_status: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default=RecipeLifecycleStatus.PUBLISHED.value,
        server_default=RecipeLifecycleStatus.PUBLISHED.value,
    )

    submitted_by_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    submitted_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)

    reviewed_by_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    review_comment: Mapped[str | None] = mapped_column(String(1000), nullable=True)

    is_archived: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="false",
    )

    owner: Mapped["UserORM | None"] = relationship(foreign_keys=[owner_user_id])
    submitted_by: Mapped["UserORM | None"] = relationship(
        foreign_keys=[submitted_by_user_id]
    )
    reviewed_by: Mapped["UserORM | None"] = relationship(
        foreign_keys=[reviewed_by_user_id]
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
