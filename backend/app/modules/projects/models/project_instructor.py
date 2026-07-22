from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, PrimaryKeyConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base

if TYPE_CHECKING:
    from app.models.user import UserORM
    from app.modules.projects.models.project import ProjectORM


class ProjectInstructorORM(Base):
    __tablename__ = "project_instructors"
    __table_args__ = (
        PrimaryKeyConstraint("project_id", "user_id", name="pk_project_instructors"),
    )

    project_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("projects.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    added_by_user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        server_default=func.now(),
    )

    project: Mapped["ProjectORM"] = relationship(back_populates="instructor_links")
    user: Mapped["UserORM"] = relationship(foreign_keys=[user_id])
    added_by: Mapped["UserORM | None"] = relationship(foreign_keys=[added_by_user_id])
