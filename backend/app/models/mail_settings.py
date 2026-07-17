from datetime import datetime

from sqlalchemy import CheckConstraint, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class MailSettingsORM(Base):
    __tablename__ = "mail_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_mail_settings_singleton"),
        CheckConstraint("version > 0", name="ck_mail_settings_version_positive"),
        CheckConstraint(
            "smtp_port BETWEEN 1 AND 65535",
            name="ck_mail_settings_port_range",
        ),
        CheckConstraint(
            "security_mode IN ('plain', 'starttls', 'tls')",
            name="ck_mail_settings_security_mode",
        ),
        CheckConstraint(
            "timeout_seconds BETWEEN 1 AND 120",
            name="ck_mail_settings_timeout_range",
        ),
        CheckConstraint(
            "retry_count BETWEEN 0 AND 10",
            name="ck_mail_settings_retry_range",
        ),
        CheckConstraint("smtp_host <> ''", name="ck_mail_settings_host_required"),
        CheckConstraint("sender_email <> ''", name="ck_mail_settings_sender_required"),
        CheckConstraint("sender_name <> ''", name="ck_mail_settings_sender_name_required"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    smtp_host: Mapped[str] = mapped_column(
        String(253), nullable=False, default="localhost", server_default="localhost"
    )
    smtp_port: Mapped[int] = mapped_column(
        Integer, nullable=False, default=587, server_default=text("587")
    )
    security_mode: Mapped[str] = mapped_column(
        String(16), nullable=False, default="starttls", server_default="starttls"
    )
    smtp_username: Mapped[str | None] = mapped_column(String(255), nullable=True)
    sender_email: Mapped[str] = mapped_column(
        String(320),
        nullable=False,
        default="tourhub@localhost",
        server_default="tourhub@localhost",
    )
    sender_name: Mapped[str] = mapped_column(
        String(120), nullable=False, default="TourHub", server_default="TourHub"
    )
    reply_to_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    test_recipient_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    timeout_seconds: Mapped[int] = mapped_column(
        Integer, nullable=False, default=30, server_default=text("30")
    )
    retry_count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=3, server_default=text("3")
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
