from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, JSON, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class AppearanceSettingsORM(Base):
    __tablename__ = "appearance_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_appearance_settings_singleton"),
        CheckConstraint("version > 0", name="ck_appearance_settings_version_positive"),
        CheckConstraint(
            "border_radius >= 0 AND border_radius <= 24",
            name="ck_appearance_settings_radius_range",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    preset_name: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="tourhub",
        server_default="tourhub",
    )
    font_family: Mapped[str] = mapped_column(
        String(32),
        nullable=False,
        default="system",
        server_default="system",
    )
    density: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="comfortable",
        server_default="comfortable",
    )
    border_radius: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=10,
        server_default=text("10"),
    )
    button_style: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="contained",
        server_default="contained",
    )
    card_style: Mapped[str] = mapped_column(
        String(16),
        nullable=False,
        default="outlined",
        server_default="outlined",
    )
    shadows_enabled: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
        server_default=text("true"),
    )
    light_tokens: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)
    dark_tokens: Mapped[dict[str, str]] = mapped_column(JSON, nullable=False, default=dict)
    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
