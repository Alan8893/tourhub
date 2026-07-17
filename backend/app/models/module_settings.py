from datetime import datetime

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, func, text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class ModuleSettingsORM(Base):
    __tablename__ = "module_settings"
    __table_args__ = (
        CheckConstraint("id = 1", name="ck_module_settings_singleton"),
        CheckConstraint("version > 0", name="ck_module_settings_version_positive"),
        CheckConstraint("projects_visible", name="ck_module_settings_projects_required"),
        CheckConstraint("catalogue_visible", name="ck_module_settings_catalogue_required"),
        CheckConstraint(
            "NOT documents_visible OR (shopping_visible AND equipment_visible)",
            name="ck_module_settings_document_dependencies",
        ),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, default=1)
    projects_visible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    catalogue_visible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    catalog_import_visible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    shopping_visible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    equipment_visible: Mapped[bool] = mapped_column(
        Boolean, nullable=False, default=True, server_default=text("true")
    )
    documents_visible: Mapped[bool] = mapped_column(
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
