"""add recipe publication lifecycle

Revision ID: h10018
Revises: h10017
Create Date: 2026-07-18
"""

from alembic import op
import sqlalchemy as sa


revision = "h10018"
down_revision = "h10017"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "recipes",
        sa.Column(
            "lifecycle_status",
            sa.String(length=16),
            nullable=False,
            server_default="published",
        ),
    )
    op.add_column(
        "recipes",
        sa.Column("submitted_by_user_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "recipes",
        sa.Column("submitted_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "recipes",
        sa.Column("reviewed_by_user_id", sa.Integer(), nullable=True),
    )
    op.add_column(
        "recipes",
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
    )
    op.add_column(
        "recipes",
        sa.Column("review_comment", sa.String(length=1000), nullable=True),
    )
    op.create_foreign_key(
        "fk_recipes_submitted_by_user_id_users",
        "recipes",
        "users",
        ["submitted_by_user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_foreign_key(
        "fk_recipes_reviewed_by_user_id_users",
        "recipes",
        "users",
        ["reviewed_by_user_id"],
        ["id"],
        ondelete="RESTRICT",
    )
    op.create_index(
        "ix_recipes_submitted_by_user_id",
        "recipes",
        ["submitted_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_recipes_reviewed_by_user_id",
        "recipes",
        ["reviewed_by_user_id"],
        unique=False,
    )
    op.create_index(
        "ix_recipes_lifecycle_status",
        "recipes",
        ["lifecycle_status"],
        unique=False,
    )
    op.create_check_constraint(
        "ck_recipes_supported_lifecycle_status",
        "recipes",
        "lifecycle_status IN ('draft', 'submitted', 'rejected', 'published')",
    )
    op.create_check_constraint(
        "ck_recipes_scope_lifecycle_shape",
        "recipes",
        "(scope = 'club' AND lifecycle_status = 'published') OR "
        "(scope = 'personal' AND lifecycle_status IN ('draft', 'submitted', 'rejected'))",
    )
    op.create_check_constraint(
        "ck_recipes_submission_metadata",
        "recipes",
        "lifecycle_status NOT IN ('submitted', 'rejected') OR "
        "(submitted_by_user_id IS NOT NULL AND submitted_at IS NOT NULL)",
    )
    op.create_check_constraint(
        "ck_recipes_submitted_has_no_decision",
        "recipes",
        "lifecycle_status <> 'submitted' OR "
        "(reviewed_by_user_id IS NULL AND reviewed_at IS NULL AND review_comment IS NULL)",
    )
    op.create_check_constraint(
        "ck_recipes_rejection_metadata",
        "recipes",
        "lifecycle_status <> 'rejected' OR "
        "(reviewed_by_user_id IS NOT NULL AND reviewed_at IS NOT NULL "
        "AND review_comment IS NOT NULL AND length(trim(review_comment)) > 0)",
    )


def downgrade() -> None:
    op.drop_constraint("ck_recipes_rejection_metadata", "recipes", type_="check")
    op.drop_constraint("ck_recipes_submitted_has_no_decision", "recipes", type_="check")
    op.drop_constraint("ck_recipes_submission_metadata", "recipes", type_="check")
    op.drop_constraint("ck_recipes_scope_lifecycle_shape", "recipes", type_="check")
    op.drop_constraint("ck_recipes_supported_lifecycle_status", "recipes", type_="check")
    op.drop_index("ix_recipes_lifecycle_status", table_name="recipes")
    op.drop_index("ix_recipes_reviewed_by_user_id", table_name="recipes")
    op.drop_index("ix_recipes_submitted_by_user_id", table_name="recipes")
    op.drop_constraint(
        "fk_recipes_reviewed_by_user_id_users",
        "recipes",
        type_="foreignkey",
    )
    op.drop_constraint(
        "fk_recipes_submitted_by_user_id_users",
        "recipes",
        type_="foreignkey",
    )
    op.drop_column("recipes", "review_comment")
    op.drop_column("recipes", "reviewed_at")
    op.drop_column("recipes", "reviewed_by_user_id")
    op.drop_column("recipes", "submitted_at")
    op.drop_column("recipes", "submitted_by_user_id")
    op.drop_column("recipes", "lifecycle_status")
