import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { isAxiosError } from "axios";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import type {
  ProductWriteInput,
  RecipeComponent,
  RecipeComponentWriteInput,
} from "@/features/recipe/api/recipeApi";
import {
  useAddRecipeComponent,
  useCreateProduct,
  useCreateRecipe,
  useDeleteRecipeComponent,
  useRenameRecipe,
  useUpdateRecipeComponent,
} from "@/features/recipe/hooks/useRecipeMutations";
import { useRecipe, useRecipeProducts, useRecipes } from "@/features/recipe/hooks/useRecipes";
import { validateRecipeName } from "@/features/recipe/model/recipeEditor";
import { getRecipeLibraryViewState } from "@/features/recipe/model/recipeLibraryViewState";
import ProductDialog from "@/features/recipe/ui/ProductDialog";
import RecipeComponentDialog from "@/features/recipe/ui/RecipeComponentDialog";
import RecipeNotesSection from "@/features/recipe/ui/RecipeNotesSection";

const componentTypeLabels: Record<string, string> = {
  base: "Основа",
  cooking: "Для приготовления",
  optional: "Дополнительно",
  serving_add_on: "Для подачи",
};

const calculationTypeLabels: Record<string, string> = {
  per_person: "на человека",
  fixed_group: "на всю группу",
  package_per_people: "упаковка на группу",
};

function getApiErrorMessage(error: unknown): string {
  if (isAxiosError<{ error?: string }>(error)) {
    return error.response?.data?.error ?? "Не удалось сохранить изменения.";
  }
  return "Не удалось сохранить изменения.";
}

