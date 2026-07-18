"""add recipe ownership

Revision ID: h10017
Revises: h10016
Create Date: 2026-07-18
"""

from alembic import op
import sqlalchemy as sa


revision = "h10017"
down_revision = "h10016"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column(
            "scope",
            sa.String(length=16),
            nullable=False,
            server_default="club",
        ),
    )
    op.add_column(
        "recipes",
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
    )
    op.create_foreign_key(
        "fk_recipes_owner_user_id_users",
        "recipes",
        "users",
        ["owner_user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_recipes_owner_user_id",
        "recipes",
        ["owner_user_id"],
        unique=False,
    )
    op.create_check_constraint(
        "ck_recipes_supported_scope",
        "recipes",
        "scope IN ('club', 'personal')",
    )
    op.create_check_constraint(
        "ck_recipes_scope_owner_shape",
        "recipes",
        "(scope = 'club' AND owner_user_id IS NULL) OR "
        "(scope = 'personal' AND owner_user_id IS NOT NULL)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_recipes_scope_owner_shape", "recipes", type_="check")
    op.drop_constraint("ck_recipes_supported_scope", "recipes", type_="check")
    op.drop_index("ix_recipes_owner_user_id", table_name="recipes")
    op.drop_constraint(
        "fk_recipes_owner_user_id_users",
        "recipes",
        type_="foreignkey",
    )
    op.drop_column("recipes", "owner_user_id")
    op.drop_column("recipes", "scope")
