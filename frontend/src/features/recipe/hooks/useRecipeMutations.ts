import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  addRecipeComponent,
  archiveRecipe,
  createProduct,
  createRecipe,
  createRecipeNote,
  deleteRecipe,
  deleteRecipeComponent,
  deleteRecipeNote,
  renameRecipe,
  restoreRecipe,
  updateRecipeComponent,
  updateRecipeNote,
  type ProductWriteInput,
  type RecipeComponentWriteInput,
  type RecipeNoteWriteInput,
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
  return useMutation({ mutationFn: createRecipe, onSuccess: invalidateRecipes });
}

export function useRenameRecipe() {
  const invalidateRecipes = useInvalidateRecipes();
  return useMutation({
    mutationFn: ({ recipeId, name }: { recipeId: string; name: string }) =>
      renameRecipe(recipeId, name),
    onSuccess: invalidateRecipes,
  });
}

export function useArchiveRecipe() {
  const invalidateRecipes = useInvalidateRecipes();
  return useMutation({ mutationFn: archiveRecipe, onSuccess: invalidateRecipes });
}

export function useRestoreRecipe() {
  const invalidateRecipes = useInvalidateRecipes();
  return useMutation({ mutationFn: restoreRecipe, onSuccess: invalidateRecipes });
}

export function useDeleteRecipe() {
  const invalidateRecipes = useInvalidateRecipes();
  return useMutation({ mutationFn: deleteRecipe, onSuccess: invalidateRecipes });
}

export function useAddRecipeComponent() {
  const invalidateRecipes = useInvalidateRecipes();
  return useMutation({
    mutationFn: ({ recipeId, input }: { recipeId: string; input: RecipeComponentWriteInput }) =>
      addRecipeComponent(recipeId, input),
    onSuccess: invalidateRecipes,
  });
}

export function useUpdateRecipeComponent() {
  const invalidateRecipes = useInvalidateRecipes();
  return useMutation({
    mutationFn: ({ recipeId, componentId, input }: { recipeId: string; componentId: string; input: RecipeComponentWriteInput }) =>
      updateRecipeComponent(recipeId, componentId, input),
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

export function useCreateRecipeNote() {
  const invalidateRecipes = useInvalidateRecipes();
  return useMutation({
    mutationFn: ({ recipeId, input }: { recipeId: string; input: RecipeNoteWriteInput }) =>
      createRecipeNote(recipeId, input),
    onSuccess: invalidateRecipes,
  });
}

export function useUpdateRecipeNote() {
  const invalidateRecipes = useInvalidateRecipes();
  return useMutation({
    mutationFn: ({ recipeId, noteId, input }: { recipeId: string; noteId: string; input: RecipeNoteWriteInput }) =>
      updateRecipeNote(recipeId, noteId, input),
    onSuccess: invalidateRecipes,
  });
}

export function useDeleteRecipeNote() {
  const invalidateRecipes = useInvalidateRecipes();
  return useMutation({
    mutationFn: ({ recipeId, noteId }: { recipeId: string; noteId: string }) =>
      deleteRecipeNote(recipeId, noteId),
    onSuccess: invalidateRecipes,
  });
}

export function useCreateProduct() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (input: ProductWriteInput) => createProduct(input),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ["recipe-products"] }),
  });
}
