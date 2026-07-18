"""add user administration versions

Revision ID: h10016
Revises: h10015
Create Date: 2026-07-18
"""

from alembic import op
import sqlalchemy as sa


revision = "h10016"
down_revision = "h10015"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )
    op.create_check_constraint(
        "ck_users_version_positive",
        "users",
        "version > 0",
    )


def downgrade() -> None:
    op.drop_constraint("ck_users_version_positive", "users", type_="check")
    op.drop_column("users", "version")
