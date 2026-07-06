from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DishORM(Base):

    __tablename__ = "dishes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    recipe_id: Mapped[str] = mapped_column(
        String,
        nullable=False
    )