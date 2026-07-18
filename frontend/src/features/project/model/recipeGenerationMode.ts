export type RecipeGenerationMode =
  | "club_only"
  | "club_and_personal"
  | "personal_preferred";

export const RECIPE_GENERATION_MODE_OPTIONS: Array<{
  value: RecipeGenerationMode;
  label: string;
  description: string;
}> = [
  {
    value: "club_only",
    label: "Только клубные рецепты",
    description: "Генератор использует только опубликованные рецепты клуба.",
  },
  {
    value: "club_and_personal",
    label: "Клубные и мои личные",
    description: "Сначала используются клубные варианты, затем доступные личные рецепты.",
  },
  {
    value: "personal_preferred",
    label: "Предпочитать мои личные",
    description: "Сначала используются личные варианты текущего пользователя, затем клубные.",
  },
];

export function getRecipeGenerationModeLabel(mode: RecipeGenerationMode): string {
  return RECIPE_GENERATION_MODE_OPTIONS.find((option) => option.value === mode)?.label ?? mode;
}
