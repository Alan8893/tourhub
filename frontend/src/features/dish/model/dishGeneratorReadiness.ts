import type { Dish, DishMealRole } from "../api/dishApi";

export type DishGeneratorState = "ready" | "not_configured";

export function getDishGeneratorState(
  dish: Pick<Dish, "meal_roles"> | { meal_roles: DishMealRole[] },
): DishGeneratorState {
  return dish.meal_roles.length > 0 ? "ready" : "not_configured";
}

export function formatDishGeneratorState(state: DishGeneratorState): string {
  return state === "ready" ? "Готово для генератора" : "Не настроено для генератора";
}
