export type RecipeLibraryViewState = "loading" | "error" | "empty" | "ready";

interface RecipeLibraryViewStateInput {
  isLoading: boolean;
  isError: boolean;
  recipeCount: number;
}

export function getRecipeLibraryViewState({
  isLoading,
  isError,
  recipeCount,
}: RecipeLibraryViewStateInput): RecipeLibraryViewState {
  if (isLoading) {
    return "loading";
  }

  if (isError) {
    return "error";
  }

  if (recipeCount === 0) {
    return "empty";
  }

  return "ready";
}
