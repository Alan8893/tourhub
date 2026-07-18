from collections.abc import Iterable

from fastapi.dependencies.models import Dependant
from fastapi.routing import APIRoute

from app.core.auth import require_preparation_access
from app.main import app
from app.models.user import UserORM

ADMIN_PAYLOAD = {
    "email": "admin@tourhub.local",
    "display_name": "Локальный администратор",
    "password": "correct-horse-battery-staple",
}

_PREPARATION_ENDPOINT_MODULES = {
    "app.modules.api.catalog_import_router",
    "app.modules.api.dish_router",
    "app.modules.api.equipment_list_router",
    "app.modules.api.meal_plan_router",
    "app.modules.api.meal_slot_router",
    "app.modules.api.product_router",
    "app.modules.api.project_preparation_status_router",
    "app.modules.api.purchase_checklist_router",
    "app.modules.api.purchase_dashboard_router",
    "app.modules.api.purchase_list_router",
    "app.modules.api.recipe_equipment_router",
    "app.modules.api.recipe_note_router",
    "app.modules.api.recipe_router",
    "app.modules.projects.router",
}


def _dependency_calls(dependant: Dependant) -> set[object]:
    calls: set[object] = set()
    for dependency in dependant.dependencies:
        if dependency.call is not None:
            calls.add(dependency.call)
        calls.update(_dependency_calls(dependency))
    return calls


def _route_label(route: APIRoute) -> str:
    methods = ",".join(sorted(route.methods or []))
    return f"{methods} {route.path}"


def _preparation_routes() -> Iterable[APIRoute]:
    return (
        route
        for route in app.routes
        if isinstance(route, APIRoute)
        and route.endpoint.__module__ in _PREPARATION_ENDPOINT_MODULES
    )


def _bootstrap(auth_client) -> dict:
    response = auth_client.post("/api/v1/auth/bootstrap", json=ADMIN_PAYLOAD)
    assert response.status_code == 201, response.text
    return response.json()["user"]


def test_every_preparation_endpoint_has_central_access_dependency() -> None:
    routes = list(_preparation_routes())
    assert routes
    missing = [
        _route_label(route)
        for route in routes
        if require_preparation_access not in _dependency_calls(route.dependant)
    ]
    assert missing == []


def test_public_boundaries_remain_public(auth_client) -> None:
    assert auth_client.get("/api/v1/health").status_code == 200
    assert auth_client.get("/api/v1/auth/bootstrap-status").status_code == 200
    inspection = auth_client.post(
        "/api/v1/invitations/inspect",
        json={"token": "x" * 48},
    )
    assert inspection.status_code != 401


def test_preparation_requires_session_and_all_active_roles_are_allowed(
    auth_client,
    db_session,
) -> None:
    assert auth_client.get("/api/v1/projects").status_code == 401

    current = _bootstrap(auth_client)
    assert auth_client.get("/api/v1/projects").status_code == 200

    user = db_session.get(UserORM, current["id"])
    assert user is not None
    for role in ("instructor", "verified_instructor", "administrator"):
        user.role = role
        db_session.commit()
        assert auth_client.get("/api/v1/projects").status_code == 200


def test_inactive_user_loses_preparation_access_and_admin_apis_stay_restricted(
    auth_client,
    db_session,
) -> None:
    current = _bootstrap(auth_client)
    user = db_session.get(UserORM, current["id"])
    assert user is not None

    user.role = "instructor"
    db_session.commit()
    assert auth_client.get("/api/v1/projects").status_code == 200
    assert auth_client.get("/api/v1/users").status_code == 403

    user.is_active = False
    db_session.commit()
    assert auth_client.get("/api/v1/projects").status_code == 401
