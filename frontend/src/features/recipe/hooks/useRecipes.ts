import { useQuery } from "@tanstack/react-query";

import { getProducts, getRecipe, getRecipes } from "../api/recipeApi";

export function useRecipes(includeArchived = false) {
  return useQuery({
    queryKey: ["recipes", { includeArchived }],
    queryFn: () => getRecipes(includeArchived),
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
