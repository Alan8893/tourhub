"""add purchase checklist

Revision ID: 8f3a1d2c4e5b
Revises: 74d17f270bc5
Create Date: 2026-07-07

"""

from alembic import op
import sqlalchemy as sa


revision = "8f3a1d2c4e5b"
down_revision = "74d17f270bc5"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "purchase_checklists",
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
        "purchase_checklist_items",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("checklist_id", sa.String(), nullable=False),
        sa.Column("product_id", sa.String(), nullable=False),
        sa.Column("required_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("purchased_quantity", sa.Numeric(10, 2), nullable=False),
        sa.Column("unit", sa.String(length=50), nullable=False),
        sa.Column("is_checked", sa.Boolean(), nullable=False),
        sa.Column("note", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["checklist_id"],
            ["purchase_checklists.id"],
        ),
        sa.ForeignKeyConstraint(
            ["product_id"],
            ["products.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("purchase_checklist_items")
    op.drop_table("purchase_checklists")
