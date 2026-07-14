import type { ProductWriteInput, RecipeNoteWriteInput } from "../api/recipeApi";

export interface RecipeNoteDraft {
  type: RecipeNoteWriteInput["type"];
  text: string;
  priority: string;
}

export interface ProductDraft {
  name: string;
  category: string;
  unit: string;
  packageSize: string;
}

export function validateRecipeNoteDraft(draft: RecipeNoteDraft): string | null {
  if (!draft.text.trim()) {
    return "Введите текст заметки.";
  }

  const priority = Number(draft.priority);
  if (!Number.isInteger(priority) || priority < 0) {
    return "Приоритет должен быть целым неотрицательным числом.";
  }

  return null;
}

export function toRecipeNoteWriteInput(draft: RecipeNoteDraft): RecipeNoteWriteInput {
  return {
    type: draft.type,
    text: draft.text.trim(),
    priority: Number(draft.priority),
  };
}

export function validateProductDraft(draft: ProductDraft): string | null {
  if (!draft.name.trim()) {
    return "Введите название продукта.";
  }

  if (!draft.unit.trim()) {
    return "Введите единицу измерения.";
  }

  if (draft.packageSize.trim()) {
    const packageSize = Number(draft.packageSize);
    if (!Number.isInteger(packageSize) || packageSize <= 0) {
      return "Размер упаковки должен быть положительным целым числом.";
    }
  }

  return null;
}

export function toProductWriteInput(draft: ProductDraft): ProductWriteInput {
  return {
    name: draft.name.trim(),
    category: draft.category.trim() || null,
    unit: draft.unit.trim(),
    package_size: draft.packageSize.trim() ? Number(draft.packageSize) : null,
  };
}
