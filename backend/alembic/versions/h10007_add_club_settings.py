"""add club settings

Revision ID: h10007
Revises: h10006
Create Date: 2026-07-17
"""

from alembic import op
import sqlalchemy as sa


revision = "h10007"
down_revision = "h10006"
branch_labels = None
depends_on = None


def upgrade() -> None:
    club_settings = op.create_table(
        "club_settings",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("club_name", sa.String(length=255), nullable=False),
        sa.Column("logo_mime_type", sa.String(length=32), nullable=True),
        sa.Column("logo_bytes", sa.LargeBinary(), nullable=True),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.CheckConstraint("id = 1", name="ck_club_settings_singleton"),
    )
    op.bulk_insert(club_settings, [{"id": 1, "club_name": "TourHub"}])


def downgrade() -> None:
    op.drop_table("club_settings")
