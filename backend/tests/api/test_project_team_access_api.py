import pytest
from sqlalchemy import func, select

from app.core.auth import require_preparation_access
from app.main import app
from app.models.audit_event import AuditEventORM
from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.models.project_instructor import ProjectInstructorORM
from app.services.audit_service import AuditService
from app.services.project_team_service import ProjectTeamService


def _user(
    user_id: int,
    name: str,
    role: str = "instructor",
    *,
    active: bool = True,
) -> UserORM:
    return UserORM(
        id=user_id,
        email=f"user{user_id}@example.org",
        display_name=name,
        phone=f"+799900000{user_id:02d}",
        telegram_url=f"https://t.me/user{user_id}",
        max_url=f"https://max.ru/user{user_id}",
        vk_url=f"https://vk.com/user{user_id}",
        role=role,
        password_hash="not-used",
        is_active=active,
    )


def _project(project_id: int, owner_id: int, *, status: str = "draft") -> ProjectORM:
    return ProjectORM(
        id=project_id,
        name=f"Project {project_id}",
        participants=12,
        days=5,
        status=status,
        owner_user_id=owner_id,
    )


def _act_as(actor: UserORM) -> None:
    app.dependency_overrides[require_preparation_access] = lambda: actor


def _actions(db_session) -> list[str]:
    db_session.expire_all()
    return list(
        db_session.scalars(
            select(AuditEventORM.action).order_by(AuditEventORM.id)
        ).all()
    )


def test_project_list_and_direct_reads_are_scoped_to_admin_owner_and_team(
    client,
    db_session,
):
    administrator = _user(10, "Администратор", "administrator")
    owner = _user(11, "Владелец")
    collaborator = _user(12, "Приглашённый", "verified_instructor")
    outsider = _user(13, "Посторонний")
    project = _project(101, owner.id)
    hidden = _project(102, outsider.id)
    db_session.add_all([administrator, owner, collaborator, outsider, project, hidden])
    db_session.flush()
    db_session.add(
        ProjectInstructorORM(
            project_id=project.id,
            user_id=collaborator.id,
            added_by_user_id=owner.id,
        )
    )
    db_session.commit()

    _act_as(owner)
    owner_list = client.get("/api/v1/projects")
    assert owner_list.status_code == 200
    assert [item["id"] for item in owner_list.json()["items"]] == [project.id]

    _act_as(collaborator)
    member_list = client.get("/api/v1/projects")
    assert member_list.status_code == 200
    assert [item["id"] for item in member_list.json()["items"]] == [project.id]
    project_response = client.get(f"/api/v1/projects/{project.id}")
    assert project_response.status_code == 200
    capabilities = project_response.json()["capabilities"]
    assert capabilities["can_view"] is True
    assert capabilities["can_edit_menu"] is False
    assert capabilities["can_manage_project"] is False
    assert capabilities["can_operate_shopping"] is True
    assert capabilities["can_operate_equipment"] is True
    assert capabilities["can_generate_documents"] is True

    _act_as(outsider)
    assert client.get(f"/api/v1/projects/{project.id}").status_code == 404
    assert client.get(f"/api/v1/projects/{project.id}/team").status_code == 404
    assert client.get(f"/api/v1/projects/{project.id}/preparation").status_code == 404
    assert client.get(f"/api/v1/meal-plans/project/{project.id}").status_code == 404

    _act_as(administrator)
    admin_list = client.get("/api/v1/projects")
    assert admin_list.status_code == 200
    assert {item["id"] for item in admin_list.json()["items"]} == {
        project.id,
        hidden.id,
    }


def test_owner_manages_multiple_instructors_and_removed_member_loses_access(
    client,
    db_session,
):
    owner = _user(21, "Владелец")
    collaborator = _user(22, "Инструктор")
    administrator = _user(23, "Администратор похода", "administrator")
    outsider = _user(24, "Посторонний")
    project = _project(201, owner.id)
    db_session.add_all([owner, collaborator, administrator, outsider, project])
    db_session.commit()

    _act_as(owner)
    response = client.put(
        f"/api/v1/projects/{project.id}/team",
        json={"instructor_user_ids": [collaborator.id, administrator.id]},
    )
    assert response.status_code == 200, response.text
    assert response.json()["owner"]["id"] == owner.id
    assert {item["id"] for item in response.json()["instructors"]} == {
        collaborator.id,
        administrator.id,
    }
    assert _actions(db_session) == [
        "project_instructor_added",
        "project_instructor_added",
    ]

    _act_as(collaborator)
    assert client.get(f"/api/v1/projects/{project.id}").status_code == 200
    assert client.get(f"/api/v1/projects/{project.id}/team").status_code == 200
    assert client.get(f"/api/v1/projects/{project.id}/team/candidates").status_code == 403
    assert (
        client.post(f"/api/v1/meal-plans/project/{project.id}/generate").status_code
        == 403
    )
    assert (
        client.patch(
            f"/api/v1/projects/{project.id}/participants",
            json={"participants": 15},
        ).status_code
        == 403
    )

    _act_as(owner)
    removed = client.put(
        f"/api/v1/projects/{project.id}/team",
        json={"instructor_user_ids": [administrator.id]},
    )
    assert removed.status_code == 200, removed.text
    assert _actions(db_session)[-1] == "project_instructor_removed"

    _act_as(collaborator)
    assert client.get(f"/api/v1/projects/{project.id}").status_code == 404

    _act_as(outsider)
    assert (
        client.get(
            f"/api/v1/projects/{project.id}/team/{administrator.id}/vcard"
        ).status_code
        == 404
    )

    _act_as(administrator)
    card = client.get(
        f"/api/v1/projects/{project.id}/team/{administrator.id}/vcard"
    )
    assert card.status_code == 200
    assert card.headers["content-type"].startswith("text/vcard")
    assert "BEGIN:VCARD" in card.text


