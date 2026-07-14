export interface MealSlotMutationState {
  addPending: boolean;
  replacePending: boolean;
  removePending: boolean;
  addError: boolean;
  replaceError: boolean;
  removeError: boolean;
}

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

export function isMealSlotMutationBusy(state: MealSlotMutationState): boolean {
  return state.addPending || state.replacePending || state.removePending;
}

export function hasMealSlotMutationError(state: MealSlotMutationState): boolean {
  return state.addError || state.replaceError || state.removeError;
}

export function canSubmitDishSelection(value: string, busy: boolean): boolean {
  return !busy && value.trim().length > 0;
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
