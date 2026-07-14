import { useQuery } from "@tanstack/react-query";

import { getProducts, getRecipe, getRecipes } from "../api/recipeApi";

export function useRecipes() {
  return useQuery({
    queryKey: ["recipes"],
    queryFn: getRecipes,
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
