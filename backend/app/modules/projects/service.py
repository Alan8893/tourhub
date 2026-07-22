from dataclasses import dataclass

from app.engines.meal_schedule import MealScheduleEngine
from app.models.recipe_generation_mode import RecipeGenerationMode
from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.services.audit_service import AuditService


@dataclass(frozen=True)
class Project:
    id: int
    name: str
    participants: int
    days: int
    start_date: str | None
    first_meal: str | None
    last_meal: str | None
    recipe_generation_mode: str
    status: str
    owner_user_id: int | None


class ProjectService:
    def __init__(
        self,
        repository: ProjectRepository,
        schedule_engine: MealScheduleEngine | None = None,
        actor: UserORM | None = None,
    ) -> None:
        self.repository = repository
        self.schedule_engine = schedule_engine or MealScheduleEngine()
        self.actor = actor

    def create_project(
        self,
        name: str,
        participants: int,
        days: int,
        start_date: str | None = None,
        first_meal: str | None = None,
        last_meal: str | None = None,
        recipe_generation_mode: str = RecipeGenerationMode.CLUB_ONLY.value,
    ) -> Project:
        if participants <= 0:
            raise ValueError("Participants must be greater than zero")
        if days <= 0:
            raise ValueError("Days must be greater than zero")
        self._validate_meal_boundaries(days, first_meal, last_meal)
        self._validate_generation_mode(recipe_generation_mode)

        session = self.repository.session
        try:
            project = self.repository.create(
                ProjectORM(
                    name=name,
                    participants=participants,
                    days=days,
                    start_date=start_date,
                    first_meal=first_meal,
                    last_meal=last_meal,
                    recipe_generation_mode=recipe_generation_mode,
                    status="draft",
                    owner_user_id=self.actor.id if self.actor is not None else None,
                )
            )
            if self.actor is not None:
                AuditService(session).record(
                    actor=self.actor,
                    action="project_created",
                    entity_type="project",
                    entity_id=project.id,
                    after=self._snapshot(project),
                    context={"project_name": project.name},
                )
            session.commit()
        except Exception:
            session.rollback()
            raise

        session.refresh(project)
        return self._map(project)

    def get_project(self, project_id: int) -> Project:
        project = self.repository.get_by_id(project_id)
        if project is None:
            raise ValueError("Project not found")
        return self._map(project)

    def update_recipe_generation_mode(
        self,
        project_id: int,
        recipe_generation_mode: str,
    ) -> Project:
        self._validate_generation_mode(recipe_generation_mode)
        project = self.repository.get_by_id(project_id)
        if project is None:
            raise ValueError("Project not found")
        if project.recipe_generation_mode == recipe_generation_mode:
            return self._map(project)

        session = self.repository.session
        before = self._snapshot(project)
        try:
            project.recipe_generation_mode = recipe_generation_mode
            if self.actor is not None:
                AuditService(session).record(
                    actor=self.actor,
                    action="project_generation_mode_updated",
                    entity_type="project",
                    entity_id=project.id,
                    before=before,
                    after=self._snapshot(project),
                    context={"changed_fields": ["recipe_generation_mode"]},
                )
            session.commit()
        except Exception:
            session.rollback()
            raise

        session.refresh(project)
        return self._map(project)

    def complete_project(self, project_id: int) -> Project:
        project = self.repository.get_by_id(project_id)
        if project is None:
            raise ValueError("Project not found")
        if project.status == "completed":
            return self._map(project)

        session = self.repository.session
        before = self._snapshot(project)
        try:
            project.status = "completed"
            if self.actor is not None:
                AuditService(session).record(
                    actor=self.actor,
                    action="project_status_updated",
                    entity_type="project",
                    entity_id=project.id,
                    before=before,
                    after=self._snapshot(project),
                    context={"changed_fields": ["status"]},
                )
            session.commit()
        except Exception:
            session.rollback()
            raise
        session.refresh(project)
        return self._map(project)

    def delete_project(self, project_id: int) -> None:
        project = self.repository.get_by_id(project_id)
        if project is None:
            raise ValueError("Project not found")
        session = self.repository.session
        snapshot = self._snapshot(project)
        try:
            self.repository.delete(project)
            if self.actor is not None:
                AuditService(session).record(
                    actor=self.actor,
                    action="project_deleted",
                    entity_type="project",
                    entity_id=project.id,
                    before=snapshot,
                    after=None,
                    context={"project_name": project.name},
                )
            session.commit()
        except Exception:
            session.rollback()
            raise

    def _validate_meal_boundaries(
        self,
        days: int,
        first_meal: str | None,
        last_meal: str | None,
    ) -> None:
        if first_meal is None and last_meal is None:
            return
        if first_meal is None or last_meal is None:
            raise ValueError("First and last meal must be provided together")
        self.schedule_engine.build(
            days=days,
            start_meal=first_meal,
            end_meal=last_meal,
        )

    @staticmethod
    def _validate_generation_mode(value: str) -> None:
        try:
            RecipeGenerationMode(value)
        except ValueError as exc:
            raise ValueError("Unsupported recipe generation mode") from exc

    @staticmethod
    def _snapshot(project: ProjectORM) -> dict[str, object]:
        return {
            "name": project.name,
            "participants": project.participants,
            "days": project.days,
            "start_date": project.start_date,
            "first_meal": project.first_meal,
            "last_meal": project.last_meal,
            "recipe_generation_mode": project.recipe_generation_mode,
            "status": project.status,
            "owner_user_id": project.owner_user_id,
        }

    @staticmethod
    def _map(project: ProjectORM) -> Project:
        return Project(
            id=project.id,
            name=project.name,
            participants=project.participants,
            days=project.days,
            start_date=getattr(project, "start_date", None),
            first_meal=getattr(project, "first_meal", None),
            last_meal=getattr(project, "last_meal", None),
            recipe_generation_mode=getattr(
                project,
                "recipe_generation_mode",
                RecipeGenerationMode.CLUB_ONLY.value,
            ),
            status=project.status,
            owner_user_id=getattr(project, "owner_user_id", None),
        )
