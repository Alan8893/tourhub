from __future__ import annotations

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.models.project_instructor import ProjectInstructorORM


class ProjectRepository:
    def __init__(self, session: Session):
        self.session = session

    @staticmethod
    def _options():
        return (
            selectinload(ProjectORM.owner),
            selectinload(ProjectORM.instructor_links).selectinload(
                ProjectInstructorORM.user
            ),
            selectinload(ProjectORM.meal_plans),
            selectinload(ProjectORM.purchase_lists),
            selectinload(ProjectORM.purchase_checklists),
        )

    def get_by_id(self, project_id: int) -> ProjectORM | None:
        return self.session.scalar(
            select(ProjectORM)
            .options(*self._options())
            .where(ProjectORM.id == project_id)
        )

    def list(self) -> list[ProjectORM]:
        return list(
            self.session.scalars(
                select(ProjectORM)
                .options(*self._options())
                .order_by(ProjectORM.id.desc())
            ).all()
        )

    def list_visible_to(self, actor: UserORM) -> list[ProjectORM]:
        statement = select(ProjectORM).options(*self._options())
        if actor.role != "administrator":
            statement = statement.where(
                or_(
                    ProjectORM.owner_user_id == actor.id,
                    ProjectORM.instructor_links.any(
                        ProjectInstructorORM.user_id == actor.id
                    ),
                )
            )
        return list(
            self.session.scalars(statement.order_by(ProjectORM.id.desc())).all()
        )

    def create(self, project: ProjectORM) -> ProjectORM:
        self.session.add(project)
        self.session.flush()
        self.session.refresh(project)
        return project

    def delete(self, project: ProjectORM) -> None:
        self.session.delete(project)
        self.session.flush()
