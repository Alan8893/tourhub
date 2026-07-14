import type { RecipeComponentWriteInput } from "../api/recipeApi";

export interface RecipeComponentDraft {
  productId: string;
  componentType: RecipeComponentWriteInput["component_type"];
  amount: string;
  unit: string;
  calculationType: RecipeComponentWriteInput["calculation_type"];
  peopleCount: string;
}

export function validateRecipeName(name: string): string | null {
  return name.trim() ? null : "Введите название рецепта.";
}

export function validateRecipeComponentDraft(draft: RecipeComponentDraft): string | null {
  if (!draft.productId) {
    return "Выберите продукт.";
  }

  const amount = Number(draft.amount);
  if (!Number.isFinite(amount) || amount <= 0) {
    return "Количество должно быть больше нуля.";
  }

  if (!draft.unit.trim()) {
    return "Введите единицу измерения.";
  }

  if (draft.calculationType === "package_per_people") {
    const peopleCount = Number(draft.peopleCount);
    if (!Number.isInteger(peopleCount) || peopleCount <= 0) {
      return "Укажите положительное число человек на упаковку.";
    }
  }

  return null;
}

export function toRecipeComponentWriteInput(
  draft: RecipeComponentDraft,
): RecipeComponentWriteInput {
  return {
    product_id: draft.productId,
    component_type: draft.componentType,
    amount: Number(draft.amount),
    unit: draft.unit.trim(),
    calculation_type: draft.calculationType,
    people_count:
      draft.calculationType === "package_per_people" ? Number(draft.peopleCount) : null,
  };
}
