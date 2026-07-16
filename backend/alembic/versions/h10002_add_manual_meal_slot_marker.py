"""add manual meal slot marker

Revision ID: h10002
Revises: h10001
Create Date: 2026-07-16
"""

from alembic import op
import sqlalchemy as sa


revision = "h10002"
down_revision = "h10001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "meal_slots",
        sa.Column(
            "is_manually_edited",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.alter_column(
        "meal_slots",
        "is_manually_edited",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("meal_slots", "is_manually_edited")
