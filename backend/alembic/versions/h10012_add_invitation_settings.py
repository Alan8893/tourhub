"""add typed invitation settings

Revision ID: h10012
Revises: h10011
Create Date: 2026-07-17
"""

from alembic import op
import sqlalchemy as sa


revision = "h10012"
down_revision = "h10011"
branch_labels = None
depends_on = None


def upgrade() -> None:
    invitation_settings = op.create_table(
        "invitation_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("expires_after_days", sa.Integer(), nullable=False),
        sa.Column("default_role", sa.String(length=32), nullable=False),
        sa.Column("allowed_email_domains", sa.JSON(), nullable=False),
        sa.Column("allow_resend", sa.Boolean(), nullable=False),
        sa.Column("active_invitation_limit", sa.Integer(), nullable=False),
        sa.Column("administrators_only", sa.Boolean(), nullable=False),
        sa.Column("require_email_confirmation", sa.Boolean(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("id = 1", name="ck_invitation_settings_singleton"),
        sa.CheckConstraint(
            "version > 0",
            name="ck_invitation_settings_version_positive",
        ),
        sa.CheckConstraint(
            "expires_after_days BETWEEN 1 AND 90",
            name="ck_invitation_settings_expiry_range",
        ),
        sa.CheckConstraint(
            "active_invitation_limit BETWEEN 1 AND 1000",
            name="ck_invitation_settings_active_limit_range",
        ),
        sa.CheckConstraint(
            "default_role IN ('instructor', 'verified_instructor')",
            name="ck_invitation_settings_safe_default_role",
        ),
        sa.CheckConstraint(
            "administrators_only",
            name="ck_invitation_settings_administrators_only",
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.bulk_insert(
        invitation_settings,
        [
            {
                "id": 1,
                "expires_after_days": 7,
                "default_role": "instructor",
                "allowed_email_domains": [],
                "allow_resend": True,
                "active_invitation_limit": 100,
                "administrators_only": True,
                "require_email_confirmation": True,
                "version": 1,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("invitation_settings")
