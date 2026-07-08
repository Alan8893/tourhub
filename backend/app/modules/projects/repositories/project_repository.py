from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.projects.models.project import ProjectORM


class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, project_id: int) -> ProjectORM | None:
        return self.session.scalar(
            select(ProjectORM).where(ProjectORM.id == project_id)
        )
