"""add equipment list overrides

Revision ID: h10006
Revises: h10005
Create Date: 2026-07-16
"""

from alembic import op
import sqlalchemy as sa


revision = "h10006"
down_revision = "h10005"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "equipment_list_items",
        sa.Column("calculated_quantity", sa.Integer(), nullable=True),
    )
    op.add_column(
        "equipment_list_items",
        sa.Column(
            "is_manual",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.add_column(
        "equipment_list_items",
        sa.Column(
            "is_removed",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.execute(
        "UPDATE equipment_list_items "
        "SET calculated_quantity = required_quantity"
    )
    op.create_check_constraint(
        "ck_equipment_calculated_quantity_positive",
        "equipment_list_items",
        "calculated_quantity IS NULL OR calculated_quantity > 0",
    )
    op.alter_column("equipment_list_items", "is_manual", server_default=None)
    op.alter_column("equipment_list_items", "is_removed", server_default=None)


def downgrade() -> None:
    op.drop_constraint(
        "ck_equipment_calculated_quantity_positive",
        "equipment_list_items",
        type_="check",
    )
    op.drop_column("equipment_list_items", "is_removed")
    op.drop_column("equipment_list_items", "is_manual")
    op.drop_column("equipment_list_items", "calculated_quantity")
