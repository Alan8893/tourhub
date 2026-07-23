from dataclasses import dataclass
from typing import cast
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.core.project_access import ProjectAccessPolicy
from app.engines.meal_schedule import MealScheduleEngine
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_plan_item import MealPlanItemORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe_generation_mode import RecipeGenerationMode
from app.models.user import UserORM
from app.modules.projects.models.project import ProjectORM
from app.modules.projects.repositories.project_repository import ProjectRepository
from app.repositories.meal_plan_repository import MealPlanRepository
from app.services.audit_service import AuditService
from app.services.dish_recipe_variant_service import DishRecipeVariantService

_MAX_WARNINGS = 20


@dataclass(frozen=True)
class ProjectCopyResult:
    project_id: int
    meal_plan_id: str
    copied_slot_count: int
    copied_assignment_count: int
    skipped_assignment_count: int
    warnings: list[str]


class ProjectCopyService:
    """Create a new draft Project from a completed Project menu template."""

    def __init__(
        self,
        session: Session,
        *,
        actor: UserORM,
        schedule_engine: MealScheduleEngine | None = None,
    ) -> None:
        self.session = session
        self.actor = actor
        self.schedule_engine = schedule_engine or MealScheduleEngine()

    def copy_project(
        self,
        source_project_id: int,
        *,
        name: str,
        participants: int,
        days: int,
        start_date: str | None,
        first_meal: str | None,
        last_meal: str | None,
        recipe_generation_mode: str,
    ) -> ProjectCopyResult:
        source = ProjectAccessPolicy.require_visible(
            self.session,
            source_project_id,
            self.actor,
        )
        if not (
            ProjectAccessPolicy.is_administrator(self.actor)
            or ProjectAccessPolicy.is_owner(source, self.actor)
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Копировать проект может только владелец или администратор.",
            )
        if source.status != "completed":
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Копировать можно только завершённый проект.",
            )

        normalized_name = name.strip()
        if not normalized_name:
            raise ValueError("Project name cannot be empty")
        if participants <= 0:
            raise ValueError("Participants must be greater than zero")
        if days <= 0:
            raise ValueError("Days must be greater than zero")
        if (first_meal is None) != (last_meal is None):
            raise ValueError("First and last meal must be provided together")
        RecipeGenerationMode(recipe_generation_mode)
        schedule = self.schedule_engine.build(
            days=days,
            start_meal=first_meal or "breakfast",
            end_meal=last_meal or "dinner",
        )

        source_plan = self._source_plan(source)
        source_slots = self._source_slots(source_plan)
        warnings: list[str] = []
        copied_slot_count = 0
        copied_assignment_count = 0
        skipped_assignment_count = 0

        try:
            destination = ProjectORM(
                name=normalized_name,
                participants=participants,
                days=days,
                start_date=start_date,
                first_meal=first_meal,
                last_meal=last_meal,
                recipe_generation_mode=recipe_generation_mode,
                status="draft",
                owner_user_id=self.actor.id,
            )
            self.session.add(destination)
            self.session.flush()

            meal_plan = MealPlanORM(
                id=str(uuid4()),
                project=destination,
                name=normalized_name,
                participants=participants,
                days_count=days,
                warnings=[],
            )
            self.session.add(meal_plan)

            if source_plan is None:
                self._warning(warnings, "Исходный проект не содержит плана питания.")

            for schedule_day in schedule:
                destination_day = MealPlanDayORM(
                    id=str(uuid4()),
                    meal_plan=meal_plan,
                    day_number=schedule_day.day_number,
                )
                self.session.add(destination_day)
                for slot_order, meal_type in enumerate(schedule_day.meals):
                    source_slot = source_slots.get((schedule_day.day_number, meal_type))
                    destination_slot = MealSlotORM(
                        id=str(uuid4()),
                        day=destination_day,
                        meal_type=meal_type,
                        name=source_slot.name if source_slot is not None else None,
                        order=slot_order,
                        is_manually_edited=source_slot is not None,
                    )
                    self.session.add(destination_slot)
                    copied_in_slot = 0
                    if source_slot is not None:
                        for source_assignment in cast(
                            list[MealSlotDishORM],
                            source_slot.dishes,
                        ):
                            if not self._assignment_is_usable(
                                source_assignment,
                                recipe_generation_mode,
                            ):
                                skipped_assignment_count += 1
                                self._warning(
                                    warnings,
                                    (
                                        f"День {schedule_day.day_number}, {meal_type}: "
                                        f"назначение «{source_assignment.dish.name}» пропущено."
                                    ),
                                )
                                continue
                            self.session.add(
                                MealSlotDishORM(
                                    id=str(uuid4()),
                                    slot=destination_slot,
                                    dish_id=source_assignment.dish_id,
                                    recipe_id=source_assignment.recipe_id,
                                    order=source_assignment.order,
                                )
                            )
                            self.session.add(
                                MealPlanItemORM(
                                    id=str(uuid4()),
                                    day=destination_day,
                                    dish_id=source_assignment.dish_id,
                                    recipe_id=source_assignment.recipe_id,
                                    meal_type=meal_type,
                                )
                            )
                            copied_in_slot += 1
                            copied_assignment_count += 1
                    if copied_in_slot:
                        copied_slot_count += 1

            meal_plan.warnings = list(warnings)
            AuditService(self.session).record(
                actor=self.actor,
                action="project_copied",
                entity_type="project",
                entity_id=destination.id,
                after={
                    "name": destination.name,
                    "participants": destination.participants,
                    "days": destination.days,
                    "start_date": destination.start_date,
                    "first_meal": destination.first_meal,
                    "last_meal": destination.last_meal,
                    "recipe_generation_mode": destination.recipe_generation_mode,
                    "status": destination.status,
                    "owner_user_id": destination.owner_user_id,
                },
                context={
                    "source_project_id": source.id,
                    "destination_project_id": destination.id,
                    "copied_slot_count": copied_slot_count,
                    "copied_assignment_count": copied_assignment_count,
                    "skipped_assignment_count": skipped_assignment_count,
                },
            )
            self.session.commit()
            return ProjectCopyResult(
                project_id=destination.id,
                meal_plan_id=meal_plan.id,
                copied_slot_count=copied_slot_count,
                copied_assignment_count=copied_assignment_count,
                skipped_assignment_count=skipped_assignment_count,
                warnings=list(warnings),
            )
        except Exception:
            self.session.rollback()
            raise

    def _source_plan(self, source: ProjectORM) -> MealPlanORM | None:
        current = MealPlanRepository(self.session).get_by_project_id(source.id)
        if current is None:
            return None
        return MealPlanRepository(self.session).get_with_details(current.id)

    @staticmethod
    def _source_slots(
        source_plan: MealPlanORM | None,
    ) -> dict[tuple[int, str], MealSlotORM]:
        if source_plan is None:
            return {}
        result: dict[tuple[int, str], MealSlotORM] = {}
        for day in cast(list[MealPlanDayORM], source_plan.days):
            for slot in cast(list[MealSlotORM], day.slots):
                result.setdefault((day.day_number, slot.meal_type), slot)
        return result

    def _assignment_is_usable(
        self,
        assignment: MealSlotDishORM,
        recipe_generation_mode: str,
    ) -> bool:
        dish = assignment.dish
        if dish.is_archived:
            return False
        eligible_recipe_ids = {
            recipe.id
            for recipe in DishRecipeVariantService.ordered_for_generation(
                dish,
                self.actor,
                recipe_generation_mode,
            )
        }
        return assignment.recipe_id in eligible_recipe_ids

    @staticmethod
    def _warning(warnings: list[str], message: str) -> None:
        if len(warnings) < _MAX_WARNINGS:
            warnings.append(message)
