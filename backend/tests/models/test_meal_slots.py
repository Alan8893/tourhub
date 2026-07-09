from uuid import uuid4

from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM



def test_meal_slot_can_contain_multiple_dishes():
    slot = MealSlotORM(
        id=str(uuid4()),
        meal_plan_day_id=str(uuid4()),
        meal_type="breakfast",
        name="Mountain breakfast",
        order=1,
    )

    first = MealSlotDishORM(
        id=str(uuid4()),
        dish_id=str(uuid4()),
        order=1,
    )

    second = MealSlotDishORM(
        id=str(uuid4()),
        dish_id=str(uuid4()),
        order=2,
    )

    slot.dishes.append(first)
    slot.dishes.append(second)

    assert len(slot.dishes) == 2
    assert slot.dishes[0].order == 1
    assert slot.dishes[1].order == 2



def test_meal_slot_defaults_are_defined():
    slot = MealSlotORM(
        id=str(uuid4()),
        meal_plan_day_id=str(uuid4()),
        meal_type="dinner",
    )

    assert slot.meal_type == "dinner"
    assert slot.order is None
