from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PurchaseChecklistORM(Base):
    """
    Purchase checklist generated from a meal plan.

    Stores user-controlled purchase progress separately from calculated shopping lists.
    """

    __tablename__ = "purchase_checklists"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    meal_plan_id: Mapped[str] = mapped_column(
        ForeignKey("meal_plans.id"),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="draft",
    )

    items = relationship(
        "PurchaseChecklistItemORM",
        back_populates="checklist",
        cascade="all, delete-orphan",
    )
