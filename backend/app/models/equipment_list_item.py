from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EquipmentListItemORM(Base):
    """Aggregated equipment line for a prepared project."""

    __tablename__ = "equipment_list_items"
    __table_args__ = (
        UniqueConstraint(
            "equipment_list_id",
            "equipment_name",
            name="uq_equipment_list_item_name",
        ),
        CheckConstraint("required_quantity > 0", name="ck_equipment_required_quantity_positive"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    equipment_list_id: Mapped[str] = mapped_column(
        ForeignKey("equipment_lists.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    equipment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    required_quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    equipment_list = relationship(
        "EquipmentListORM",
        back_populates="items",
    )
