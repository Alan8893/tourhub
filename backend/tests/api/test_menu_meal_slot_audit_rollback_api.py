import pytest
from sqlalchemy import func, select

from app.models.audit_event import AuditEventORM
from app.models.dish import DishORM
from app.models.dish_meal_role import DishMealRoleMealTypeORM, DishMealRoleORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.recipe import RecipeORM
from app.modules.projects.models.project import ProjectORM
from app.services.audit_service import AuditService


def _fail_audit(*args, **kwargs):
    raise RuntimeError("audit failure")


def test_menu_generation_rolls_back_when_audit_recording_fails(
    client,
    db_session,
    monkeypatch,
):
    project = ProjectORM(
        id=71,
        name="Generation rollback",
        participants=5,
        days=1,
        first_meal="breakfast",
        last_meal="breakfast",
        status="draft",
    )
    recipe = RecipeORM(id="rollback-breakfast-recipe", name="Rollback breakfast")
    dish = DishORM(id="rollback-breakfast-dish", name="Rollback porridge", recipe=recipe)
    role = DishMealRoleORM(dish=dish, role="main", is_repeatable=False)
    role.meal_types = [
        DishMealRoleMealTypeORM(
            dish_id=dish.id,
            role="main",
            meal_type="breakfast",
        )
    ]
    db_session.add_all([project, recipe, dish, role])
    db_session.commit()
    monkeypatch.setattr(AuditService, "record", _fail_audit)

    with pytest.raises(RuntimeError, match="audit failure"):
        client.post("/api/v1/meal-plans/project/71/generate")

    db_session.expire_all()
    assert db_session.scalar(select(func.count()).select_from(MealPlanORM)) == 0
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0


def test_meal_slot_replace_rolls_back_when_audit_recording_fails(
    client,
    db_session,
    monkeypatch,
):
    project = ProjectORM(
        id=72,
        name="Slot rollback",
        participants=4,
        days=1,
        status="draft",
    )
    first_recipe = RecipeORM(id="slot-first-recipe", name="First recipe")
    second_recipe = RecipeORM(id="slot-second-recipe", name="Second recipe")
    first_dish = DishORM(id="slot-first-dish", name="First dish", recipe=first_recipe)
    second_dish = DishORM(id="slot-second-dish", name="Second dish", recipe=second_recipe)
    plan = MealPlanORM(
        id="slot-rollback-plan",
        project=project,
        name=project.name,
        participants=project.participants,
        days_count=1,
    )
    day = MealPlanDayORM(id="slot-rollback-day", meal_plan=plan, day_number=1)
    slot = MealSlotORM(
        id="slot-rollback",
        day=day,
        meal_type="dinner",
        order=0,
    )
    item = MealSlotDishORM(
        id="slot-rollback-item",
        slot=slot,
        dish=first_dish,
        recipe=first_recipe,
        order=0,
    )
    db_session.add_all(
        [
            project,
            first_recipe,
            second_recipe,
            first_dish,
            second_dish,
            plan,
            day,
            slot,
            item,
        ]
    )
    db_session.commit()
    monkeypatch.setattr(AuditService, "record", _fail_audit)

    with pytest.raises(RuntimeError, match="audit failure"):
        client.put(
            "/api/v1/meal-slots/slot-rollback/dishes/"
            "slot-rollback-item/slot-second-dish"
        )

    db_session.expire_all()
    stored = db_session.get(MealSlotDishORM, "slot-rollback-item")
    assert stored.dish_id == "slot-first-dish"
    assert stored.recipe_id == "slot-first-recipe"
    assert db_session.scalar(select(func.count()).select_from(AuditEventORM)) == 0
