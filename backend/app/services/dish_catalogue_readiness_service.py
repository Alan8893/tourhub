from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.modules.domain.meal_role import MealRole
from app.modules.domain.meal_type import MealType
from app.services.dish_service import DishService


@dataclass(frozen=True)
class DishCatalogueCoverage:
    meal_type: MealType
    role: MealRole
    required: bool
    candidate_count: int
    minimum_required: int

    @property
    def ready(self) -> bool:
        return self.candidate_count >= self.minimum_required


@dataclass(frozen=True)
class DishCatalogueReadiness:
    ready: bool
    active_dish_count: int
    classified_dish_count: int
    unclassified_dish_count: int
    coverage: tuple[DishCatalogueCoverage, ...]


_COVERAGE_POLICY = (
    (MealType.BREAKFAST, MealRole.MAIN, True),
    (MealType.BREAKFAST, MealRole.ADDITION, False),
    (MealType.BREAKFAST, MealRole.DRINK, False),
    (MealType.SNACK, MealRole.SNACK, True),
    (MealType.LUNCH, MealRole.MAIN, True),
    (MealType.LUNCH, MealRole.ADDITION, False),
    (MealType.LUNCH, MealRole.DRINK, False),
    (MealType.DINNER, MealRole.MAIN, True),
    (MealType.DINNER, MealRole.ADDITION, False),
    (MealType.DINNER, MealRole.DRINK, False),
)


class DishCatalogueReadinessService:
    def __init__(self, session: Session):
        self.session = session

    def evaluate(self) -> DishCatalogueReadiness:
        active_dishes = [
            dish
            for dish in DishService(self.session).list_dishes()
            if not dish.recipe.is_archived
        ]
        candidate_counts = {
            (meal_type, role): 0
            for meal_type, role, _required in _COVERAGE_POLICY
        }

        for dish in active_dishes:
            for assignment in dish.meal_roles:
                role = MealRole(assignment.role)
                for meal_type_assignment in assignment.meal_types:
                    key = (MealType(meal_type_assignment.meal_type), role)
                    if key in candidate_counts:
                        candidate_counts[key] += 1

        coverage = tuple(
            DishCatalogueCoverage(
                meal_type=meal_type,
                role=role,
                required=required,
                candidate_count=candidate_counts[(meal_type, role)],
                minimum_required=1,
            )
            for meal_type, role, required in _COVERAGE_POLICY
        )
        classified_dish_count = sum(bool(dish.meal_roles) for dish in active_dishes)

        return DishCatalogueReadiness(
            ready=all(item.ready for item in coverage if item.required),
            active_dish_count=len(active_dishes),
            classified_dish_count=classified_dish_count,
            unclassified_dish_count=len(active_dishes) - classified_dish_count,
            coverage=coverage,
        )
