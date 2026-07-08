"""add project id to meal plans

Revision ID: a10001
Revises: 9c0001
Create Date: 2026-07-08
"""

from alembic import op
import sqlalchemy as sa


revision = "a10001"
down_revision = "9c0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "meal_plans",
        sa.Column("project_id", sa.Integer(), nullable=True),
    )

    op.execute(
        """
        UPDATE meal_plans
        SET project_id = (
            SELECT id
            FROM projects
            ORDER BY id
            LIMIT 1
        )
        WHERE project_id IS NULL
        """
    )

    op.alter_column(
        "meal_plans",
        "project_id",
        nullable=False,
    )

    op.create_foreign_key(
        "fk_meal_plans_project_id",
        "meal_plans",
        "projects",
        ["project_id"],
        ["id"],
    )

    op.create_index(
        "ix_meal_plans_project_id",
        "meal_plans",
        ["project_id"],
    )


def downgrade() -> None:
    op.drop_index(
        "ix_meal_plans_project_id",
        table_name="meal_plans",
    )

    op.drop_constraint(
        "fk_meal_plans_project_id",
        "meal_plans",
        type_="foreignkey",
    )

    op.drop_column(
        "meal_plans",
        "project_id",
    )
