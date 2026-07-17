"""add typed document appearance settings

Revision ID: h10010
Revises: h10009
Create Date: 2026-07-17
"""

from alembic import op
import sqlalchemy as sa


revision = "h10010"
down_revision = "h10009"
branch_labels = None
depends_on = None


def upgrade() -> None:
    document_settings = op.create_table(
        "document_appearance_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("primary_color", sa.String(length=7), nullable=False),
        sa.Column("accent_color", sa.String(length=7), nullable=False),
        sa.Column("heading_color", sa.String(length=7), nullable=False),
        sa.Column("table_header_background", sa.String(length=7), nullable=False),
        sa.Column("table_header_text", sa.String(length=7), nullable=False),
        sa.Column("table_border_color", sa.String(length=7), nullable=False),
        sa.Column("title_background_color", sa.String(length=7), nullable=False),
        sa.Column("logo_source", sa.String(length=32), nullable=False),
        sa.Column("show_contacts", sa.Boolean(), nullable=False),
        sa.Column("footer_text", sa.Text(), nullable=True),
        sa.Column(
            "use_document_image_as_title_background",
            sa.Boolean(),
            nullable=False,
        ),
        sa.Column("table_density", sa.String(length=16), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint(
            "id = 1",
            name="ck_document_appearance_settings_singleton",
        ),
        sa.CheckConstraint(
            "version > 0",
            name="ck_document_appearance_settings_version_positive",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.bulk_insert(
        document_settings,
        [
            {
                "id": 1,
                "primary_color": "#1B5E20",
                "accent_color": "#F9A825",
                "heading_color": "#1B5E20",
                "table_header_background": "#E8F2E8",
                "table_header_text": "#162018",
                "table_border_color": "#405047",
                "title_background_color": "#F4F7F4",
                "logo_source": "main_logo",
                "show_contacts": True,
                "footer_text": None,
                "use_document_image_as_title_background": False,
                "table_density": "comfortable",
                "version": 1,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("document_appearance_settings")
