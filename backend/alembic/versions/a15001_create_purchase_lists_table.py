"""create purchase lists tables

Revision ID: a15001
Revises: a10001
Create Date: 2026-07-08
"""

from alembic import op
import sqlalchemy as sa


revision = "a15001"
down_revision = "a10001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "purchase_lists",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("meal_plan_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["meal_plan_id"],
            ["meal_plans.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "purchase_list_items",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("purchase_list_id", sa.String(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("required_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("required_unit", sa.String(length=50), nullable=False),
        sa.Column("package_size", sa.Numeric(10, 2), nullable=False),
        sa.Column("package_unit", sa.String(length=50), nullable=False),
        sa.Column("packages_count", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["purchase_list_id"],
            ["purchase_lists.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("purchase_list_items")
    op.drop_table("purchase_lists")
