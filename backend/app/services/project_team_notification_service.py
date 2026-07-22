from typing import Protocol

from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM


class ProjectTeamNotificationService(Protocol):
    def instructor_added(self, project: ProjectORM, user: UserORM) -> None: ...

    def instructor_removed(self, project: ProjectORM, user: UserORM) -> None: ...

    def owner_transferred(
        self,
        project: ProjectORM,
        previous_owner: UserORM,
        new_owner: UserORM,
    ) -> None: ...


class NoOpProjectTeamNotificationService:
    """Extension point for future email, Telegram, and MAX notifications."""

    def instructor_added(self, project: ProjectORM, user: UserORM) -> None:
        return None

    def instructor_removed(self, project: ProjectORM, user: UserORM) -> None:
        return None

    def owner_transferred(
        self,
        project: ProjectORM,
        previous_owner: UserORM,
        new_owner: UserORM,
    ) -> None:
        return None
