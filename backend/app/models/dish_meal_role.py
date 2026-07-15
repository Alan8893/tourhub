from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    ForeignKey,
    ForeignKeyConstraint,
    String,
    false,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.modules.domain.meal_role import MEAL_ROLE_VALUES
from app.modules.domain.meal_type import MEAL_TYPE_VALUES

if TYPE_CHECKING:
    from app.models.dish import DishORM


_ROLE_CHECK = "role IN ({})".format(
    ", ".join(f"'{role}'" for role in MEAL_ROLE_VALUES)
)
_MEAL_TYPE_CHECK = "meal_type IN ({})".format(
    ", ".join(f"'{meal_type}'" for meal_type in MEAL_TYPE_VALUES)
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
    meal_types: Mapped[list["DishMealRoleMealTypeORM"]] = relationship(
        "DishMealRoleMealTypeORM",
        back_populates="meal_role",
        cascade="all, delete-orphan",
        passive_deletes=True,
        order_by="DishMealRoleMealTypeORM.meal_type",
    )


class DishMealRoleMealTypeORM(Base):
    __tablename__ = "dish_meal_role_meal_types"
    __table_args__ = (
        CheckConstraint(
            _MEAL_TYPE_CHECK,
            name="ck_dish_meal_role_meal_types_meal_type",
        ),
        ForeignKeyConstraint(
            ["dish_id", "role"],
            ["dish_meal_roles.dish_id", "dish_meal_roles.role"],
            ondelete="CASCADE",
        ),
    )

    dish_id: Mapped[str] = mapped_column(String, primary_key=True)
    role: Mapped[str] = mapped_column(String(32), primary_key=True)
    meal_type: Mapped[str] = mapped_column(String(32), primary_key=True)

    meal_role: Mapped[DishMealRoleORM] = relationship(
        "DishMealRoleORM",
        back_populates="meal_types",
    )
