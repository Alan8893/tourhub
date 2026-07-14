import type { DishWriteInput } from "../api/dishApi";

export interface DishFormState {
  name: string;
  recipeId: string;
}

export function toDishWriteInput(state: DishFormState): DishWriteInput {
  const name = state.name.trim();
  if (!name) throw new Error("Введите название блюда.");
  if (!state.recipeId) throw new Error("Выберите рецепт.");
  return { name, recipe_id: state.recipeId };
}
