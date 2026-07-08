"""add project id to purchase checklists

Revision ID: a30001
Revises: a20001
Create Date: 2026-07-08
"""

from alembic import op
import sqlalchemy as sa


revision = "a30001"
down_revision = "a20001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "purchase_checklists",
        sa.Column(
            "project_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.create_foreign_key(
        "fk_purchase_checklists_project_id",
        "purchase_checklists",
        "projects",
        ["project_id"],
        ["id"],
    )

    op.create_index(
        "ix_purchase_checklists_project_id",
        "purchase_checklists",
        ["project_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_purchase_checklists_project_id",
        table_name="purchase_checklists",
    )

    op.drop_constraint(
        "fk_purchase_checklists_project_id",
        "purchase_checklists",
        type_="foreignkey",
    )

    op.drop_column(
        "purchase_checklists",
        "project_id",
    )
