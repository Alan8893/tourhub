export type MealPlanViewState = "loading" | "error" | "empty" | "ready";

interface MealPlanViewStateInput {
  isLoading: boolean;
  isError: boolean;
  hasMealPlan: boolean;
}

interface MealSlotSummary {
  meal_type: string;
  dishes: readonly unknown[];
}

const mealTypeOrder: Record<string, number> = {
  breakfast: 0,
  snack: 1,
  lunch: 2,
  dinner: 3,
};

export function getMealPlanViewState({
  isLoading,
  isError,
  hasMealPlan,
}: MealPlanViewStateInput): MealPlanViewState {
  if (isLoading) return "loading";
  if (isError) return "error";
  if (!hasMealPlan) return "empty";
  return "ready";
}

export function sortMealSlots<T extends { meal_type: string }>(slots: readonly T[]): T[] {
  return [...slots].sort(
    (a, b) =>
      (mealTypeOrder[a.meal_type] ?? Number.MAX_SAFE_INTEGER) -
      (mealTypeOrder[b.meal_type] ?? Number.MAX_SAFE_INTEGER),
  );
}

export function countMealPlanDayDishes(slots: readonly MealSlotSummary[]): number {
  return slots.reduce((total, slot) => total + slot.dishes.length, 0);
}

export function isMealPlanDayExpandedByDefault(index: number): boolean {
  return index === 0;
}
