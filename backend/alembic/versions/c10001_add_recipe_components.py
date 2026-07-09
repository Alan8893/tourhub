"""add recipe components table

Revision ID: c10001
Revises: b10001
Create Date: 2026-07-09
"""

from alembic import op
import sqlalchemy as sa


revision = "c10001"
down_revision = "b10001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipe_components",
        sa.Column("id", sa.String(), primary_key=True),
        sa.Column(
            "recipe_id",
            sa.String(),
            sa.ForeignKey("recipes.id"),
            nullable=False,
        ),
        sa.Column(
            "product_id",
            sa.String(),
            sa.ForeignKey("products.id"),
            nullable=False,
        ),
        sa.Column(
            "component_type",
            sa.String(length=50),
            nullable=False,
            server_default="base",
        ),
        sa.Column("amount", sa.Integer(), nullable=False),
        sa.Column(
            "unit",
            sa.String(length=50),
            nullable=False,
            server_default="gram",
        ),
        sa.Column(
            "calculation_type",
            sa.String(length=50),
            nullable=False,
            server_default="per_person",
        ),
        sa.Column("people_count", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    op.drop_table("recipe_components")
