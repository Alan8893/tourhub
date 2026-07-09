"""add last meal to projects

Revision ID: a40001
Revises: a30001
Create Date: 2026-07-09
"""

from alembic import op
import sqlalchemy as sa


revision = "a40001"
down_revision = "a30001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "projects",
        sa.Column("last_meal", sa.String(length=20), nullable=True),
    )


def downgrade() -> None:
    op.drop_column(
        "projects",
        "last_meal",
    )
