PRODUCTS_CSV = """name;category;unit;package_size
Гречка;Крупы;gram;800
Тушёнка;Консервы;can;1
"""

RECIPES_CSV = """recipe_name;product_name;component_type;amount;unit;calculation_type;people_count;note_type;note_text;note_priority
Походная гречка;Гречка;base;80;gram;per_person;;;Промыть крупу;10
Походная гречка;Тушёнка;cooking;1;can;package_per_people;4;expedition_tip;Открыть перед подачей;20
"""


def test_product_import_preview_does_not_write(client):
    preview = client.post(
        "/api/v1/catalog-import/preview",
        json={"kind": "products", "content": PRODUCTS_CSV},
    )

    assert preview.status_code == 200
    assert preview.json()["valid"] is True
    assert preview.json()["create_count"] == 2
    assert client.get("/api/v1/products").json()["items"] == []


def test_product_import_apply_creates_and_then_skips_existing(client):
    first = client.post(
        "/api/v1/catalog-import/apply",
        json={"kind": "products", "content": PRODUCTS_CSV},
    )
    second = client.post(
        "/api/v1/catalog-import/preview",
        json={"kind": "products", "content": PRODUCTS_CSV},
    )

    assert first.status_code == 200
    assert first.json()["create_count"] == 2
    assert second.json()["create_count"] == 0
    assert second.json()["skip_count"] == 2
    assert len(client.get("/api/v1/products").json()["items"]) == 2


def test_recipe_import_rejects_unknown_product(client):
    response = client.post(
        "/api/v1/catalog-import/preview",
        json={"kind": "recipes", "content": RECIPES_CSV},
    )

    assert response.status_code == 200
    assert response.json()["valid"] is False
    assert any(error["field"] == "product_name" for error in response.json()["errors"])


def test_recipe_import_creates_recipe_components_and_notes(client):
    client.post(
        "/api/v1/catalog-import/apply",
        json={"kind": "products", "content": PRODUCTS_CSV},
    )

    response = client.post(
        "/api/v1/catalog-import/apply",
        json={"kind": "recipes", "content": RECIPES_CSV},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["valid"] is True
    assert data["create_count"] == 1
    assert data["component_count"] == 2
    assert data["note_count"] == 2

    recipes = client.get("/api/v1/recipes").json()["items"]
    assert len(recipes) == 1
    detail = client.get(f"/api/v1/recipes/{recipes[0]['id']}").json()
    assert len(detail["components"]) == 2
    assert len(detail["notes"]) == 2
