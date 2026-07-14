from app.models.dish import DishORM


def test_recipe_archive_restore_and_delete(client):
    create_response = client.post("/api/v1/recipes", json={"name": "Архивный суп"})
    assert create_response.status_code == 201
    recipe_id = create_response.json()["id"]
    assert create_response.json()["is_archived"] is False

    archive_response = client.post(f"/api/v1/recipes/{recipe_id}/archive")
    assert archive_response.status_code == 200
    assert archive_response.json()["is_archived"] is True

    active_list = client.get("/api/v1/recipes")
    assert active_list.status_code == 200
    assert active_list.json()["items"] == []

    archived_list = client.get("/api/v1/recipes?include_archived=true")
    assert archived_list.status_code == 200
    assert archived_list.json()["items"][0]["is_archived"] is True

    detail_response = client.get(f"/api/v1/recipes/{recipe_id}")
    assert detail_response.status_code == 200
    assert detail_response.json()["is_archived"] is True

    restore_response = client.post(f"/api/v1/recipes/{recipe_id}/restore")
    assert restore_response.status_code == 200
    assert restore_response.json()["is_archived"] is False

    delete_response = client.delete(f"/api/v1/recipes/{recipe_id}")
    assert delete_response.status_code == 204
    assert client.get(f"/api/v1/recipes/{recipe_id}").status_code == 404


def test_recipe_delete_is_blocked_when_used_by_dish(client, db_session):
    recipe_id = client.post(
        "/api/v1/recipes",
        json={"name": "Связанный рецепт"},
    ).json()["id"]
    db_session.add(DishORM(id="dish-linked", name="Блюдо", recipe_id=recipe_id))
    db_session.commit()
    db_session.close()

    response = client.delete(f"/api/v1/recipes/{recipe_id}")

    assert response.status_code == 409
    assert response.json()["error"] == "Recipe is used by a dish and cannot be deleted"
    assert client.get(f"/api/v1/recipes/{recipe_id}").status_code == 200
