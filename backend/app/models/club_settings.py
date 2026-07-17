from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, JSON, LargeBinary, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ClubSettingsORM(Base):
    __tablename__ = "club_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_club_settings_singleton"),
        CheckConstraint("version > 0", name="ck_club_settings_version_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    club_name: Mapped[str] = mapped_column(String(255), nullable=False)
    short_name: Mapped[str | None] = mapped_column(String(100), nullable=True)
    legal_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    address: Mapped[str | None] = mapped_column(String(500), nullable=True)
    phone: Mapped[str | None] = mapped_column(String(100), nullable=True)
    email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    website: Mapped[str | None] = mapped_column(String(500), nullable=True)
    timezone: Mapped[str | None] = mapped_column(String(64), nullable=True)
    city: Mapped[str | None] = mapped_column(String(255), nullable=True)
    region: Mapped[str | None] = mapped_column(String(255), nullable=True)
    social_links: Mapped[list[dict[str, str]]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default=text("'[]'"),
    )

    logo_mime_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    logo_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    light_logo_mime_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    light_logo_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    dark_logo_mime_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    dark_logo_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    square_icon_mime_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    square_icon_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    favicon_mime_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    favicon_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    login_background_mime_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    login_background_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)
    document_image_mime_type: Mapped[str | None] = mapped_column(String(32), nullable=True)
    document_image_bytes: Mapped[bytes | None] = mapped_column(LargeBinary, nullable=True)

    version: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=1,
        server_default=text("1"),
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
