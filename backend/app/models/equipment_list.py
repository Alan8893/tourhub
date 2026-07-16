from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class EquipmentListORM(Base):
    """Persisted equipment projection for one project meal plan."""

    __tablename__ = "equipment_lists"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    meal_plan_id: Mapped[str] = mapped_column(
        ForeignKey("meal_plans.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="prepared",
    )

    project = relationship("ProjectORM")
    meal_plan = relationship("MealPlanORM")
    items = relationship(
        "EquipmentListItemORM",
        back_populates="equipment_list",
        cascade="all, delete-orphan",
        order_by="EquipmentListItemORM.equipment_name",
    )
