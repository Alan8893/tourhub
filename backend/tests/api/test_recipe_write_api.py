from app.models.product import ProductORM


def test_recipe_write_workflow(client, db_session):
    product = ProductORM(
        id="product-1",
        name="Гречка",
        category="Крупы",
        unit="gram",
        package_size=800,
    )
    db_session.add(product)
    db_session.commit()

    products_response = client.get("/api/v1/products")
    assert products_response.status_code == 200
    assert products_response.json()["items"][0]["name"] == "Гречка"

    create_response = client.post("/api/v1/recipes", json={"name": "Походная каша"})
    assert create_response.status_code == 201
    recipe_id = create_response.json()["id"]

    rename_response = client.patch(
        f"/api/v1/recipes/{recipe_id}",
        json={"name": "Гречневая каша"},
    )
    assert rename_response.status_code == 200
    assert rename_response.json()["name"] == "Гречневая каша"

    component_response = client.post(
        f"/api/v1/recipes/{recipe_id}/components",
        json={
            "product_id": "product-1",
            "component_type": "base",
            "amount": 80,
            "unit": "gram",
            "calculation_type": "per_person",
            "people_count": None,
        },
    )
    assert component_response.status_code == 201
    component_id = component_response.json()["id"]
    assert component_response.json()["product"]["name"] == "Гречка"

    update_response = client.put(
        f"/api/v1/recipes/{recipe_id}/components/{component_id}",
        json={
            "product_id": "product-1",
            "component_type": "cooking",
            "amount": 2,
            "unit": "package",
            "calculation_type": "package_per_people",
            "people_count": 4,
        },
    )
    assert update_response.status_code == 200
    assert update_response.json()["component_type"] == "cooking"
    assert update_response.json()["people_count"] == 4

    detail_response = client.get(f"/api/v1/recipes/{recipe_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["components"][0]["amount"] == 2

    delete_response = client.delete(
        f"/api/v1/recipes/{recipe_id}/components/{component_id}"
    )
    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/recipes/{recipe_id}").json()["components"] == []


def test_recipe_component_validates_package_people_count(client, db_session):
    db_session.add(ProductORM(id="product-1", name="Рис", unit="gram"))
    db_session.commit()
    recipe_id = client.post("/api/v1/recipes", json={"name": "Рисовая каша"}).json()["id"]

    response = client.post(
        f"/api/v1/recipes/{recipe_id}/components",
        json={
            "product_id": "product-1",
            "component_type": "base",
            "amount": 1,
            "unit": "package",
            "calculation_type": "package_per_people",
        },
    )

    assert response.status_code == 422


def test_recipe_name_must_be_unique(client):
    assert client.post("/api/v1/recipes", json={"name": "Суп"}).status_code == 201
    response = client.post("/api/v1/recipes", json={"name": "Суп"})
    assert response.status_code == 409
    assert response.json()["error"] == "Recipe name must be unique"
