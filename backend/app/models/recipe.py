from sqlalchemy import String, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class RecipeORM(Base):

    __tablename__ = "recipes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True
    )

    name: Mapped[str] = mapped_column(
        String,
        nullable=False
    )

    ingredients: Mapped[dict] = mapped_column(
        JSON,
        nullable=False
    )