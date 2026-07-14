from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.modules.projects.models.project import ProjectORM


class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    def get_by_id(self, project_id: int) -> ProjectORM | None:
        return self.session.scalar(
            select(ProjectORM)
            .options(
                selectinload(ProjectORM.meal_plans),
                selectinload(ProjectORM.purchase_lists),
                selectinload(ProjectORM.purchase_checklists),
            )
            .where(ProjectORM.id == project_id)
        )

    def list(self) -> list[ProjectORM]:
        return list(
            self.session.scalars(
                select(ProjectORM).order_by(ProjectORM.id.desc())
            ).all()
        )

    def create(self, project: ProjectORM) -> ProjectORM:
        self.session.add(project)
        self.session.commit()
        self.session.refresh(project)
        return project
