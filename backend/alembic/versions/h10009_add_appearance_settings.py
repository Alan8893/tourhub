"""add typed appearance settings

Revision ID: h10009
Revises: h10008
Create Date: 2026-07-17
"""

from alembic import op
import sqlalchemy as sa


revision = "h10009"
down_revision = "h10008"
branch_labels = None
depends_on = None


TOURHUB_LIGHT = {
    "primary": "#1B5E20",
    "secondary": "#2E7D32",
    "accent": "#F9A825",
    "background": "#F4F7F4",
    "paper": "#FFFFFF",
    "sidebar": "#E8F2E8",
    "appbar": "#1B5E20",
    "text_primary": "#162018",
    "text_secondary": "#435348",
    "divider": "#C8D2CA",
    "success": "#2E7D32",
    "warning": "#ED6C02",
    "error": "#D32F2F",
}

TOURHUB_DARK = {
    "primary": "#81C784",
    "secondary": "#A5D6A7",
    "accent": "#FFD54F",
    "background": "#101713",
    "paper": "#18211B",
    "sidebar": "#1E2A22",
    "appbar": "#16351D",
    "text_primary": "#F2F7F3",
    "text_secondary": "#C1CDC4",
    "divider": "#405047",
    "success": "#81C784",
    "warning": "#FFB74D",
    "error": "#EF9A9A",
}


def upgrade() -> None:
    appearance_settings = op.create_table(
        "appearance_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("preset_name", sa.String(length=32), nullable=False),
        sa.Column("font_family", sa.String(length=32), nullable=False),
        sa.Column("density", sa.String(length=16), nullable=False),
        sa.Column("border_radius", sa.Integer(), nullable=False),
        sa.Column("button_style", sa.String(length=16), nullable=False),
        sa.Column("card_style", sa.String(length=16), nullable=False),
        sa.Column("shadows_enabled", sa.Boolean(), nullable=False),
        sa.Column("light_tokens", sa.JSON(), nullable=False),
        sa.Column("dark_tokens", sa.JSON(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("id = 1", name="ck_appearance_settings_singleton"),
        sa.CheckConstraint(
            "version > 0",
            name="ck_appearance_settings_version_positive",
        ),
        sa.CheckConstraint(
            "border_radius >= 0 AND border_radius <= 24",
            name="ck_appearance_settings_radius_range",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.bulk_insert(
        appearance_settings,
        [
            {
                "id": 1,
                "preset_name": "tourhub",
                "font_family": "system",
                "density": "comfortable",
                "border_radius": 10,
                "button_style": "contained",
                "card_style": "outlined",
                "shadows_enabled": True,
                "light_tokens": TOURHUB_LIGHT,
                "dark_tokens": TOURHUB_DARK,
                "version": 1,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("appearance_settings")
