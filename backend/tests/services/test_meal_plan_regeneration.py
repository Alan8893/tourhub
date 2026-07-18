from types import SimpleNamespace

from app.models.dish import DishORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.services.meal_plan_service import MealPlanService


def _assignment(role: str, *meal_types: str):
    return SimpleNamespace(
        role=role,
        is_repeatable=False,
        meal_types=[SimpleNamespace(meal_type=meal_type) for meal_type in meal_types],
    )


def _automatic_dish(dish_id: str, name: str, role: str, meal_type: str):
    recipe_id = f"recipe-{dish_id}"
    return SimpleNamespace(
        id=dish_id,
        name=name,
        recipe_id=recipe_id,
        recipe=SimpleNamespace(
            id=recipe_id,
            name=f"{name} recipe",
            is_archived=False,
        ),
        recipe_variants=[],
        meal_roles=[_assignment(role, meal_type)],
    )


class FakeDishRepository:
    def list(self):
        return [_automatic_dish("auto-lunch", "Automatic lunch", "main", "lunch")]


class FakeMealPlanRepository:
    def __init__(self, meal_plan: MealPlanORM):
        self.meal_plan = meal_plan
        self.added_plans = []
        self.days = []
        self.items = []
        self.slots = []
        self.slot_dishes = []
        self.committed = False

    def get_by_project_id(self, project_id: int):
        if self.meal_plan.project_id == project_id:
            return self.meal_plan
        return None

    def get_with_details(self, meal_plan_id: str):
        if self.meal_plan.id == meal_plan_id:
            return self.meal_plan
        return None

    def add(self, meal_plan):
        self.added_plans.append(meal_plan)
        self.meal_plan = meal_plan

    def add_day(self, day):
        self.days.append(day)

    def add_item(self, item):
        self.items.append(item)

    def add_slot(self, slot):
        self.slots.append(slot)

    def add_slot_dish(self, slot_dish):
        self.slot_dishes.append(slot_dish)

    def commit(self):
        self.committed = True


def _existing_plan_with_manual_breakfast() -> MealPlanORM:
    manual_recipe = RecipeORM(id="manual-recipe", name="Manual recipe")
    manual_dish = DishORM(id="manual-dish", name="Manual dish", recipe=manual_recipe)
    meal_plan = MealPlanORM(
        id="existing-plan",
        project_id=7,
        name="Old plan",
        participants=2,
        days_count=1,
    )
    day = MealPlanDayORM(id="old-day", day_number=1, meal_plan=meal_plan)
    slot = MealSlotORM(
        id="old-slot",
        day=day,
        meal_type="breakfast",
        order=0,
        is_manually_edited=True,
    )
    MealSlotDishORM(
        id="old-slot-dish",
        slot=slot,
        dish=manual_dish,
        dish_id=manual_dish.id,
        recipe=manual_recipe,
        recipe_id=manual_recipe.id,
        order=0,
    )
    return meal_plan


def test_regeneration_reuses_plan_and_preserves_manual_slot():
    repository = FakeMealPlanRepository(_existing_plan_with_manual_breakfast())
    service = MealPlanService(
        dish_repository=FakeDishRepository(),
        meal_plan_repository=repository,
    )

    saved = service.generate_and_save_result(
        name="Updated plan",
        participants=5,
        days=1,
        meals_per_day=["breakfast", "lunch"],
        project_id=7,
    )

    assert saved.meal_plan.id == "existing-plan"
    assert saved.meal_plan.name == "Updated plan"
    assert saved.meal_plan.participants == 5
    assert repository.added_plans == []
    assert repository.committed is True
    assert saved.warnings == []
    assert [slot.meal_type for slot in repository.slots] == ["breakfast", "lunch"]
    assert [slot.is_manually_edited for slot in repository.slots] == [True, False]
    assert [dish.dish_id for dish in repository.slot_dishes] == [
        "manual-dish",
        "auto-lunch",
    ]
    assert [dish.recipe_id for dish in repository.slot_dishes] == [
        "manual-recipe",
        "recipe-auto-lunch",
    ]


def test_regeneration_preserves_manually_emptied_slot():
    meal_plan = _existing_plan_with_manual_breakfast()
    meal_plan.days[0].slots[0].dishes.clear()
    repository = FakeMealPlanRepository(meal_plan)
    service = MealPlanService(
        dish_repository=FakeDishRepository(),
        meal_plan_repository=repository,
    )

    saved = service.generate_and_save_result(
        name="Updated plan",
        participants=5,
        days=1,
        meals_per_day=["breakfast", "lunch"],
        project_id=7,
    )

    breakfast = next(slot for slot in repository.slots if slot.meal_type == "breakfast")
    assert breakfast.is_manually_edited is True
    assert breakfast.dishes == []
    assert saved.warnings == []
