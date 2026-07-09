"""add meal slots tables

Revision ID: e10001
Revises: d10001
Create Date: 2026-07-09
"""

from alembic import op
import sqlalchemy as sa


revision = "e10001"
down_revision = "d10001"
branch_labels = None
depends_on = None



def upgrade() -> None:
    op.create_table(
        "meal_slots",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "meal_plan_day_id",
            sa.String(),
            sa.ForeignKey("meal_plan_days.id"),
            nullable=False,
        ),
        sa.Column("meal_type", sa.String(length=50), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )

    op.create_table(
        "meal_slot_dishes",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "meal_slot_id",
            sa.String(),
            sa.ForeignKey("meal_slots.id"),
            nullable=False,
        ),
        sa.Column(
            "dish_id",
            sa.String(),
            sa.ForeignKey("dishes.id"),
            nullable=False,
        ),
        sa.Column("order", sa.Integer(), nullable=False, server_default="0"),
    )



def downgrade() -> None:
    op.drop_table("meal_slot_dishes")
    op.drop_table("meal_slots")
