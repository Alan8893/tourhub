from uuid import uuid4

from app.models.meal_slot_dish import MealSlotDishORM


class MealSlotService:
    """
    Application service for editing meal compositions.

    Works only with MealSlot layer.
    Legacy MealPlanItem remains untouched.
    """

    def add_dish(self, slot, dish_id: str):
        item = MealSlotDishORM(
            id=str(uuid4()),
            slot=slot,
            dish_id=dish_id,
            order=len(slot.dishes),
        )
        slot.dishes.append(item)
        return item

    def remove_dish(self, slot, slot_dish_id: str):
        slot.dishes = [
            item
            for item in slot.dishes
            if item.id != slot_dish_id
        ]

        for index, item in enumerate(slot.dishes):
            item.order = index

        return slot

    def replace_dish(self, slot, slot_dish_id: str, new_dish_id: str):
        for item in slot.dishes:
            if item.id == slot_dish_id:
                item.dish_id = new_dish_id
                return item

        raise ValueError("Meal slot dish not found")
