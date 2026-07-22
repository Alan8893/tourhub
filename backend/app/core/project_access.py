from dataclasses import dataclass

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.repositories.project_repository import ProjectRepository


@dataclass(frozen=True)
class ProjectCapabilities:
    can_view: bool
    can_manage_project: bool
    can_manage_team: bool
    can_transfer_ownership: bool
    can_edit_menu: bool
    can_operate_shopping: bool
    can_operate_equipment: bool
    can_generate_documents: bool
    can_delete: bool


class ProjectAccessPolicy:
    @staticmethod
    def is_administrator(actor: UserORM) -> bool:
        return actor.role == "administrator"

    @classmethod
    def is_owner(cls, project: ProjectORM, actor: UserORM) -> bool:
        return project.owner_user_id == actor.id

    @classmethod
    def is_additional_instructor(cls, project: ProjectORM, actor: UserORM) -> bool:
        return any(link.user_id == actor.id for link in project.instructor_links)

    @classmethod
    def can_view(cls, project: ProjectORM, actor: UserORM) -> bool:
        return (
            actor.is_active
            and (
                cls.is_administrator(actor)
                or cls.is_owner(project, actor)
                or cls.is_additional_instructor(project, actor)
            )
        )

    @classmethod
    def capabilities(
        cls,
        project: ProjectORM,
        actor: UserORM,
    ) -> ProjectCapabilities:
        visible = cls.can_view(project, actor)
        owner_or_admin = visible and (
            cls.is_administrator(actor) or cls.is_owner(project, actor)
        )
        writable = project.status != "completed"
        manager_write = owner_or_admin and writable
        collaborator_write = visible and writable
        return ProjectCapabilities(
            can_view=visible,
            can_manage_project=manager_write,
            can_manage_team=manager_write,
            can_transfer_ownership=manager_write,
            can_edit_menu=manager_write,
            can_operate_shopping=collaborator_write,
            can_operate_equipment=collaborator_write,
            can_generate_documents=visible,
            can_delete=owner_or_admin,
        )

    @classmethod
    def require_visible(
        cls,
        session: Session,
        project_id: int,
        actor: UserORM,
    ) -> ProjectORM:
        project = ProjectRepository(session).get_by_id(project_id)
        if project is None or not cls.can_view(project, actor):
            # Hide both existence and membership from unrelated users.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
        return project

    @classmethod
    def require_manager_write(
        cls,
        session: Session,
        project_id: int,
        actor: UserORM,
    ) -> ProjectORM:
        project = cls.require_visible(session, project_id, actor)
        if project.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Завершённый проект доступен только для чтения.",
            )
        if not (cls.is_administrator(actor) or cls.is_owner(project, actor)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Изменять проект может только владелец или администратор.",
            )
        return project

    @classmethod
    def require_menu_write(
        cls,
        session: Session,
        project_id: int,
        actor: UserORM,
    ) -> ProjectORM:
        project = cls.require_manager_write(session, project_id, actor)
        return project

    @classmethod
    def require_operational_write(
        cls,
        session: Session,
        project_id: int,
        actor: UserORM,
    ) -> ProjectORM:
        project = cls.require_visible(session, project_id, actor)
        if project.status == "completed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Завершённый проект доступен только для чтения.",
            )
        return project

    @classmethod
    def require_delete(
        cls,
        session: Session,
        project_id: int,
        actor: UserORM,
    ) -> ProjectORM:
        project = cls.require_visible(session, project_id, actor)
        if not (cls.is_administrator(actor) or cls.is_owner(project, actor)):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Удалить проект может только владелец или администратор.",
            )
        return project
