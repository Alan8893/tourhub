from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, String, Text, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class DocumentAppearanceSettingsORM(Base):
    __tablename__ = "document_appearance_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_document_appearance_settings_singleton"),
        CheckConstraint(
            "version > 0",
            name="ck_document_appearance_settings_version_positive",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    primary_color: Mapped[str] = mapped_column(
        String(7), nullable=False, default="#1B5E20", server_default="#1B5E20"
    )
    accent_color: Mapped[str] = mapped_column(
        String(7), nullable=False, default="#F9A825", server_default="#F9A825"
    )
    heading_color: Mapped[str] = mapped_column(
        String(7), nullable=False, default="#1B5E20", server_default="#1B5E20"
    )
    table_header_background: Mapped[str] = mapped_column(
        String(7), nullable=False, default="#E8F2E8", server_default="#E8F2E8"
    )
    table_header_text: Mapped[str] = mapped_column(
        String(7), nullable=False, default="#162018", server_default="#162018"
    )
    table_border_color: Mapped[str] = mapped_column(
        String(7), nullable=False, default="#405047", server_default="#405047"
    )
    title_background_color: Mapped[str] = mapped_column(
        String(7), nullable=False, default="#F4F7F4", server_default="#F4F7F4"
    )
    logo_source: Mapped[str] = mapped_column(
        String(32), nullable=False, default="main_logo", server_default="main_logo"
    )
    show_contacts: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    footer_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    use_document_image_as_title_background: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    table_density: Mapped[str] = mapped_column(
        String(16), nullable=False, default="comfortable", server_default="comfortable"
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        server_default=func.now(),
        onupdate=func.now(),
    )
