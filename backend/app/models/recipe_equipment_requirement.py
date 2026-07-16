from sqlalchemy import CheckConstraint, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, validates

from app.models.base import Base


class RecipeEquipmentRequirementORM(Base):
    """Equipment quantity required while preparing one recipe."""

    __tablename__ = "recipe_equipment_requirements"
    __table_args__ = (
        UniqueConstraint(
            "recipe_id",
            "equipment_name",
            name="uq_recipe_equipment_requirement_name",
        ),
        CheckConstraint("quantity > 0", name="ck_recipe_equipment_quantity_positive"),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    recipe_id: Mapped[str] = mapped_column(
        ForeignKey("recipes.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    equipment_name: Mapped[str] = mapped_column(String(255), nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)

    @validates("equipment_name")
    def normalize_equipment_name(self, _key: str, value: str) -> str:
        normalized = " ".join(value.split())
        if not normalized:
            raise ValueError("Equipment name must not be empty")
        return normalized[:1].upper() + normalized[1:]
