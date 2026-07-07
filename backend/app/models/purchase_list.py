from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PurchaseListORM(Base):
    """Persisted shopping result prepared for purchasing."""

    __tablename__ = "purchase_lists"

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
        "PurchaseListItemORM",
        back_populates="purchase_list",
        cascade="all, delete-orphan",
    )
