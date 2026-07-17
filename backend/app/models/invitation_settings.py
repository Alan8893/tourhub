from datetime import datetime

from sqlalchemy import JSON, Boolean, CheckConstraint, DateTime, Integer, String, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class InvitationSettingsORM(Base):
    __tablename__ = "invitation_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_invitation_settings_singleton"),
        CheckConstraint("version > 0", name="ck_invitation_settings_version_positive"),
        CheckConstraint(
            "expires_after_days BETWEEN 1 AND 90",
            name="ck_invitation_settings_expiry_range",
        ),
        CheckConstraint(
            "active_invitation_limit BETWEEN 1 AND 1000",
            name="ck_invitation_settings_active_limit_range",
        ),
        CheckConstraint(
            "default_role IN ('instructor', 'verified_instructor')",
            name="ck_invitation_settings_safe_default_role",
        ),
        CheckConstraint(
            "administrators_only",
            name="ck_invitation_settings_administrators_only",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    expires_after_days: Mapped[int] = mapped_column(
        Integer, nullable=False, default=7, server_default=text("7")
    )
    default_role: Mapped[str] = mapped_column(
        String(32), nullable=False, default="instructor", server_default="instructor"
    )
    allowed_email_domains: Mapped[list[str]] = mapped_column(
        JSON,
        nullable=False,
        default=list,
        server_default=text("'[]'"),
    )
    allow_resend: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    active_invitation_limit: Mapped[int] = mapped_column(
        Integer, nullable=False, default=100, server_default=text("100")
    )
    administrators_only: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    require_email_confirmation: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
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
