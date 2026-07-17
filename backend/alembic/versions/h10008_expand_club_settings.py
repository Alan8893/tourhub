"""expand club settings foundation

Revision ID: h10008
Revises: h10007
Create Date: 2026-07-17
"""

from alembic import op
import sqlalchemy as sa


revision = "h10008"
down_revision = "h10007"
branch_labels = None
depends_on = None


OPTIONAL_STRING_COLUMNS = (
    ("short_name", 100),
    ("legal_name", 255),
    ("address", 500),
    ("phone", 100),
    ("email", 320),
    ("website", 500),
    ("timezone", 64),
    ("city", 255),
    ("region", 255),
)

IMAGE_COLUMNS = (
    "light_logo",
    "dark_logo",
    "square_icon",
    "favicon",
    "login_background",
    "document_image",
)


def upgrade() -> None:
    for column_name, length in OPTIONAL_STRING_COLUMNS:
        op.add_column(
            "club_settings",
            sa.Column(column_name, sa.String(length=length), nullable=True),
        )

    op.add_column(
        "club_settings",
        sa.Column("description", sa.Text(), nullable=True),
    )
    op.add_column(
        "club_settings",
        sa.Column(
            "social_links",
            sa.JSON(),
            nullable=False,
            server_default=sa.text("'[]'"),
        ),
    )

    for image_name in IMAGE_COLUMNS:
        op.add_column(
            "club_settings",
            sa.Column(f"{image_name}_mime_type", sa.String(length=32), nullable=True),
        )
        op.add_column(
            "club_settings",
            sa.Column(f"{image_name}_bytes", sa.LargeBinary(), nullable=True),
        )

    op.add_column(
        "club_settings",
        sa.Column(
            "version",
            sa.Integer(),
            nullable=False,
            server_default=sa.text("1"),
        ),
    )
    op.create_check_constraint(
        "ck_club_settings_version_positive",
        "club_settings",
        "version > 0",
    )

    op.create_table(
        "system_settings_history",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("section", sa.String(length=64), nullable=False),
        sa.Column("actor_label", sa.String(length=255), nullable=False),
        sa.Column("action", sa.String(length=32), nullable=False),
        sa.Column("changed_fields", sa.JSON(), nullable=False),
        sa.Column("settings_version", sa.Integer(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_system_settings_history_section",
        "system_settings_history",
        ["section"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_system_settings_history_section",
        table_name="system_settings_history",
    )
    op.drop_table("system_settings_history")

    op.drop_constraint(
        "ck_club_settings_version_positive",
        "club_settings",
        type_="check",
    )
    op.drop_column("club_settings", "version")

    for image_name in reversed(IMAGE_COLUMNS):
        op.drop_column("club_settings", f"{image_name}_bytes")
        op.drop_column("club_settings", f"{image_name}_mime_type")

    op.drop_column("club_settings", "social_links")
    op.drop_column("club_settings", "description")

    for column_name, _ in reversed(OPTIONAL_STRING_COLUMNS):
        op.drop_column("club_settings", column_name)
