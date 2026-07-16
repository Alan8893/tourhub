from uuid import uuid4

from app.models.recipe import RecipeORM


def test_recipe_equipment_requirement_crud(client, db_session):
    recipe = RecipeORM(id=str(uuid4()), name="Походный суп")
    db_session.add(recipe)
    db_session.commit()

    created = client.post(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements",
        json={"equipment_name": "  Котел   5 л ", "quantity": 2},
    )
    assert created.status_code == 201
    requirement = created.json()
    assert requirement["equipment_name"] == "Котел 5 л"
    assert requirement["quantity"] == 2

    duplicate = client.post(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements",
        json={"equipment_name": "котел 5 Л", "quantity": 1},
    )
    assert duplicate.status_code == 409

    listed = client.get(f"/api/v1/recipes/{recipe.id}/equipment-requirements")
    assert listed.status_code == 200
    assert listed.json()["items"] == [requirement]

    updated = client.put(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements/{requirement['id']}",
        json={"equipment_name": "Горелка", "quantity": 3},
    )
    assert updated.status_code == 200
    assert updated.json()["equipment_name"] == "Горелка"
    assert updated.json()["quantity"] == 3

    deleted = client.delete(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements/{requirement['id']}"
    )
    assert deleted.status_code == 204


def test_archived_recipe_equipment_is_read_only(client, db_session):
    recipe = RecipeORM(id=str(uuid4()), name="Архивный рецепт", is_archived=True)
    db_session.add(recipe)
    db_session.commit()
    response = client.post(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements",
        json={"equipment_name": "Котел", "quantity": 1},
    )
    assert response.status_code == 409


def test_recipe_equipment_quantity_must_be_positive(client, db_session):
    recipe = RecipeORM(id=str(uuid4()), name="Чай")
    db_session.add(recipe)
    db_session.commit()
    response = client.post(
        f"/api/v1/recipes/{recipe.id}/equipment-requirements",
        json={"equipment_name": "Чайник", "quantity": 0},
    )
    assert response.status_code == 422
