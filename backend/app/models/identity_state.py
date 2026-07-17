from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class IdentityStateORM(Base):
    __tablename__ = "identity_state"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_identity_state_singleton"),
        CheckConstraint("version > 0", name="ck_identity_state_version_positive"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    bootstrap_completed: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=False, server_default=text("false")
    )
    version: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, server_default=text("1")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, nullable=False, server_default=func.now(), onupdate=func.now()
    )
