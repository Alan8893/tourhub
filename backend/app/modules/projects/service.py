from dataclasses import dataclass

from app.modules.projects.repositories.project_repository import ProjectRepository


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    participants: int
    days: int
    status: str


class ProjectService:
    def __init__(self, repository: ProjectRepository):
        self.repository = repository

    def get_project(self, project_id: int) -> Project:
        project = self.repository.get_by_id(project_id)

        if project is None:
            raise ValueError("Project not found")

        return Project(
            id=project.id,
            name=project.name,
            participants=project.participants,
            days=project.days,
            status=project.status,
        )
