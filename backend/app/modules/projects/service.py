from dataclasses import dataclass


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    participants: int
    days: int
    status: str


class ProjectService:
    def get_project(self, project_id: int) -> Project:
        return Project(
            id=project_id,
            name="Altai Trip 2026",
            participants=10,
            days=7,
            status="draft",
        )
