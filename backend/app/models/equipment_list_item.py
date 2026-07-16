from sqlalchemy import Boolean, CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EquipmentListItemORM(Base):
    """Calculated or manually adjusted equipment line for a prepared project."""

    __tablename__ = "equipment_list_items"
    __table_args__ = (
        UniqueConstraint(
            "equipment_list_id",
            "equipment_name",
            name="uq_equipment_list_item_name",
        ),
        CheckConstraint(
            "required_quantity > 0",
            name="ck_equipment_required_quantity_positive",
        ),
        CheckConstraint(
            "calculated_quantity IS NULL OR calculated_quantity > 0",
            name="ck_equipment_calculated_quantity_positive",
        ),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    equipment_list_id: Mapped[str] = mapped_column(
        ForeignKey("equipment_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    equipment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    required_quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    calculated_quantity: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_manual: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_removed: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    equipment_list = relationship(
        "EquipmentListORM",
        back_populates="items",
    )
