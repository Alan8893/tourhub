"""add dish recipe variants and project generation modes

Revision ID: h10019
Revises: h10018
Create Date: 2026-07-18
"""

from alembic import op
import sqlalchemy as sa


revision = "h10019"
down_revision = "h10018"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "dish_recipe_variants",
        sa.Column("dish_id", sa.String(), nullable=False),
        sa.Column("recipe_id", sa.String(), nullable=False),
        sa.Column("position", sa.Integer(), nullable=False),
        sa.CheckConstraint(
            "position >= 0",
            name="ck_dish_recipe_variants_position_non_negative",
        ),
        sa.ForeignKeyConstraint(
            ["dish_id"],
            ["dishes.id"],
            name="fk_dish_recipe_variants_dish_id_dishes",
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["recipe_id"],
            ["recipes.id"],
            name="fk_dish_recipe_variants_recipe_id_recipes",
            ondelete="RESTRICT",
        ),
        sa.PrimaryKeyConstraint(
            "dish_id",
            "recipe_id",
            name="pk_dish_recipe_variants",
        ),
    )
    op.create_index(
        "ix_dish_recipe_variants_recipe_id",
        "dish_recipe_variants",
        ["recipe_id"],
        unique=False,
    )
    op.execute(
        sa.text(
            "INSERT INTO dish_recipe_variants (dish_id, recipe_id, position) "
            "SELECT id, recipe_id, 0 FROM dishes"
        )
    )

    op.add_column(
        "projects",
        sa.Column(
            "recipe_generation_mode",
            sa.String(length=32),
            nullable=False,
            server_default="club_only",
        ),
    )
    op.create_check_constraint(
        "ck_projects_recipe_generation_mode",
        "projects",
        "recipe_generation_mode IN "
        "('club_only', 'club_and_personal', 'personal_preferred')",
    )

    for table_name in ("meal_slot_dishes", "meal_plan_items"):
        op.add_column(
            table_name,
            sa.Column("recipe_id", sa.String(), nullable=True),
        )
        op.execute(
            sa.text(
                f"UPDATE {table_name} AS item "
                "SET recipe_id = dishes.recipe_id "
                "FROM dishes WHERE dishes.id = item.dish_id"
            )
        )
        op.alter_column(table_name, "recipe_id", nullable=False)
        op.create_foreign_key(
            f"fk_{table_name}_recipe_id_recipes",
            table_name,
            "recipes",
            ["recipe_id"],
            ["id"],
            ondelete="RESTRICT",
        )
        op.create_index(
            f"ix_{table_name}_recipe_id",
            table_name,
            ["recipe_id"],
            unique=False,
        )


def downgrade() -> None:
    for table_name in ("meal_plan_items", "meal_slot_dishes"):
        op.drop_index(f"ix_{table_name}_recipe_id", table_name=table_name)
        op.drop_constraint(
            f"fk_{table_name}_recipe_id_recipes",
            table_name,
            type_="foreignkey",
        )
        op.drop_column(table_name, "recipe_id")

    op.drop_constraint(
        "ck_projects_recipe_generation_mode",
        "projects",
        type_="check",
    )
    op.drop_column("projects", "recipe_generation_mode")

    op.drop_index(
        "ix_dish_recipe_variants_recipe_id",
        table_name="dish_recipe_variants",
    )
    op.drop_table("dish_recipe_variants")
