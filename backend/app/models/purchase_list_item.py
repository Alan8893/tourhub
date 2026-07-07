from decimal import Decimal

from sqlalchemy import ForeignKey, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class PurchaseListItemORM(Base):
    """Single product line inside a purchase list."""

    __tablename__ = "purchase_list_items"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    purchase_list_id: Mapped[str] = mapped_column(
        ForeignKey("purchase_lists.id"),
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

    required_unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    package_size: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
    )

    package_unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
    )

    packages_count: Mapped[int] = mapped_column(
        nullable=False,
    )

    purchase_list = relationship(
        "PurchaseListORM",
        back_populates="items",
    )

    product = relationship(
        "ProductORM",
        back_populates="purchase_list_items",
    )
