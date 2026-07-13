"""add recipe notes table

Revision ID: e10001
Revises: c10001
Create Date: 2026-07-13
"""

from alembic import op
import sqlalchemy as sa


revision = "e10001"
down_revision = "c10001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipe_notes",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "recipe_id",
            sa.String(),
            sa.ForeignKey("recipes.id"),
            nullable=False,
        ),
        sa.Column(
            "type",
            sa.String(length=50),
            nullable=False,
            server_default="cooking_tip",
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("priority", sa.Integer(), nullable=False, server_default="100"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("NOW()"),
        ),
    )
    op.create_index(
        "ix_recipe_notes_recipe_id_priority",
        "recipe_notes",
        ["recipe_id", "priority"],
    )


def downgrade() -> None:
    op.drop_index("ix_recipe_notes_recipe_id_priority", table_name="recipe_notes")
    op.drop_table("recipe_notes")
