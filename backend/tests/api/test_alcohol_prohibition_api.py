from app.models.dish import DishORM
from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM


def _published_recipe(
    *,
    recipe_id: str,
    name: str,
    product: ProductORM | None = None,
) -> RecipeORM:
    recipe = RecipeORM(
        id=recipe_id,
        name=name,
        scope="club",
        lifecycle_status="published",
    )
    if product is not None:
        recipe.components.append(
            RecipeComponentORM(
                id=f"component-{recipe_id}",
                product=product,
                component_type="base",
                amount=10,
                unit="gram",
                calculation_type="per_person",
            )
        )
    return recipe


def test_product_api_rejects_alcohol_and_allows_unrelated_words(client) -> None:
    rejected = client.post(
        "/api/v1/products",
        json={
            "name": "Красное вино",
            "category": "Напитки",
            "unit": "millilitre",
            "package_size": 750,
        },
    )
    allowed = client.post(
        "/api/v1/products",
        json={
            "name": "Ромашка сушёная",
            "category": "Травы",
            "unit": "gram",
            "package_size": 50,
        },
    )

    assert rejected.status_code == 422
    assert rejected.json()["error"] == "Алкоголь запрещён в TourHub без исключений."
    assert allowed.status_code == 201
    assert [item["name"] for item in client.get("/api/v1/products").json()["items"]] == [
        "Ромашка сушёная"
    ]


def test_recipe_name_and_alcohol_product_component_are_rejected(
    client,
    db_session,
) -> None:
    rejected_recipe = client.post(
        "/api/v1/recipes",
        json={"name": "Чай с ромом"},
    )
    assert rejected_recipe.status_code == 422

    recipe_response = client.post(
        "/api/v1/recipes",
        json={"name": "Лесной чай"},
    )
    assert recipe_response.status_code == 201
    recipe_id = recipe_response.json()["id"]

    prohibited_product = ProductORM(
        id="alcohol-product",
        name="Водка",
        category="Напитки",
        unit="millilitre",
        package_size=500,
    )
    db_session.add(prohibited_product)
    db_session.commit()

    component_response = client.post(
        f"/api/v1/recipes/{recipe_id}/components",
        json={
            "product_id": prohibited_product.id,
            "component_type": "base",
            "amount": 10,
            "unit": "millilitre",
            "calculation_type": "per_person",
            "people_count": None,
        },
    )

    assert component_response.status_code == 422
    assert component_response.json()["error"] == (
        "Алкоголь запрещён в TourHub без исключений."
    )


def test_dish_api_rejects_alcohol_name_and_prohibited_default_recipe(
    client,
    db_session,
) -> None:
    allowed_recipe = _published_recipe(recipe_id="allowed-recipe", name="Компот")
    prohibited_product = ProductORM(
        id="wine-product",
        name="Wine",
        category="Drinks",
        unit="millilitre",
        package_size=750,
    )
    prohibited_recipe = _published_recipe(
        recipe_id="prohibited-recipe",
        name="Соус",
        product=prohibited_product,
    )
    db_session.add_all([allowed_recipe, prohibited_recipe])
    db_session.commit()

    name_response = client.post(
        "/api/v1/dishes",
        json={
            "name": "Пиво к ужину",
            "recipe_id": allowed_recipe.id,
            "recipe_ids": [],
        },
    )
    recipe_response = client.post(
        "/api/v1/dishes",
        json={
            "name": "Вечерний напиток",
            "recipe_id": prohibited_recipe.id,
            "recipe_ids": [],
        },
    )

    assert name_response.status_code == 422
    assert recipe_response.status_code == 422
    assert client.get("/api/v1/dishes").json()["items"] == []


def test_product_and_recipe_import_use_the_same_policy(client) -> None:
    products_csv = """name;category;unit;package_size
Виски;Напитки;millilitre;500
"""
    product_preview = client.post(
        "/api/v1/catalog-import/preview",
        json={"kind": "products", "content": products_csv},
    )
    product_apply = client.post(
        "/api/v1/catalog-import/apply",
        json={"kind": "products", "content": products_csv},
    )

    assert product_preview.status_code == 200
    assert product_preview.json()["valid"] is False
    assert product_apply.json()["valid"] is False
    assert client.get("/api/v1/products").json()["items"] == []

    client.post(
        "/api/v1/products",
        json={
            "name": "Чай",
            "category": "Напитки",
            "unit": "gram",
            "package_size": 100,
        },
    )
    recipes_csv = """recipe_name;product_name;component_type;amount;unit;calculation_type;people_count;note_type;note_text;note_priority
Чай с вином;Чай;base;10;gram;per_person;;;;100
"""
    recipe_preview = client.post(
        "/api/v1/catalog-import/preview",
        json={"kind": "recipes", "content": recipes_csv},
    )

    assert recipe_preview.status_code == 200
    assert recipe_preview.json()["valid"] is False
    assert any(
        error["field"] == "recipe_name"
        and "Алкоголь запрещён" in error["message"]
        for error in recipe_preview.json()["errors"]
    )


def test_policy_archived_products_and_dishes_are_hidden_from_active_catalogues(
    client,
    db_session,
) -> None:
    archived_product = ProductORM(
        id="archived-product",
        name="Старый продукт",
        category="Архив",
        unit="gram",
        package_size=100,
        is_archived=True,
        archived_by_alcohol_policy=True,
    )
    recipe = _published_recipe(recipe_id="historical-recipe", name="Исторический рецепт")
    archived_dish = DishORM(
        id="archived-dish",
        name="Историческое блюдо",
        recipe_id=recipe.id,
        is_archived=True,
        archived_by_alcohol_policy=True,
    )
    db_session.add_all([archived_product, recipe, archived_dish])
    db_session.commit()

    assert client.get("/api/v1/products").json()["items"] == []
    assert client.get("/api/v1/dishes").json()["items"] == []
