"""enforce centralized alcohol prohibition

Revision ID: h10021
Revises: h10020
Create Date: 2026-07-19
"""

import re
import unicodedata

from alembic import op
import sqlalchemy as sa


revision = "h10021"
down_revision = "h10020"
branch_labels = None
depends_on = None

_TOKEN_PATTERN = re.compile(r"[\w]+", flags=re.UNICODE)
_POLICY_TERMS_V1 = frozenset(
    """
    алкоголь алкоголя алкогольный алкогольная алкогольное алкогольные
    спирт спирта спиртом спиртное спиртные
    водка водки водку водкой водке
    вино вина вину вином вине
    пиво пива пиву пивом пиве
    сидр сидра сидру сидром сидре
    шампанское шампанского шампанским шампанском
    коньяк коньяка коньяку коньяком коньяке
    виски
    ром рома рому ромом роме
    джин джина джину джином джине
    текила текилы текилу текилой текиле
    ликер ликера ликеру ликером ликере
    вермут вермута вермуту вермутом вермуте
    медовуха медовухи медовуху медовухой медовухе
    самогон самогона самогону самогоном самогоне
    настойка настойки настойку настойкой настойке
    наливка наливки наливку наливкой наливке
    мартини саке бренди
    бурбон бурбона бурбону бурбоном бурбоне
    абсент абсента абсенту абсентом абсенте
    кальвадос кальвадоса кальвадосу кальвадосом кальвадосе
    граппа граппы граппу граппой граппе
    портвейн портвейна портвейну портвейном портвейне
    херес хереса хересу хересом хересе
    мадера мадеры мадеру мадерой мадере
    beer wine vodka cider champagne cognac whisky whiskey rum gin tequila
    liqueur liquor vermouth mead moonshine sake brandy bourbon absinthe
    """.split()
)


def _is_prohibited(*values: str | None) -> bool:
    combined = " ".join(value for value in values if value)
    normalized = unicodedata.normalize("NFKC", combined).casefold().replace("ё", "е")
    return any(token in _POLICY_TERMS_V1 for token in _TOKEN_PATTERN.findall(normalized))


def upgrade() -> None:
    for table_name in ("products", "dishes"):
        op.add_column(
            table_name,
            sa.Column(
                "is_archived",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
        op.add_column(
            table_name,
            sa.Column(
                "archived_by_alcohol_policy",
                sa.Boolean(),
                nullable=False,
                server_default=sa.false(),
            ),
        )
        op.create_index(
            f"ix_{table_name}_is_archived",
            table_name,
            ["is_archived"],
            unique=False,
        )

    op.add_column(
        "recipes",
        sa.Column(
            "archived_by_alcohol_policy",
            sa.Boolean(),
            nullable=False,
            server_default=sa.false(),
        ),
    )
    op.create_index(
        "ix_recipes_archived_by_alcohol_policy",
        "recipes",
        ["archived_by_alcohol_policy"],
        unique=False,
    )

    connection = op.get_bind()
    prohibited_product_ids = {
        row.id
        for row in connection.execute(
            sa.text("SELECT id, name, category FROM products")
        ).mappings()
        if _is_prohibited(row.name, row.category)
    }
    if prohibited_product_ids:
        connection.execute(
            sa.text(
                "UPDATE products SET is_archived = true, "
                "archived_by_alcohol_policy = true WHERE id IN :ids"
            ).bindparams(sa.bindparam("ids", expanding=True)),
            {"ids": sorted(prohibited_product_ids)},
        )

    prohibited_recipe_ids = {
        row.id
        for row in connection.execute(sa.text("SELECT id, name FROM recipes")).mappings()
        if _is_prohibited(row.name)
    }
    if prohibited_product_ids:
        prohibited_recipe_ids.update(
            row.recipe_id
            for row in connection.execute(
                sa.text(
                    "SELECT DISTINCT recipe_id FROM recipe_components "
                    "WHERE product_id IN :ids"
                ).bindparams(sa.bindparam("ids", expanding=True)),
                {"ids": sorted(prohibited_product_ids)},
            ).mappings()
        )
    if prohibited_recipe_ids:
        connection.execute(
            sa.text(
                "UPDATE recipes SET is_archived = true, "
                "archived_by_alcohol_policy = true WHERE id IN :ids"
            ).bindparams(sa.bindparam("ids", expanding=True)),
            {"ids": sorted(prohibited_recipe_ids)},
        )

    prohibited_dish_ids = {
        row.id
        for row in connection.execute(
            sa.text("SELECT id, name, recipe_id FROM dishes")
        ).mappings()
        if _is_prohibited(row.name) or row.recipe_id in prohibited_recipe_ids
    }
    if prohibited_dish_ids:
        connection.execute(
            sa.text(
                "UPDATE dishes SET is_archived = true, "
                "archived_by_alcohol_policy = true WHERE id IN :ids"
            ).bindparams(sa.bindparam("ids", expanding=True)),
            {"ids": sorted(prohibited_dish_ids)},
        )


def downgrade() -> None:
    connection = op.get_bind()
    connection.execute(
        sa.text(
            "UPDATE recipes SET is_archived = false "
            "WHERE archived_by_alcohol_policy = true"
        )
    )
    op.drop_index("ix_recipes_archived_by_alcohol_policy", table_name="recipes")
    op.drop_column("recipes", "archived_by_alcohol_policy")

    for table_name in ("dishes", "products"):
        op.drop_index(f"ix_{table_name}_is_archived", table_name=table_name)
        op.drop_column(table_name, "archived_by_alcohol_policy")
        op.drop_column(table_name, "is_archived")
