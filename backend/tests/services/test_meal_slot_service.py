from types import SimpleNamespace

from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.services.meal_slot_service import MealSlotService



def make_slot():
    slot = MealSlotORM(
        id="slot-1",
        meal_type="breakfast",
    )
    slot.dishes = []
    return slot



def test_add_dish_to_slot():
    service = MealSlotService()
    slot = make_slot()

    item = service.add_dish(slot, "dish-1")

    assert item.dish_id == "dish-1"
    assert len(slot.dishes) == 1
    assert slot.dishes[0].order == 0



def test_replace_dish_in_slot():
    service = MealSlotService()
    slot = make_slot()

    item = MealSlotDishORM(
        id="slot-dish-1",
        dish_id="old-dish",
        order=0,
    )
    slot.dishes = [item]

    service.replace_dish(slot, "slot-dish-1", "new-dish")

    assert slot.dishes[0].dish_id == "new-dish"



def test_remove_dish_reorders_items():
    service = MealSlotService()
    slot = make_slot()

    slot.dishes = [
        MealSlotDishORM(id="1", dish_id="dish-1", order=0),
        MealSlotDishORM(id="2", dish_id="dish-2", order=1),
    ]

    service.remove_dish(slot, "1")

    assert len(slot.dishes) == 1
    assert slot.dishes[0].dish_id == "dish-2"
    assert slot.dishes[0].order == 0
