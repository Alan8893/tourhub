"""persist meal plan generation warnings

Revision ID: h10003
Revises: h10002
Create Date: 2026-07-16
"""

from alembic import op
import sqlalchemy as sa


revision = "h10003"
down_revision = "h10002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "meal_plans",
        sa.Column(
            "warnings",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )


def downgrade() -> None:
    op.drop_column("meal_plans", "warnings")
