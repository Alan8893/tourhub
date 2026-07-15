from typing import TYPE_CHECKING

from sqlalchemy import Boolean, CheckConstraint, ForeignKey, String, false
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.modules.domain.meal_role import MEAL_ROLE_VALUES

if TYPE_CHECKING:
    from app.models.dish import DishORM


_ROLE_CHECK = "role IN ({})".format(
    ", ".join(f"'{role}'" for role in MEAL_ROLE_VALUES)
)


class DishMealRoleORM(Base):
    __tablename__ = "dish_meal_roles"
    __table_args__ = (
        CheckConstraint(_ROLE_CHECK, name="ck_dish_meal_roles_role"),
    )

    dish_id: Mapped[str] = mapped_column(
        ForeignKey("dishes.id", ondelete="CASCADE"),
        primary_key=True,
    )
    role: Mapped[str] = mapped_column(
        String(32),
        primary_key=True,
    )
    is_repeatable: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default=false(),
    )

    dish: Mapped["DishORM"] = relationship(
        "DishORM",
        back_populates="meal_roles",
    )
