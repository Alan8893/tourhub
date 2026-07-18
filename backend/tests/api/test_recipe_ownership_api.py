from fastapi.testclient import TestClient

from app.main import app
from app.models.recipe import RecipeORM
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM
from app.services.auth_service import hash_password

ADMIN_PASSWORD = "correct-horse-battery-staple"
MEMBER_PASSWORD = "member-password-12345"


def bootstrap(client: TestClient) -> dict:
    response = client.post(
        "/api/v1/auth/bootstrap",
        json={
            "email": "admin@tourhub.local",
            "display_name": "Администратор",
            "password": ADMIN_PASSWORD,
        },
    )
    assert response.status_code == 201, response.text
    return response.json()["user"]


def add_user(db_session, *, email: str, role: str) -> UserORM:
    user = UserORM(
        email=email,
        display_name=email.split("@", 1)[0],
        role=role,
        password_hash=hash_password(MEMBER_PASSWORD),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def add_recipe(
    db_session,
    *,
    recipe_id: str,
    name: str,
    scope: RecipeScope,
    owner_user_id: int | None = None,
) -> RecipeORM:
    recipe = RecipeORM(
        id=recipe_id,
        name=name,
        scope=scope.value,
        owner_user_id=owner_user_id,
    )
    db_session.add(recipe)
    db_session.commit()
    db_session.refresh(recipe)
    return recipe


def logged_in_client(email: str) -> TestClient:
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": MEMBER_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return client


def test_interactive_recipe_creation_is_personal_and_owned(auth_client, db_session) -> None:
    administrator = bootstrap(auth_client)

    response = auth_client.post("/api/v1/recipes", json={"name": "Личный суп"})

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["scope"] == "personal"
    assert body["owner_user_id"] == administrator["id"]
    assert body["owner_display_name"] == "Администратор"
    assert body["is_owned_by_current_user"] is True
    assert body["can_edit"] is True
    assert body["can_delete"] is True

    stored = db_session.get(RecipeORM, body["id"])
    assert stored is not None
    assert stored.scope == RecipeScope.PERSONAL.value
    assert stored.owner_user_id == administrator["id"]


def test_instructor_lists_club_and_owned_personal_recipes_only(
    auth_client,
    db_session,
) -> None:
    bootstrap(auth_client)
    owner = add_user(db_session, email="owner@example.org", role="instructor")
    other = add_user(db_session, email="other@example.org", role="instructor")
    club = add_recipe(
        db_session,
        recipe_id="club-recipe",
        name="Клубный плов",
        scope=RecipeScope.CLUB,
    )
    owned = add_recipe(
        db_session,
        recipe_id="owned-recipe",
        name="Личная каша",
        scope=RecipeScope.PERSONAL,
        owner_user_id=owner.id,
    )
    hidden = add_recipe(
        db_session,
        recipe_id="hidden-recipe",
        name="Чужой суп",
        scope=RecipeScope.PERSONAL,
        owner_user_id=other.id,
    )
    client = logged_in_client(owner.email)

    try:
        response = client.get("/api/v1/recipes")
        assert response.status_code == 200, response.text
        items = {item["id"]: item for item in response.json()["items"]}
        assert set(items) == {club.id, owned.id}
        assert items[club.id]["scope"] == "club"
        assert items[club.id]["can_edit"] is False
        assert items[owned.id]["is_owned_by_current_user"] is True
        assert items[owned.id]["can_edit"] is True
        assert client.get(f"/api/v1/recipes/{hidden.id}").status_code == 404
    finally:
        client.close()


def test_role_policy_protects_recipe_root_and_nested_mutations(
    auth_client,
    db_session,
) -> None:
    bootstrap(auth_client)
    instructor = add_user(db_session, email="instructor@example.org", role="instructor")
    verified = add_user(
        db_session,
        email="verified@example.org",
        role="verified_instructor",
    )
    club = add_recipe(
        db_session,
        recipe_id="shared-club-recipe",
        name="Клубный борщ",
        scope=RecipeScope.CLUB,
    )
    instructor_client = logged_in_client(instructor.email)
    verified_client = logged_in_client(verified.email)

    try:
        rename = instructor_client.patch(
            f"/api/v1/recipes/{club.id}",
            json={"name": "Недопустимое имя"},
        )
        assert rename.status_code == 403

        note = instructor_client.post(
            f"/api/v1/recipes/{club.id}/notes",
            json={"type": "cooking_tip", "text": "Нельзя", "priority": 0},
        )
        assert note.status_code == 403

        equipment = instructor_client.post(
            f"/api/v1/recipes/{club.id}/equipment-requirements",
            json={"equipment_name": "Котёл", "quantity": 1},
        )
        assert equipment.status_code == 403

        verified_rename = verified_client.patch(
            f"/api/v1/recipes/{club.id}",
            json={"name": "Клубный борщ обновлён"},
        )
        assert verified_rename.status_code == 200, verified_rename.text
        assert verified_rename.json()["can_edit"] is True
        assert verified_rename.json()["can_delete"] is False
    finally:
        instructor_client.close()
        verified_client.close()


def test_only_administrator_may_permanently_delete_recipe(auth_client, db_session) -> None:
    bootstrap(auth_client)
    instructor = add_user(db_session, email="owner-delete@example.org", role="instructor")
    personal = add_recipe(
        db_session,
        recipe_id="personal-delete-recipe",
        name="Черновик для удаления",
        scope=RecipeScope.PERSONAL,
        owner_user_id=instructor.id,
    )
    client = logged_in_client(instructor.email)

    try:
        assert client.delete(f"/api/v1/recipes/{personal.id}").status_code == 403
    finally:
        client.close()

    admin_list = auth_client.get("/api/v1/recipes")
    assert admin_list.status_code == 200
    item = next(item for item in admin_list.json()["items"] if item["id"] == personal.id)
    assert item["can_delete"] is True
    assert auth_client.delete(f"/api/v1/recipes/{personal.id}").status_code == 204