def test_transfer_keeps_previous_owner_and_changes_management_rights(client, db_session):
    owner = _user(31, "Первый владелец")
    new_owner = _user(32, "Новый владелец", "verified_instructor")
    project = _project(301, owner.id)
    db_session.add_all([owner, new_owner, project])
    db_session.flush()
    db_session.add(
        ProjectInstructorORM(
            project_id=project.id,
            user_id=new_owner.id,
            added_by_user_id=owner.id,
        )
    )
    db_session.commit()

    _act_as(owner)
    response = client.post(
        f"/api/v1/projects/{project.id}/owner-transfer",
        json={"new_owner_user_id": new_owner.id},
    )
    assert response.status_code == 200, response.text
    assert response.json()["owner"]["id"] == new_owner.id
    assert [item["id"] for item in response.json()["instructors"]] == [owner.id]
    assert _actions(db_session) == ["project_owner_transferred"]

    _act_as(owner)
    old_owner_project = client.get(f"/api/v1/projects/{project.id}")
    assert old_owner_project.status_code == 200
    assert old_owner_project.json()["capabilities"]["can_manage_project"] is False
    assert (
        client.patch(
            f"/api/v1/projects/{project.id}/recipe-generation-mode",
            json={"recipe_generation_mode": "club_and_personal"},
        ).status_code
        == 403
    )

    _act_as(new_owner)
    assert (
        client.patch(
            f"/api/v1/projects/{project.id}/recipe-generation-mode",
            json={"recipe_generation_mode": "club_and_personal"},
        ).status_code
        == 200
    )


def test_completed_project_is_read_only_but_remains_visible_and_deletable(
    client,
    db_session,
):
    owner = _user(41, "Владелец")
    collaborator = _user(42, "Инструктор")
    project = _project(401, owner.id)
    db_session.add_all([owner, collaborator, project])
    db_session.flush()
    db_session.add(
        ProjectInstructorORM(
            project_id=project.id,
            user_id=collaborator.id,
            added_by_user_id=owner.id,
        )
    )
    db_session.commit()

    _act_as(collaborator)
    assert (
        client.patch(
            f"/api/v1/projects/{project.id}/status",
            json={"status": "completed"},
        ).status_code
        == 403
    )

    _act_as(owner)
    complete = client.patch(
        f"/api/v1/projects/{project.id}/status",
        json={"status": "completed"},
    )
    assert complete.status_code == 200, complete.text
    assert complete.json()["status"] == "completed"
    assert complete.json()["capabilities"]["can_manage_project"] is False
    assert complete.json()["capabilities"]["can_delete"] is True

    assert client.get(f"/api/v1/projects/{project.id}").status_code == 200
    assert (
        client.patch(
            f"/api/v1/projects/{project.id}/participants",
            json={"participants": 20},
        ).status_code
        == 409
    )
    assert (
        client.put(
            f"/api/v1/projects/{project.id}/team",
            json={"instructor_user_ids": []},
        ).status_code
        == 409
    )
    assert (
        client.post(f"/api/v1/meal-plans/project/{project.id}/generate").status_code
        == 409
    )
    assert (
        client.post(
            f"/api/v1/equipment-lists/project/{project.id}/items",
            json={"equipment_name": "Тент", "required_quantity": 1},
        ).status_code
        == 409
    )

    deleted = client.delete(f"/api/v1/projects/{project.id}")
    assert deleted.status_code == 204
    assert db_session.get(ProjectORM, project.id) is None
    assert _actions(db_session)[-2:] == ["project_status_updated", "project_deleted"]


def test_inactive_team_member_loses_and_regains_access(client, db_session):
    owner = _user(51, "Владелец")
    collaborator = _user(52, "Инструктор")
    project = _project(501, owner.id)
    db_session.add_all([owner, collaborator, project])
    db_session.flush()
    db_session.add(
        ProjectInstructorORM(
            project_id=project.id,
            user_id=collaborator.id,
            added_by_user_id=owner.id,
        )
    )
    db_session.commit()

    _act_as(collaborator)
    assert client.get(f"/api/v1/projects/{project.id}").status_code == 200

    collaborator.is_active = False
    db_session.commit()
    assert client.get(f"/api/v1/projects/{project.id}").status_code == 404

    collaborator.is_active = True
    db_session.commit()
    assert client.get(f"/api/v1/projects/{project.id}").status_code == 200


def test_team_update_rolls_back_membership_when_audit_fails(db_session, monkeypatch):
    owner = _user(61, "Владелец")
    collaborator = _user(62, "Инструктор")
    project = _project(601, owner.id)
    db_session.add_all([owner, collaborator, project])
    db_session.commit()

    def fail_record(*args, **kwargs):
        raise RuntimeError("audit failure")

    monkeypatch.setattr(AuditService, "record", fail_record)
    with pytest.raises(RuntimeError, match="audit failure"):
        ProjectTeamService(db_session, actor=owner).update_instructors(
            project.id,
            [collaborator.id],
        )

    db_session.expire_all()
    assert db_session.scalar(
        select(func.count()).select_from(ProjectInstructorORM).where(
            ProjectInstructorORM.project_id == project.id
        )
    ) == 0
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0
