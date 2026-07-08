"""add project id to purchase lists

Revision ID: a20001
Revises: a10001
Create Date: 2026-07-08
"""

from alembic import op
import sqlalchemy as sa


revision = "a20001"
down_revision = "a10001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "purchase_lists",
        sa.Column(
            "project_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_purchase_lists_project_id",
        "purchase_lists",
        "projects",
        ["project_id"],
        ["id"],
    )

    op.create_index(
        "ix_purchase_lists_project_id",
        "purchase_lists",
        ["project_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_purchase_lists_project_id",
        table_name="purchase_lists",
    )

    op.drop_constraint(
        "fk_purchase_lists_project_id",
        "purchase_lists",
        type_="foreignkey",
    )

    op.drop_column(
        "purchase_lists",
        "project_id",
    )
