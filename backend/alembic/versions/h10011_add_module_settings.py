"""add typed module settings

Revision ID: h10011
Revises: h10010
Create Date: 2026-07-17
"""

from alembic import op
import sqlalchemy as sa


revision = "h10011"
down_revision = "h10010"
branch_labels = None
depends_on = None


def upgrade() -> None:
    module_settings = op.create_table(
        "module_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("projects_visible", sa.Boolean(), nullable=False),
        sa.Column("catalogue_visible", sa.Boolean(), nullable=False),
        sa.Column("catalog_import_visible", sa.Boolean(), nullable=False),
        sa.Column("shopping_visible", sa.Boolean(), nullable=False),
        sa.Column("equipment_visible", sa.Boolean(), nullable=False),
        sa.Column("documents_visible", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("id = 1", name="ck_module_settings_singleton"),
        sa.CheckConstraint(
            "version > 0",
            name="ck_module_settings_version_positive",
        ),
        sa.CheckConstraint(
            "projects_visible",
            name="ck_module_settings_projects_required",
        ),
        sa.CheckConstraint(
            "catalogue_visible",
            name="ck_module_settings_catalogue_required",
        ),
        sa.CheckConstraint(
            "NOT documents_visible OR (shopping_visible AND equipment_visible)",
            name="ck_module_settings_document_dependencies",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.bulk_insert(
        module_settings,
        [
            {
                "id": 1,
                "projects_visible": True,
                "catalogue_visible": True,
                "catalog_import_visible": True,
                "shopping_visible": True,
                "equipment_visible": True,
                "documents_visible": True,
                "version": 1,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("module_settings")
