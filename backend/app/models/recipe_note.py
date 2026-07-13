from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base
from app.models.recipe_note_type import RecipeNoteType


class RecipeNoteORM(Base):
    __tablename__ = "recipe_notes"

    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
    )

    recipe_id: Mapped[str] = mapped_column(
        ForeignKey("recipes.id"),
        nullable=False,
    )

    type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default=RecipeNoteType.COOKING_TIP.value,
    )

    text: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=100,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
    )

    recipe = relationship(
        "RecipeORM",
        back_populates="notes",
    )
