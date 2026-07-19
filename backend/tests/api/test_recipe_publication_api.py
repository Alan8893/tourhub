from fastapi.testclient import TestClient

from app.main import app
from app.models.recipe import RecipeORM
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


def add_user(
    db_session,
    *,
    email: str,
    display_name: str,
    role: str,
) -> UserORM:
    user = UserORM(
        email=email,
        display_name=display_name,
        role=role,
        password_hash=hash_password(MEMBER_PASSWORD),
        is_active=True,
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


def logged_in_client(email: str) -> TestClient:
    client = TestClient(app)
    response = client.post(
        "/api/v1/auth/login",
        json={"email": email, "password": MEMBER_PASSWORD},
    )
    assert response.status_code == 200, response.text
    return client


def create_personal_recipe(client: TestClient, name: str) -> dict:
    response = client.post("/api/v1/recipes", json={"name": name})
    assert response.status_code == 201, response.text
    return response.json()


def test_submitted_recipe_is_locked_and_instructor_cannot_open_moderation(
    auth_client,
    db_session,
) -> None:
    bootstrap(auth_client)
    owner = add_user(
        db_session,
        email="owner-lock@example.org",
        display_name="Инструктор",
        role="instructor",
    )
    owner_client = logged_in_client(owner.email)

    try:
        created = create_personal_recipe(owner_client, "Личный суп")
        assert created["lifecycle_status"] == "draft"
        assert created["can_submit"] is True

        submitted = owner_client.post(f"/api/v1/recipes/{created['id']}/submit")
        assert submitted.status_code == 200, submitted.text
        body = submitted.json()
        assert body["lifecycle_status"] == "submitted"
        assert body["submitted_by_user_id"] == owner.id
        assert body["submitted_by_display_name"] == "Инструктор"
        assert body["submitted_at"] is not None
        assert body["can_edit"] is False
        assert body["can_archive"] is False
        assert body["can_submit"] is False

        rename = owner_client.patch(
            f"/api/v1/recipes/{created['id']}",
            json={"name": "Изменённый суп"},
        )
        assert rename.status_code == 409
        assert rename.json()["error"] == "Submitted recipe cannot be edited"

        note = owner_client.post(
            f"/api/v1/recipes/{created['id']}/notes",
            json={"type": "cooking_tip", "text": "Нельзя", "priority": 0},
        )
        assert note.status_code == 409
        assert note.json()["error"] == "Submitted recipe cannot be edited"

        archive = owner_client.post(f"/api/v1/recipes/{created['id']}/archive")
        assert archive.status_code == 409
        assert archive.json()["error"] == "Submitted recipe cannot be archived"

        moderation = owner_client.get("/api/v1/recipes", params={"view": "moderation"})
        assert moderation.status_code == 403
    finally:
        owner_client.close()


def test_verified_instructor_rejects_and_owner_resubmits(
    auth_client,
    db_session,
) -> None:
    bootstrap(auth_client)
    owner = add_user(
        db_session,
        email="owner-reject@example.org",
        display_name="Автор рецепта",
        role="instructor",
    )
    reviewer = add_user(
        db_session,
        email="reviewer@example.org",
        display_name="Проверяющий",
        role="verified_instructor",
    )
    owner_client = logged_in_client(owner.email)
    reviewer_client = logged_in_client(reviewer.email)

    try:
        created = create_personal_recipe(owner_client, "Каша на проверку")
        submitted = owner_client.post(f"/api/v1/recipes/{created['id']}/submit")
        assert submitted.status_code == 200, submitted.text

        queue = reviewer_client.get("/api/v1/recipes", params={"view": "moderation"})
        assert queue.status_code == 200, queue.text
        items = queue.json()["items"]
        assert [item["id"] for item in items] == [created["id"]]
        assert items[0]["can_publish"] is True
        assert items[0]["can_reject"] is True

        rejected = reviewer_client.post(
            f"/api/v1/recipes/{created['id']}/reject",
            json={"comment": "  Добавьте точное время приготовления.  "},
        )
        assert rejected.status_code == 200, rejected.text
        rejected_body = rejected.json()
        assert rejected_body["lifecycle_status"] == "rejected"
        assert rejected_body["review_comment"] == "Добавьте точное время приготовления."
        assert rejected_body["reviewed_by_user_id"] == reviewer.id
        assert rejected_body["reviewed_by_display_name"] == "Проверяющий"
        assert rejected_body["reviewed_at"] is not None

        owner_view = owner_client.get(f"/api/v1/recipes/{created['id']}")
        assert owner_view.status_code == 200, owner_view.text
        assert owner_view.json()["can_edit"] is True
        assert owner_view.json()["can_submit"] is True
        assert owner_view.json()["review_comment"] == rejected_body["review_comment"]

        renamed = owner_client.patch(
            f"/api/v1/recipes/{created['id']}",
            json={"name": "Каша с технологией"},
        )
        assert renamed.status_code == 200, renamed.text

        resubmitted = owner_client.post(f"/api/v1/recipes/{created['id']}/submit")
        assert resubmitted.status_code == 200, resubmitted.text
        resubmitted_body = resubmitted.json()
        assert resubmitted_body["lifecycle_status"] == "submitted"
        assert resubmitted_body["review_comment"] is None
        assert resubmitted_body["reviewed_by_user_id"] is None
        assert resubmitted_body["reviewed_at"] is None
    finally:
        owner_client.close()
        reviewer_client.close()


def test_publication_converts_recipe_to_club_and_creates_unclassified_dish(
    auth_client,
    db_session,
) -> None:
    bootstrap(auth_client)
    owner = add_user(
        db_session,
        email="owner-publish@example.org",
        display_name="Автор публикации",
        role="instructor",
    )
    reviewer = add_user(
        db_session,
        email="publisher@example.org",
        display_name="Верифицированный инструктор",
        role="verified_instructor",
    )
    reader = add_user(
        db_session,
        email="reader@example.org",
        display_name="Читатель",
        role="instructor",
    )
    owner_client = logged_in_client(owner.email)
    reviewer_client = logged_in_client(reviewer.email)
    reader_client = logged_in_client(reader.email)

    try:
        created = create_personal_recipe(owner_client, "Публикуемый плов")
        assert owner_client.post(f"/api/v1/recipes/{created['id']}/submit").status_code == 200

        published = reviewer_client.post(f"/api/v1/recipes/{created['id']}/publish")
        assert published.status_code == 200, published.text
        body = published.json()
        assert body["scope"] == "club"
        assert body["lifecycle_status"] == "published"
        assert body["owner_user_id"] is None
        assert body["submitted_by_user_id"] == owner.id
        assert body["submitted_by_display_name"] == "Автор публикации"
        assert body["reviewed_by_user_id"] == reviewer.id
        assert body["reviewed_by_display_name"] == "Верифицированный инструктор"
        assert body["can_edit"] is True
        assert body["can_publish"] is False

        catalogue = reviewer_client.get("/api/v1/dishes")
        assert catalogue.status_code == 200, catalogue.text
        dishes = catalogue.json()["items"]
        assert len(dishes) == 1
        dish = dishes[0]
        assert dish["name"] == "Публикуемый плов"
        assert dish["recipe"]["id"] == created["id"]
        assert [(item["id"], item["is_default"]) for item in dish["recipes"]] == [
            (created["id"], True)
        ]
        assert dish["meal_roles"] == []

        readiness = reviewer_client.get("/api/v1/dishes/catalogue-readiness")
        assert readiness.status_code == 200, readiness.text
        assert readiness.json()["active_dish_count"] == 1
        assert readiness.json()["unclassified_dish_count"] == 1

        repeated = reviewer_client.post(f"/api/v1/recipes/{created['id']}/publish")
        assert repeated.status_code == 409
        assert len(reviewer_client.get("/api/v1/dishes").json()["items"]) == 1

        reader_view = reader_client.get(f"/api/v1/recipes/{created['id']}")
        assert reader_view.status_code == 200, reader_view.text
        assert reader_view.json()["scope"] == "club"
        assert reader_view.json()["can_edit"] is False

        db_session.expire_all()
        stored = db_session.get(RecipeORM, created["id"])
        assert stored is not None
        assert stored.scope == "club"
        assert stored.owner_user_id is None
        assert stored.lifecycle_status == "published"
        assert stored.submitted_by_user_id == owner.id
        assert stored.reviewed_by_user_id == reviewer.id
    finally:
        owner_client.close()
        reviewer_client.close()
        reader_client.close()


def test_verified_instructor_cannot_review_own_submission(
    auth_client,
    db_session,
) -> None:
    bootstrap(auth_client)
    verified = add_user(
        db_session,
        email="self-review@example.org",
        display_name="Сам себе проверяющий",
        role="verified_instructor",
    )
    client = logged_in_client(verified.email)

    try:
        created = create_personal_recipe(client, "Собственный рецепт")
        assert client.post(f"/api/v1/recipes/{created['id']}/submit").status_code == 200

        queue = client.get("/api/v1/recipes", params={"view": "moderation"})
        assert queue.status_code == 200, queue.text
        assert queue.json()["items"] == []

        publish = client.post(f"/api/v1/recipes/{created['id']}/publish")
        assert publish.status_code == 403
        assert publish.json()["error"] == "Verified instructor cannot review their own recipe"
    finally:
        client.close()
