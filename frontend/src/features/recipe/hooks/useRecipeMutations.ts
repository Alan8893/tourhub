import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  addRecipeComponent,
  createRecipe,
  deleteRecipeComponent,
  renameRecipe,
  updateRecipeComponent,
  type RecipeComponentWriteInput,
} from "../api/recipeApi";

function useInvalidateRecipes() {
  const queryClient = useQueryClient();

  return () =>
    queryClient.invalidateQueries({
      queryKey: ["recipes"],
    });
}

export function useCreateRecipe() {
  const invalidateRecipes = useInvalidateRecipes();

  return useMutation({
    mutationFn: createRecipe,
    onSuccess: invalidateRecipes,
  });
}

export function useRenameRecipe() {
  const invalidateRecipes = useInvalidateRecipes();

  return useMutation({
    mutationFn: ({ recipeId, name }: { recipeId: string; name: string }) =>
      renameRecipe(recipeId, name),
    onSuccess: invalidateRecipes,
  });
}

export function useAddRecipeComponent() {
  const invalidateRecipes = useInvalidateRecipes();

  return useMutation({
    mutationFn: ({
      recipeId,
      input,
    }: {
      recipeId: string;
      input: RecipeComponentWriteInput;
    }) => addRecipeComponent(recipeId, input),
    onSuccess: invalidateRecipes,
  });
}

export function useUpdateRecipeComponent() {
  const invalidateRecipes = useInvalidateRecipes();

  return useMutation({
    mutationFn: ({
      recipeId,
      componentId,
      input,
    }: {
      recipeId: string;
      componentId: string;
      input: RecipeComponentWriteInput;
    }) => updateRecipeComponent(recipeId, componentId, input),
    onSuccess: invalidateRecipes,
  });
}

export function useDeleteRecipeComponent() {
  const invalidateRecipes = useInvalidateRecipes();

  return useMutation({
    mutationFn: ({ recipeId, componentId }: { recipeId: string; componentId: string }) =>
      deleteRecipeComponent(recipeId, componentId),
    onSuccess: invalidateRecipes,
  });
}
