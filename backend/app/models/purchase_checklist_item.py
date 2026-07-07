from decimal import Decimal

from sqlalchemy import Boolean, ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PurchaseChecklistItemORM(Base):
    """Single product item inside a purchase checklist."""

    __tablename__ = "purchase_checklist_items"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    checklist_id: Mapped[str] = mapped_column(
        ForeignKey("purchase_checklists.id"),
        nullable=False,
    )

    product_id: Mapped[str] = mapped_column(
        ForeignKey("products.id"),
        nullable=False,
    )

    required_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    purchased_quantity: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=0,
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    is_checked: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
    )

    note: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    checklist = relationship(
        "PurchaseChecklistORM",
        back_populates="items",
    )
