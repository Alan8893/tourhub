"""add project ownership and team

Revision ID: h10023
Revises: h10022
Create Date: 2026-07-22
"""

import sqlalchemy as sa
from alembic import op


revision = "h10023"
down_revision = "h10022"
branch_labels = None
depends_on = None


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    op.add_column(
        "projects",
        sa.Column("owner_user_id", sa.Integer(), nullable=True),
    )
    op.create_index(
        "ix_projects_owner_user_id",
        "projects",
        ["owner_user_id"],
        unique=False,
    )
    if dialect != "sqlite":
        op.create_foreign_key(
            "fk_projects_owner_user_id_users",
            "projects",
            "users",
            ["owner_user_id"],
            ["id"],
            ondelete="RESTRICT",
        )

    op.create_table(
        "project_instructors",
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("added_by_user_id", sa.Integer(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.func.now(),
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            name="fk_project_instructors_project_id_projects",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name="fk_project_instructors_user_id_users",
            ondelete="RESTRICT",
        ),
        sa.ForeignKeyConstraint(
            ["added_by_user_id"],
            ["users.id"],
            name="fk_project_instructors_added_by_user_id_users",
            ondelete="SET NULL",
        ),
        sa.PrimaryKeyConstraint(
            "project_id",
            "user_id",
            name="pk_project_instructors",
        ),
    )
    op.create_index(
        "ix_project_instructors_user_id",
        "project_instructors",
        ["user_id"],
        unique=False,
    )

    op.execute(
        sa.text(
            """
            UPDATE projects
            SET owner_user_id = COALESCE(
                (
                    SELECT audit_events.actor_user_id
                    FROM audit_events
                    WHERE audit_events.action = 'project_created'
                      AND audit_events.entity_type = 'project'
                      AND audit_events.entity_id = CAST(projects.id AS VARCHAR)
                      AND audit_events.actor_user_id IS NOT NULL
                      AND EXISTS (
                          SELECT 1
                          FROM users
                          WHERE users.id = audit_events.actor_user_id
                      )
                    ORDER BY audit_events.created_at ASC, audit_events.id ASC
                    LIMIT 1
                ),
                (
                    SELECT users.id
                    FROM users
                    WHERE users.role = 'administrator'
                    ORDER BY users.id ASC
                    LIMIT 1
                )
            )
            WHERE owner_user_id IS NULL
            """
        )
    )

    missing_owner_count = bind.execute(
        sa.text("SELECT COUNT(*) FROM projects WHERE owner_user_id IS NULL")
    ).scalar_one()
    if missing_owner_count:
        raise RuntimeError(
            "Cannot assign Project owners: no trustworthy creator or Administrator exists"
        )

    if dialect != "sqlite":
        op.alter_column(
            "projects",
            "owner_user_id",
            existing_type=sa.Integer(),
            nullable=False,
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    op.drop_index("ix_project_instructors_user_id", table_name="project_instructors")
    op.drop_table("project_instructors")
    if dialect != "sqlite":
        op.drop_constraint(
            "fk_projects_owner_user_id_users",
            "projects",
            type_="foreignkey",
        )
    op.drop_index("ix_projects_owner_user_id", table_name="projects")
    op.drop_column("projects", "owner_user_id")
