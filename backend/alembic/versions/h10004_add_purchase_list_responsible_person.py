"""add purchase list responsible person

Revision ID: h10004
Revises: h10003
Create Date: 2026-07-16
"""

from alembic import op
import sqlalchemy as sa


revision = "h10004"
down_revision = "h10003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "purchase_lists",
        sa.Column(
            "responsible_person",
            sa.String(length=255),
            nullable=True,
        ),
    )


def downgrade() -> None:
    op.drop_column("purchase_lists", "responsible_person")
