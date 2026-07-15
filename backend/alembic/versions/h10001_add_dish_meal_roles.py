"""add dish meal roles

Revision ID: h10001
Revises: g10001
Create Date: 2026-07-15
"""

from alembic import op
import sqlalchemy as sa


revision = "h10001"
down_revision = "g10001"
branch_labels = None
depends_on = None


_ROLE_CHECK = "role IN ('main', 'addition', 'drink', 'snack')"


def upgrade() -> None:
    op.create_table(
        "dish_meal_roles",
        sa.Column("dish_id", sa.String(), nullable=False),
        sa.Column("role", sa.String(length=32), nullable=False),
        sa.Column(
            "is_repeatable",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
        sa.CheckConstraint(
            _ROLE_CHECK,
            name="ck_dish_meal_roles_role",
        ),
        sa.ForeignKeyConstraint(
            ["dish_id"],
            ["dishes.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("dish_id", "role"),
    )


def downgrade() -> None:
    op.drop_table("dish_meal_roles")
