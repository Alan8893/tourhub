from uuid import uuid4

from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM


def test_meal_slot_structure_supports_multiple_dishes():
    slot = MealSlotORM(
        id=str(uuid4()),
        meal_plan_day_id=str(uuid4()),
        meal_type="breakfast",
    )

    slot.dishes = [
        MealSlotDishORM(
            id=str(uuid4()),
            dish_id="dish-1",
            order=0,
        ),
        MealSlotDishORM(
            id=str(uuid4()),
            dish_id="dish-2",
            order=1,
        ),
    ]

    assert len(slot.dishes) == 2
    assert slot.dishes[0].dish_id == "dish-1"
    assert slot.dishes[1].dish_id == "dish-2"


def test_legacy_and_new_meal_structures_can_coexist():
    slot = MealSlotORM(
        id=str(uuid4()),
        meal_plan_day_id=str(uuid4()),
        meal_type="dinner",
    )

    assert slot.meal_type == "dinner"
    assert hasattr(slot, "dishes")
