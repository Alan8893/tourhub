from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.recipe_generation_mode import RecipeGenerationMode

if TYPE_CHECKING:
    from app.models.user import UserORM
    from app.modules.projects.models.project_instructor import ProjectInstructorORM


class ProjectORM(Base):
    __tablename__ = "projects"
    __table_args__ = (
        CheckConstraint(
            "recipe_generation_mode IN "
            "('club_only', 'club_and_personal', 'personal_preferred')",
            name="ck_projects_recipe_generation_mode",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    participants: Mapped[int] = mapped_column(Integer, nullable=False)
    days: Mapped[int] = mapped_column(Integer, nullable=False)
    start_date: Mapped[str | None] = mapped_column(String(20), nullable=True)
    first_meal: Mapped[str | None] = mapped_column(String(20), nullable=True)
    last_meal: Mapped[str | None] = mapped_column(String(20), nullable=True)
    recipe_generation_mode: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default=RecipeGenerationMode.CLUB_ONLY.value,
        server_default=RecipeGenerationMode.CLUB_ONLY.value,
    )
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")
    # Nullable in metadata-created test databases for backwards-compatible fixtures.
    # Production migration h10023 backfills every row and applies NOT NULL.
    owner_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=True,
        index=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )

    owner: Mapped["UserORM | None"] = relationship(foreign_keys=[owner_user_id])
    instructor_links: Mapped[list["ProjectInstructorORM"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    meal_plans = relationship(
        "MealPlanORM",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    purchase_lists = relationship(
        "PurchaseListORM",
        back_populates="project",
        cascade="all, delete-orphan",
    )
    purchase_checklists = relationship(
        "PurchaseChecklistORM",
        back_populates="project",
        cascade="all, delete-orphan",
    )
