from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.models.project_instructor import ProjectInstructorORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.services.audit_service import AuditService
from app.services.project_team_notification_service import (
    NoOpProjectTeamNotificationService,
    ProjectTeamNotificationService,
)

_SUPPORTED_ROLES = {"administrator", "instructor", "verified_instructor"}


class ProjectTeamService:
    def __init__(
        self,
        session: Session,
        *,
        actor: UserORM,
        notifications: ProjectTeamNotificationService | None = None,
    ) -> None:
        self.session = session
        self.actor = actor
        self.notifications = notifications or NoOpProjectTeamNotificationService()

    def get_team(self, project_id: int) -> ProjectORM:
        project = ProjectRepository(self.session).get_by_id(project_id)
        if project is None or project.owner is None:
            raise LookupError("Project team not found")
        return project

    def list_candidates(self, project_id: int) -> list[UserORM]:
        project = self.get_team(project_id)
        return list(
            self.session.scalars(
                select(UserORM)
                .where(
                    UserORM.is_active.is_(True),
                    UserORM.role.in_(_SUPPORTED_ROLES),
                    UserORM.id != project.owner_user_id,
                )
                .order_by(UserORM.role, UserORM.display_name, UserORM.email, UserORM.id)
            ).all()
        )

    def update_instructors(
        self,
        project_id: int,
        instructor_user_ids: list[int],
    ) -> ProjectORM:
        added_users: list[UserORM] = []
        removed_users: list[UserORM] = []
        try:
            project = self._locked_project(project_id)
            requested_ids = set(instructor_user_ids)
            if project.owner_user_id in requested_ids:
                raise ValueError("Владелец уже входит в команду проекта.")

            users = list(
                self.session.scalars(
                    select(UserORM)
                    .where(UserORM.id.in_(requested_ids))
                    .with_for_update()
                ).all()
            ) if requested_ids else []
            users_by_id = {user.id: user for user in users}
            if set(users_by_id) != requested_ids:
                raise ValueError("Один или несколько пользователей не найдены.")
            invalid = [
                user
                for user in users
                if not user.is_active or user.role not in _SUPPORTED_ROLES
            ]
            if invalid:
                raise ValueError("В команду можно добавить только активного инструктора.")

            current_links = list(
                self.session.scalars(
                    select(ProjectInstructorORM)
                    .where(ProjectInstructorORM.project_id == project.id)
                    .with_for_update()
                ).all()
            )
            current_ids = {link.user_id for link in current_links}
            added_ids = requested_ids - current_ids
            removed_ids = current_ids - requested_ids

            if not added_ids and not removed_ids:
                return ProjectRepository(self.session).get_by_id(project.id) or project

            removed_users_by_id = {
                user.id: user
                for user in self.session.scalars(
                    select(UserORM).where(UserORM.id.in_(removed_ids))
                ).all()
            } if removed_ids else {}

            for link in current_links:
                if link.user_id not in removed_ids:
                    continue
                removed_user = removed_users_by_id.get(link.user_id)
                self.session.delete(link)
                if removed_user is not None:
                    removed_users.append(removed_user)
                    AuditService(self.session).record(
                        actor=self.actor,
                        action="project_instructor_removed",
                        entity_type="project",
                        entity_id=project.id,
                        before={"instructor": self._user_snapshot(removed_user)},
                        after=None,
                        context={"project_name": project.name},
                    )

            for user_id in sorted(added_ids):
                user = users_by_id[user_id]
                self.session.add(
                    ProjectInstructorORM(
                        project_id=project.id,
                        user_id=user.id,
                        added_by_user_id=self.actor.id,
                    )
                )
                added_users.append(user)
                AuditService(self.session).record(
                    actor=self.actor,
                    action="project_instructor_added",
                    entity_type="project",
                    entity_id=project.id,
                    before=None,
                    after={"instructor": self._user_snapshot(user)},
                    context={"project_name": project.name},
                )

            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        updated = ProjectRepository(self.session).get_by_id(project_id)
        if updated is None:
            raise LookupError("Project not found")
        for user in added_users:
            self.notifications.instructor_added(updated, user)
        for user in removed_users:
            self.notifications.instructor_removed(updated, user)
        return updated

    def transfer_ownership(self, project_id: int, new_owner_user_id: int) -> ProjectORM:
        try:
            project = self._locked_project(project_id)
            if project.owner_user_id == new_owner_user_id:
                return ProjectRepository(self.session).get_by_id(project.id) or project

            previous_owner = self.session.scalar(
                select(UserORM)
                .where(UserORM.id == project.owner_user_id)
                .with_for_update()
            )
            new_owner = self.session.scalar(
                select(UserORM)
                .where(UserORM.id == new_owner_user_id)
                .with_for_update()
            )
            if previous_owner is None:
                raise ValueError("Текущий владелец проекта не найден.")
            if (
                new_owner is None
                or not new_owner.is_active
                or new_owner.role not in _SUPPORTED_ROLES
            ):
                raise ValueError("Новым владельцем может быть только активный пользователь.")

            new_owner_link = self.session.scalar(
                select(ProjectInstructorORM).where(
                    ProjectInstructorORM.project_id == project.id,
                    ProjectInstructorORM.user_id == new_owner.id,
                )
            )
            if new_owner_link is not None:
                self.session.delete(new_owner_link)

            previous_owner_link = self.session.scalar(
                select(ProjectInstructorORM).where(
                    ProjectInstructorORM.project_id == project.id,
                    ProjectInstructorORM.user_id == previous_owner.id,
                )
            )
            if previous_owner_link is None:
                self.session.add(
                    ProjectInstructorORM(
                        project_id=project.id,
                        user_id=previous_owner.id,
                        added_by_user_id=self.actor.id,
                    )
                )

            before = self._user_snapshot(previous_owner)
            after = self._user_snapshot(new_owner)
            project.owner_user_id = new_owner.id
            AuditService(self.session).record(
                actor=self.actor,
                action="project_owner_transferred",
                entity_type="project",
                entity_id=project.id,
                before={"owner": before},
                after={"owner": after},
                context={
                    "project_name": project.name,
                    "previous_owner_kept_as_instructor": True,
                },
            )
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise

        updated = ProjectRepository(self.session).get_by_id(project_id)
        if updated is None:
            raise LookupError("Project not found")
        self.notifications.owner_transferred(updated, previous_owner, new_owner)
        return updated

    def get_team_member(self, project_id: int, user_id: int) -> UserORM:
        project = self.get_team(project_id)
        allowed_ids = {project.owner_user_id}
        allowed_ids.update(link.user_id for link in project.instructor_links)
        if user_id not in allowed_ids:
            raise LookupError("Контакт команды проекта не найден.")
        user = self.session.get(UserORM, user_id)
        if user is None:
            raise LookupError("Контакт команды проекта не найден.")
        return user

    def _locked_project(self, project_id: int) -> ProjectORM:
        project = self.session.scalar(
            select(ProjectORM).where(ProjectORM.id == project_id).with_for_update()
        )
        if project is None:
            raise LookupError("Project not found")
        return project

    @staticmethod
    def _user_snapshot(user: UserORM) -> dict[str, object]:
        return {
            "user_id": user.id,
            "display_name": user.display_name,
            "role": user.role,
        }
