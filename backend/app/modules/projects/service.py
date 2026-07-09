from dataclasses import dataclass

from app.modules.projects.models.project import ProjectORM
from app.modules.projects.repositories.project_repository import ProjectRepository


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    participants: int
    days: int
    start_date: str | None
    first_meal: str | None
    last_meal: str | None
    status: str


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def create_project(
        self,
        name: str,
        participants: int,
        days: int,
        start_date: str | None = None,
        first_meal: str | None = None,
        last_meal: str | None = None,
    ) -> Project:
        if participants <= 0:
            raise ValueError("Participants must be greater than zero")
        if days <= 0:
            raise ValueError("Days must be greater than zero")

        project = self.repository.create(ProjectORM(
            name=name,
            participants=participants,
            days=days,
            start_date=start_date,
            first_meal=first_meal,
            last_meal=last_meal,
            status="draft",
        ))

        return self._map(project)

    def get_project(self, project_id: int) -> Project:
        project = self.repository.get_by_id(project_id)
        if project is None:
            raise ValueError("Project not found")

        return self._map(project)

    @staticmethod
    def _map(project) -> Project:
        return Project(
            id=project.id,
            name=project.name,
            participants=project.participants,
            days=project.days,
            start_date=getattr(project, "start_date", None),
            first_meal=getattr(project, "first_meal", None),
            last_meal=getattr(project, "last_meal", None),
            status=project.status,
        )
