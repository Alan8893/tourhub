import { useQuery } from "@tanstack/react-query";

import {
  getProducts,
  getRecipe,
  getRecipes,
  type RecipeView,
} from "../api/recipeApi";

export function useRecipes(includeArchived = false, view: RecipeView = "library") {
  return useQuery({
    queryKey: ["recipes", { includeArchived, view }],
    queryFn: () => getRecipes(includeArchived, view),
  });
}

export function useRecipe(recipeId: string | undefined) {
  return useQuery({
    queryKey: ["recipes", recipeId],
    queryFn: () => getRecipe(recipeId!),
    enabled: Boolean(recipeId),
  });
}

export function useRecipeProducts(enabled = true) {
  return useQuery({
    queryKey: ["recipe-products"],
    queryFn: getProducts,
    enabled,
  });
}
