"""add equipment requirements and project lists

Revision ID: h10005
Revises: h10004
Create Date: 2026-07-16
"""

from alembic import op
import sqlalchemy as sa


revision = "h10005"
down_revision = "h10004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "recipe_equipment_requirements",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("recipe_id", sa.String(), nullable=False),
        sa.Column("equipment_name", sa.String(length=255), nullable=False),
        sa.Column("quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "quantity > 0",
            name="ck_recipe_equipment_quantity_positive",
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "recipe_id",
            "equipment_name",
            name="uq_recipe_equipment_requirement_name",
        ),
    )
    op.create_index(
        op.f("ix_recipe_equipment_requirements_recipe_id"),
        "recipe_equipment_requirements",
        ["recipe_id"],
        unique=False,
    )

    op.create_table(
        "equipment_lists",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("meal_plan_id", sa.String(), nullable=False),
        sa.Column("status", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(
            ["meal_plan_id"],
            ["meal_plans.id"],
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["project_id"],
            ["projects.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("meal_plan_id"),
        sa.UniqueConstraint("project_id"),
    )
    op.create_index(
        op.f("ix_equipment_lists_meal_plan_id"),
        "equipment_lists",
        ["meal_plan_id"],
        unique=True,
    )
    op.create_index(
        op.f("ix_equipment_lists_project_id"),
        "equipment_lists",
        ["project_id"],
        unique=True,
    )

    op.create_table(
        "equipment_list_items",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("equipment_list_id", sa.String(), nullable=False),
        sa.Column("equipment_name", sa.String(length=255), nullable=False),
        sa.Column("required_quantity", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "required_quantity > 0",
            name="ck_equipment_required_quantity_positive",
        ),
        sa.ForeignKeyConstraint(
            ["equipment_list_id"],
            ["equipment_lists.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "equipment_list_id",
            "equipment_name",
            name="uq_equipment_list_item_name",
        ),
    )
    op.create_index(
        op.f("ix_equipment_list_items_equipment_list_id"),
        "equipment_list_items",
        ["equipment_list_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(
        op.f("ix_equipment_list_items_equipment_list_id"),
        table_name="equipment_list_items",
    )
    op.drop_table("equipment_list_items")
    op.drop_index(
        op.f("ix_equipment_lists_project_id"),
        table_name="equipment_lists",
    )
    op.drop_index(
        op.f("ix_equipment_lists_meal_plan_id"),
        table_name="equipment_lists",
    )
    op.drop_table("equipment_lists")
    op.drop_index(
        op.f("ix_recipe_equipment_requirements_recipe_id"),
        table_name="recipe_equipment_requirements",
    )
    op.drop_table("recipe_equipment_requirements")
