"""add secure password reset tokens and request throttling

Revision ID: h10024
Revises: h10023
Create Date: 2026-10-20
"""

# ruff: noqa: I001
import sqlalchemy as sa

from alembic import op

revision = "h10024"
down_revision = "h10023"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("consumed_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], name="fk_password_reset_tokens_user_id_users",
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name="pk_password_reset_tokens"),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
    op.create_index(
        "ix_password_reset_tokens_token_hash",
        "password_reset_tokens",
        ["token_hash"],
        unique=True,
    )
    op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expires_at"])

    op.create_table(
        "password_reset_attempts",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("email_hash", sa.String(length=64), nullable=False),
        sa.Column("ip_hash", sa.String(length=64), nullable=False),
        sa.Column("requested_at", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id", name="pk_password_reset_attempts"),
    )
    op.create_index(
        "ix_password_reset_attempts_email_hash", "password_reset_attempts", ["email_hash"]
    )
    op.create_index("ix_password_reset_attempts_ip_hash", "password_reset_attempts", ["ip_hash"])
    op.create_index(
        "ix_password_reset_attempts_requested_at", "password_reset_attempts", ["requested_at"]
    )


def downgrade() -> None:
    op.drop_index("ix_password_reset_attempts_requested_at", table_name="password_reset_attempts")
    op.drop_index("ix_password_reset_attempts_ip_hash", table_name="password_reset_attempts")
    op.drop_index("ix_password_reset_attempts_email_hash", table_name="password_reset_attempts")
    op.drop_table("password_reset_attempts")
    op.drop_index("ix_password_reset_tokens_expires_at", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_token_hash", table_name="password_reset_tokens")
    op.drop_index("ix_password_reset_tokens_user_id", table_name="password_reset_tokens")
    op.drop_table("password_reset_tokens")
