"""add user contact profiles

Revision ID: h10022
Revises: h10021
Create Date: 2026-07-21
"""

from alembic import op
import sqlalchemy as sa


revision = "h10022"
down_revision = "h10021"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone", sa.String(length=32), nullable=True))
    op.add_column(
        "users",
        sa.Column("telegram_url", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("max_url", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "users",
        sa.Column("vk_url", sa.String(length=255), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("users", "vk_url")
    op.drop_column("users", "max_url")
    op.drop_column("users", "telegram_url")
    op.drop_column("users", "phone")