export default function RecipesPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const recipesQuery = useRecipes();
  const recipeQuery = useRecipe(id);
  const createRecipeMutation = useCreateRecipe();
  const renameRecipeMutation = useRenameRecipe();
  const addComponentMutation = useAddRecipeComponent();
  const updateComponentMutation = useUpdateRecipeComponent();
  const deleteComponentMutation = useDeleteRecipeComponent();
  const createProductMutation = useCreateProduct();

  const [nameDialogMode, setNameDialogMode] = useState<"create" | "rename" | null>(null);
  const [recipeName, setRecipeName] = useState("");
  const [nameValidationError, setNameValidationError] = useState<string | null>(null);
  const [componentDialogOpen, setComponentDialogOpen] = useState(false);
  const [editingComponent, setEditingComponent] = useState<RecipeComponent | null>(null);
  const [componentError, setComponentError] = useState<string | null>(null);
  const [productDialogOpen, setProductDialogOpen] = useState(false);
  const [productError, setProductError] = useState<string | null>(null);

  const productsQuery = useRecipeProducts(componentDialogOpen || productDialogOpen);
  const recipes = recipesQuery.data?.items ?? [];
  const viewState = getRecipeLibraryViewState({
    isLoading: recipesQuery.isLoading,
    isError: recipesQuery.isError,
    recipeCount: recipes.length,
  });
  const nameMutation = nameDialogMode === "create" ? createRecipeMutation : renameRecipeMutation;
  const componentMutation = editingComponent ? updateComponentMutation : addComponentMutation;

  const openCreateDialog = () => {
    setRecipeName("");
    setNameValidationError(null);
    createRecipeMutation.reset();
    setNameDialogMode("create");
  };

  const openRenameDialog = () => {
    if (!recipeQuery.data) return;
    setRecipeName(recipeQuery.data.name);
    setNameValidationError(null);
    renameRecipeMutation.reset();
    setNameDialogMode("rename");
  };

  const submitRecipeName = async () => {
    const error = validateRecipeName(recipeName);
    setNameValidationError(error);
    if (error) return;

    if (nameDialogMode === "create") {
      const recipe = await createRecipeMutation.mutateAsync(recipeName.trim());
      setNameDialogMode(null);
      navigate(`/recipes/${recipe.id}`);
    } else if (nameDialogMode === "rename" && id) {
      await renameRecipeMutation.mutateAsync({ recipeId: id, name: recipeName.trim() });
      setNameDialogMode(null);
    }
  };

  const openAddComponent = () => {
    setEditingComponent(null);
    setComponentError(null);
    addComponentMutation.reset();
    setComponentDialogOpen(true);
  };

  const openEditComponent = (component: RecipeComponent) => {
    setEditingComponent(component);
    setComponentError(null);
    updateComponentMutation.reset();
    setComponentDialogOpen(true);
  };

  const submitComponent = async (input: RecipeComponentWriteInput) => {
    if (!id) return;
    setComponentError(null);
    try {
      if (editingComponent) {
        await updateComponentMutation.mutateAsync({
          recipeId: id,
          componentId: editingComponent.id,
          input,
        });
      } else {
        await addComponentMutation.mutateAsync({ recipeId: id, input });
      }
      setComponentDialogOpen(false);
      setEditingComponent(null);
    } catch (error) {
      setComponentError(getApiErrorMessage(error));
    }
  };

  const deleteComponent = async (component: RecipeComponent) => {
    if (!id || !window.confirm(`Удалить «${component.product.name}» из рецепта?`)) return;
    await deleteComponentMutation.mutateAsync({ recipeId: id, componentId: component.id });
  };

  const submitProduct = async (input: ProductWriteInput) => {
    setProductError(null);
    try {
      await createProductMutation.mutateAsync(input);
      setProductDialogOpen(false);
    } catch (error) {
      setProductError(getApiErrorMessage(error));
    }
  };

  return (
    <Stack spacing={3}>
      <Stack
        direction={{ xs: "column", sm: "row" }}
        spacing={2}
        justifyContent="space-between"
        alignItems={{ xs: "stretch", sm: "flex-start" }}
      >
        <Box>
          <Typography variant="h4" component="h1">Рецепты</Typography>
          <Typography color="text.secondary">
            Библиотека походных рецептов и их продуктовых компонентов.
          </Typography>
        </Box>
        <Button variant="contained" onClick={openCreateDialog}>Создать рецепт</Button>
      </Stack>

      {viewState === "loading" && (
        <Stack alignItems="center" py={6}><CircularProgress aria-label="Загрузка рецептов" /></Stack>
      )}
      {viewState === "error" && (
        <Alert severity="error">Не удалось загрузить библиотеку рецептов.</Alert>
      )}
      {viewState === "empty" && (
        <Alert severity="info">В библиотеке пока нет рецептов. Создайте первый рецепт.</Alert>
      )}

      {viewState === "ready" && (
        <Box sx={{ display: "grid", gridTemplateColumns: { xs: "1fr", md: "minmax(260px, 360px) 1fr" }, gap: 3, alignItems: "start" }}>
          <Paper variant="outlined">
            <List disablePadding>
              {recipes.map((recipe, index) => (
                <Box key={recipe.id}>
                  {index > 0 && <Divider />}
                  <ListItemButton selected={recipe.id === id} onClick={() => navigate(`/recipes/${recipe.id}`)}>
                    <ListItemText
                      primary={recipe.name}
                      secondary={`${recipe.component_count} компонентов · ${recipe.note_count} заметок`}
                    />
                  </ListItemButton>
                </Box>
              ))}
            </List>
          </Paper>

          <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 }, minHeight: 240 }}>
            {!id && (
              <Stack spacing={1} alignItems="center" justifyContent="center" minHeight={190}>
                <Typography variant="h6">Выберите рецепт</Typography>
                <Typography color="text.secondary" textAlign="center">
                  Компоненты и заметки выбранного рецепта появятся здесь.
                </Typography>
              </Stack>
            )}
            {id && recipeQuery.isLoading && (
              <Stack alignItems="center" py={6}><CircularProgress aria-label="Загрузка рецепта" /></Stack>
            )}
            {id && recipeQuery.isError && (
              <Alert severity="error">Не удалось загрузить выбранный рецепт.</Alert>
            )}

            {recipeQuery.data && (
              <Stack spacing={3}>
                <Stack direction={{ xs: "column", sm: "row" }} spacing={2} justifyContent="space-between" alignItems={{ xs: "stretch", sm: "flex-start" }}>
                  <Box>
                    <Typography variant="h5" component="h2">{recipeQuery.data.name}</Typography>
                    <Typography color="text.secondary">
                      {recipeQuery.data.components.length} компонентов · {recipeQuery.data.notes.length} заметок
                    </Typography>
                  </Box>
                  <Button variant="outlined" onClick={openRenameDialog}>Переименовать</Button>
                </Stack>

                <Box>
                  <Stack direction={{ xs: "column", sm: "row" }} spacing={2} justifyContent="space-between" alignItems={{ xs: "stretch", sm: "center" }} mb={1.5}>
                    <Typography variant="h6">Состав</Typography>
                    <Button size="small" variant="contained" onClick={openAddComponent}>Добавить компонент</Button>
                  </Stack>
                  {deleteComponentMutation.isError && (
                    <Alert severity="error" sx={{ mb: 1.5 }}>{getApiErrorMessage(deleteComponentMutation.error)}</Alert>
                  )}
                  {recipeQuery.data.components.length === 0 ? (
                    <Typography color="text.secondary">Компоненты пока не добавлены.</Typography>
                  ) : (
                    <Stack spacing={1.5}>
                      {recipeQuery.data.components.map((component) => (
                        <Paper key={component.id} variant="outlined" sx={{ p: 2 }}>
                          <Stack spacing={1.5}>
                            <Stack direction={{ xs: "column", sm: "row" }} spacing={1} justifyContent="space-between">
                              <Box>
                                <Typography fontWeight={600}>{component.product.name}</Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {component.product.category ?? "Без категории"}
                                </Typography>
                              </Box>
                              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                                <Chip size="small" label={componentTypeLabels[component.component_type] ?? component.component_type} />
                                <Chip size="small" variant="outlined" label={`${component.amount} ${component.unit}`} />
                              </Stack>
                            </Stack>
                            <Typography variant="body2">
                              Расчёт: {calculationTypeLabels[component.calculation_type] ?? component.calculation_type}
                              {component.people_count ? `, на ${component.people_count} чел.` : ""}
                            </Typography>
                            {component.product.package_size && (
                              <Typography variant="body2" color="text.secondary">
                                Упаковка: {component.product.package_size} {component.product.unit}
                              </Typography>
                            )}
                            <Stack direction="row" spacing={1} justifyContent="flex-end">
                              <Button size="small" onClick={() => openEditComponent(component)}>Изменить</Button>
                              <Button size="small" color="error" onClick={() => void deleteComponent(component)} disabled={deleteComponentMutation.isPending}>Удалить</Button>
                            </Stack>
                          </Stack>
                        </Paper>
                      ))}
                    </Stack>
                  )}
                </Box>

                <RecipeNotesSection recipeId={recipeQuery.data.id} notes={recipeQuery.data.notes} />
              </Stack>
            )}
          </Paper>
        </Box>
      )}

      <Dialog open={nameDialogMode !== null} onClose={nameMutation.isPending ? undefined : () => setNameDialogMode(null)} fullWidth maxWidth="sm">
        <DialogTitle>{nameDialogMode === "create" ? "Новый рецепт" : "Переименовать рецепт"}</DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {(nameValidationError || nameMutation.isError) && (
              <Alert severity="error">{nameValidationError ?? getApiErrorMessage(nameMutation.error)}</Alert>
            )}
            <TextField
              autoFocus
              label="Название"
              value={recipeName}
              onChange={(event) => setRecipeName(event.target.value)}
              onKeyDown={(event) => { if (event.key === "Enter") void submitRecipeName(); }}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNameDialogMode(null)} disabled={nameMutation.isPending}>Отмена</Button>
          <Button variant="contained" onClick={() => void submitRecipeName()} disabled={nameMutation.isPending}>
            {nameMutation.isPending ? "Сохранение…" : "Сохранить"}
          </Button>
        </DialogActions>
      </Dialog>

      <RecipeComponentDialog
        open={componentDialogOpen}
        products={productsQuery.data?.items ?? []}
        component={editingComponent}
        isSubmitting={componentMutation.isPending}
        errorMessage={productsQuery.isError ? "Не удалось загрузить справочник продуктов." : componentError}
        onClose={() => { setComponentDialogOpen(false); setEditingComponent(null); }}
        onCreateProduct={() => { setProductError(null); createProductMutation.reset(); setProductDialogOpen(true); }}
        onSubmit={(input) => void submitComponent(input)}
      />

      <ProductDialog
        open={productDialogOpen}
        isSubmitting={createProductMutation.isPending}
        errorMessage={productError}
        onClose={() => setProductDialogOpen(false)}
        onSubmit={(input) => void submitProduct(input)}
      />
    </Stack>
  );
}
