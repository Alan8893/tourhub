"""add project preparation fields

Revision ID: b10001
Revises: a30001
Create Date: 2026-07-09
"""

from alembic import op
import sqlalchemy as sa

revision = "b10001"
down_revision = "a30001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("projects", sa.Column("start_date", sa.String(length=20), nullable=True))
    op.add_column("projects", sa.Column("first_meal", sa.String(length=20), nullable=True))


def downgrade() -> None:
    op.drop_column("projects", "first_meal")
    op.drop_column("projects", "start_date")
