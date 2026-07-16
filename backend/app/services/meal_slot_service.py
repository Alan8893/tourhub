from typing import cast
from uuid import uuid4

from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM


class MealSlotService:
    """
    Application service for editing meal compositions.

    Works only with MealSlot layer.
    Legacy MealPlanItem remains untouched.
    """

    def add_dish(self, slot: MealSlotORM, dish_id: str) -> MealSlotDishORM:
        dishes = cast(list[MealSlotDishORM], slot.dishes)
        item = MealSlotDishORM(
            id=str(uuid4()),
            slot=slot,
            dish_id=dish_id,
            order=len(dishes),
        )
        slot.is_manually_edited = True

        # SQLAlchemy relationship already attaches the item through slot=slot.
        # Do not append manually, otherwise the relationship collection receives
        # the same object twice.
        return item

    def remove_dish(self, slot: MealSlotORM, slot_dish_id: str) -> MealSlotORM:
        dishes = cast(list[MealSlotDishORM], slot.dishes)
        item = next(
            (dish for dish in dishes if dish.id == slot_dish_id),
            None,
        )
        if item is None:
            raise ValueError("Meal slot dish not found")

        dishes.remove(item)

        for index, dish in enumerate(dishes):
            dish.order = index

        slot.is_manually_edited = True
        return slot

    def replace_dish(
        self,
        slot: MealSlotORM,
        slot_dish_id: str,
        new_dish_id: str,
    ) -> MealSlotDishORM:
        dishes = cast(list[MealSlotDishORM], slot.dishes)
        for item in dishes:
            if item.id == slot_dish_id:
                item.dish_id = new_dish_id
                slot.is_manually_edited = True
                return item

        raise ValueError("Meal slot dish not found")
