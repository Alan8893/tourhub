from sqlalchemy import String, Integer
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ProductORM(Base):
    """
    Product available for purchase.

    Example:
    - Buckwheat
    - Rice
    - Meat
    - Tea
    """

    __tablename__ = "products"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
        unique=True
    )

    category: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True
    )

    unit: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="gram"
    )

    package_size: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )