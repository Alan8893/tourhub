"""add mail settings

Revision ID: h10013
Revises: h10012
Create Date: 2026-07-17
"""

from alembic import op
import sqlalchemy as sa

revision = "h10013"
down_revision = "h10012"
branch_labels = None
depends_on = None


def upgrade() -> None:
    table = op.create_table(
        "mail_settings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("smtp_host", sa.String(length=253), nullable=False),
        sa.Column("smtp_port", sa.Integer(), nullable=False),
        sa.Column("security_mode", sa.String(length=16), nullable=False),
        sa.Column("smtp_username", sa.String(length=255), nullable=True),
        sa.Column("sender_email", sa.String(length=320), nullable=False),
        sa.Column("sender_name", sa.String(length=120), nullable=False),
        sa.Column("reply_to_email", sa.String(length=320), nullable=True),
        sa.Column("test_recipient_email", sa.String(length=320), nullable=True),
        sa.Column("timeout_seconds", sa.Integer(), nullable=False),
        sa.Column("retry_count", sa.Integer(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.CheckConstraint("id = 1", name="ck_mail_settings_singleton"),
        sa.CheckConstraint("version > 0", name="ck_mail_settings_version_positive"),
        sa.CheckConstraint("smtp_port BETWEEN 1 AND 65535", name="ck_mail_settings_port_range"),
        sa.CheckConstraint(
            "security_mode IN ('plain', 'starttls', 'tls')",
            name="ck_mail_settings_security_mode",
        ),
        sa.CheckConstraint(
            "timeout_seconds BETWEEN 1 AND 120",
            name="ck_mail_settings_timeout_range",
        ),
        sa.CheckConstraint("retry_count BETWEEN 0 AND 10", name="ck_mail_settings_retry_range"),
        sa.CheckConstraint("smtp_host <> ''", name="ck_mail_settings_host_required"),
        sa.CheckConstraint("sender_email <> ''", name="ck_mail_settings_sender_required"),
        sa.CheckConstraint("sender_name <> ''", name="ck_mail_settings_sender_name_required"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.bulk_insert(
        table,
        [
            {
                "id": 1,
                "smtp_host": "localhost",
                "smtp_port": 587,
                "security_mode": "starttls",
                "smtp_username": None,
                "sender_email": "tourhub@localhost",
                "sender_name": "TourHub",
                "reply_to_email": None,
                "test_recipient_email": None,
                "timeout_seconds": 30,
                "retry_count": 3,
                "version": 1,
            }
        ],
    )


def downgrade() -> None:
    op.drop_table("mail_settings")
