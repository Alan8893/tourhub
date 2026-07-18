from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.recipe_generation_mode import RecipeGenerationMode


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
