export interface MealSlotMutationState {
  addPending: boolean;
  replacePending: boolean;
  removePending: boolean;
  addError: boolean;
  replaceError: boolean;
  removeError: boolean;
}

export type MealSlotMutationKind = "add" | "replace" | "remove";

export interface AddMealSlotDishCommand {
  slotId: string;
  dishId: string;
}

export interface ReplaceMealSlotDishCommand extends AddMealSlotDishCommand {
  slotDishId: string;
}

export interface RemoveMealSlotDishCommand {
  slotId: string;
  slotDishId: string;
}

export const mealSlotResponsiveDirection = {
  xs: "column",
  sm: "row",
} as const;

export function isMealSlotMutationBusy(state: MealSlotMutationState): boolean {
  return state.addPending || state.replacePending || state.removePending;
}

export function hasMealSlotMutationError(state: MealSlotMutationState): boolean {
  return state.addError || state.replaceError || state.removeError;
}

export function canSubmitDishSelection(value: string, busy: boolean): boolean {
  return !busy && value.trim().length > 0;
}

export function getMealSlotSuccessMessage(kind: MealSlotMutationKind): string {
  const messages: Record<MealSlotMutationKind, string> = {
    add: "Блюдо добавлено.",
    replace: "Блюдо заменено.",
    remove: "Блюдо удалено.",
  };

  return messages[kind];
}

export function formatDishCount(count: number): string {
  const normalized = Math.max(0, Math.trunc(count));
  const lastTwoDigits = normalized % 100;
  const lastDigit = normalized % 10;

  if (lastTwoDigits >= 11 && lastTwoDigits <= 14) {
    return `${normalized} блюд`;
  }
  if (lastDigit === 1) {
    return `${normalized} блюдо`;
  }
  if (lastDigit >= 2 && lastDigit <= 4) {
    return `${normalized} блюда`;
  }

  return `${normalized} блюд`;
}

export function createAddMealSlotDishCommand(
  slotId: string,
  dishId: string,
): AddMealSlotDishCommand {
  return { slotId, dishId: dishId.trim() };
}

export function createReplaceMealSlotDishCommand(
  slotId: string,
  slotDishId: string,
  dishId: string,
): ReplaceMealSlotDishCommand {
  return { slotId, slotDishId, dishId: dishId.trim() };
}

export function createRemoveMealSlotDishCommand(
  slotId: string,
  slotDishId: string,
): RemoveMealSlotDishCommand {
  return { slotId, slotDishId };
}
