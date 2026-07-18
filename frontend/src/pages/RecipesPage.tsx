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
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import { isAxiosError } from "axios";
import { useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import type {
  ProductWriteInput,
  RecipeComponent,
  RecipeComponentWriteInput,
  RecipeScope,
} from "@/features/recipe/api/recipeApi";
import {
  useAddRecipeComponent,
  useArchiveRecipe,
  useCreateProduct,
  useCreateRecipe,
  useDeleteRecipe,
  useDeleteRecipeComponent,
  useRenameRecipe,
  useRestoreRecipe,
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

function recipeScopeLabel(scope: RecipeScope | undefined): string {
  return scope === "personal" ? "Личный" : "Клубный";
}

function capability(value: boolean | undefined, legacyFallback: boolean): boolean {
  return value ?? legacyFallback;
}

function getApiErrorMessage(error: unknown): string {
  if (isAxiosError<{ error?: string; detail?: string }>(error)) {
    const message = error.response?.data?.error ?? error.response?.data?.detail;
    if (message === "Recipe is used by a dish and cannot be deleted") {
      return "Рецепт используется блюдом. Его можно архивировать, но нельзя удалить.";
    }
    if (message === "Recipe cannot be changed by the current user") {
      return "У текущей учётной записи нет права изменять этот рецепт.";
    }
    if (message === "Only an administrator may permanently delete a recipe") {
      return "Навсегда удалить рецепт может только администратор.";
    }
    return message ?? "Не удалось сохранить изменения.";
  }
  return "Не удалось сохранить изменения.";
}

export default function RecipesPage() {
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const [showArchived, setShowArchived] = useState(false);
  const recipesQuery = useRecipes(showArchived);
  const recipeQuery = useRecipe(id);
  const createRecipeMutation = useCreateRecipe();
  const renameRecipeMutation = useRenameRecipe();
  const archiveRecipeMutation = useArchiveRecipe();
  const restoreRecipeMutation = useRestoreRecipe();
  const deleteRecipeMutation = useDeleteRecipe();
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
  const [lifecycleError, setLifecycleError] = useState<string | null>(null);

  const productsQuery = useRecipeProducts(componentDialogOpen || productDialogOpen);
  const recipes = recipesQuery.data?.items ?? [];
  const viewState = getRecipeLibraryViewState({
    isLoading: recipesQuery.isLoading,
    isError: recipesQuery.isError,
    recipeCount: recipes.length,
  });
  const nameMutation = nameDialogMode === "create" ? createRecipeMutation : renameRecipeMutation;
  const componentMutation = editingComponent ? updateComponentMutation : addComponentMutation;
  const selectedRecipe = recipeQuery.data;
  const canEditSelected = selectedRecipe
    ? capability(selectedRecipe.can_edit, !selectedRecipe.is_archived)
    : false;
  const canArchiveSelected = selectedRecipe
    ? capability(selectedRecipe.can_archive, !selectedRecipe.is_archived)
    : false;
  const canRestoreSelected = selectedRecipe
    ? capability(selectedRecipe.can_restore, selectedRecipe.is_archived)
    : false;
  const canDeleteSelected = selectedRecipe
    ? capability(selectedRecipe.can_delete, true)
    : false;
  const lifecyclePending =
    archiveRecipeMutation.isPending ||
    restoreRecipeMutation.isPending ||
    deleteRecipeMutation.isPending;

  const openCreateDialog = () => {
    setRecipeName("");
    setNameValidationError(null);
    createRecipeMutation.reset();
    setNameDialogMode("create");
  };

  const openRenameDialog = () => {
    if (!selectedRecipe || !canEditSelected) return;
    setRecipeName(selectedRecipe.name);
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
      setShowArchived(false);
      navigate(`/recipes/${recipe.id}`);
    } else if (nameDialogMode === "rename" && id) {
      await renameRecipeMutation.mutateAsync({ recipeId: id, name: recipeName.trim() });
      setNameDialogMode(null);
    }
  };

  const openAddComponent = () => {
    if (!canEditSelected) return;
    setEditingComponent(null);
    setComponentError(null);
    addComponentMutation.reset();
    setComponentDialogOpen(true);
  };

  const openEditComponent = (component: RecipeComponent) => {
    if (!canEditSelected) return;
    setEditingComponent(component);
    setComponentError(null);
    updateComponentMutation.reset();
    setComponentDialogOpen(true);
  };

  const submitComponent = async (input: RecipeComponentWriteInput) => {
    if (!id || !canEditSelected) return;
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
    if (
      !id ||
      !canEditSelected ||
      !window.confirm(`Удалить «${component.product.name}» из рецепта?`)
    ) {
      return;
    }
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

  const archiveSelectedRecipe = async () => {
    if (
      !id ||
      !selectedRecipe ||
      !canArchiveSelected ||
      !window.confirm(`Архивировать рецепт «${selectedRecipe.name}»?`)
    ) {
      return;
    }
    setLifecycleError(null);
    try {
      await archiveRecipeMutation.mutateAsync(id);
      setShowArchived(false);
      navigate("/recipes");
    } catch (error) {
      setLifecycleError(getApiErrorMessage(error));
    }
  };

  const restoreSelectedRecipe = async () => {
    if (!id || !canRestoreSelected) return;
    setLifecycleError(null);
    try {
      await restoreRecipeMutation.mutateAsync(id);
      setShowArchived(false);
      navigate(`/recipes/${id}`);
    } catch (error) {
      setLifecycleError(getApiErrorMessage(error));
    }
  };

  const deleteSelectedRecipe = async () => {
    if (
      !id ||
      !selectedRecipe ||
      !canDeleteSelected ||
      !window.confirm(`Удалить рецепт «${selectedRecipe.name}» навсегда?`)
    ) {
      return;
    }
    setLifecycleError(null);
    try {
      await deleteRecipeMutation.mutateAsync(id);
      navigate("/recipes");
    } catch (error) {
      setLifecycleError(getApiErrorMessage(error));
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
          <Typography variant="h4" component="h1">
            Рецепты
          </Typography>
          <Typography color="text.secondary">
            Клубные стандарты и личные рецепты текущего пользователя.
          </Typography>
        </Box>
        <Button variant="contained" onClick={openCreateDialog}>
          Создать личный рецепт
        </Button>
      </Stack>

      <ToggleButtonGroup
        exclusive
        size="small"
        value={showArchived ? "archived" : "active"}
        onChange={(_, value: "active" | "archived" | null) => {
          if (!value) return;
          setShowArchived(value === "archived");
          navigate("/recipes");
        }}
      >
        <ToggleButton value="active">Активные</ToggleButton>
        <ToggleButton value="archived">Архив</ToggleButton>
      </ToggleButtonGroup>

      {viewState === "loading" && (
        <Stack alignItems="center" py={6}>
          <CircularProgress aria-label="Загрузка рецептов" />
        </Stack>
      )}
      {viewState === "error" && (
        <Alert severity="error">Не удалось загрузить библиотеку рецептов.</Alert>
      )}
      {viewState === "empty" && (
        <Alert severity="info">
          {showArchived
            ? "Архив рецептов пуст."
            : "Доступных рецептов пока нет. Создайте личный рецепт."}
        </Alert>
      )}

      {viewState === "ready" && (
        <Box
          sx={{
            display: "grid",
            gridTemplateColumns: { xs: "1fr", md: "minmax(260px, 360px) 1fr" },
            gap: 3,
            alignItems: "start",
          }}
        >
          <Paper variant="outlined">
            <List disablePadding>
              {recipes.map((recipe, index) => {
                const owner = recipe.owner_display_name
                  ? ` · ${recipe.owner_display_name}`
                  : "";
                return (
                  <Box key={recipe.id}>
                    {index > 0 && <Divider />}
                    <ListItemButton
                      selected={recipe.id === id}
                      onClick={() => navigate(`/recipes/${recipe.id}`)}
                    >
                      <ListItemText
                        primary={recipe.name}
                        secondary={`${recipeScopeLabel(recipe.scope)}${owner} · ${recipe.component_count} компонентов · ${recipe.note_count} заметок`}
                      />
                      <Stack direction="row" spacing={0.5} flexWrap="wrap" useFlexGap>
                        <Chip
                          size="small"
                          variant="outlined"
                          label={recipeScopeLabel(recipe.scope)}
                        />
                        {recipe.is_archived && <Chip size="small" label="Архив" />}
                      </Stack>
                    </ListItemButton>
                  </Box>
                );
              })}
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
              <Stack alignItems="center" py={6}>
                <CircularProgress aria-label="Загрузка рецепта" />
              </Stack>
            )}
            {id && recipeQuery.isError && (
              <Alert severity="error">Не удалось загрузить выбранный рецепт.</Alert>
            )}

            {selectedRecipe && (
              <Stack spacing={3}>
                {lifecycleError && <Alert severity="error">{lifecycleError}</Alert>}
                {selectedRecipe.is_archived && (
                  <Alert severity="warning">
                    Рецепт находится в архиве. Пользователь с соответствующими правами может его
                    восстановить.
                  </Alert>
                )}
                {!selectedRecipe.is_archived && !canEditSelected && (
                  <Alert severity="info">
                    Этот клубный рецепт доступен текущей учётной записи только для просмотра.
                  </Alert>
                )}
                <Stack
                  direction={{ xs: "column", sm: "row" }}
                  spacing={2}
                  justifyContent="space-between"
                  alignItems={{ xs: "stretch", sm: "flex-start" }}
                >
                  <Box>
                    <Stack direction="row" spacing={1} alignItems="center" flexWrap="wrap" useFlexGap>
                      <Typography variant="h5" component="h2">
                        {selectedRecipe.name}
                      </Typography>
                      <Chip
                        size="small"
                        variant="outlined"
                        label={recipeScopeLabel(selectedRecipe.scope)}
                      />
                      {selectedRecipe.is_archived && <Chip size="small" label="Архив" />}
                    </Stack>
                    <Typography color="text.secondary">
                      {selectedRecipe.owner_display_name
                        ? `Владелец: ${selectedRecipe.owner_display_name}. `
                        : "Клубный стандарт. "}
                      {selectedRecipe.components.length} компонентов · {selectedRecipe.notes.length}{" "}
                      заметок
                    </Typography>
                  </Box>
                  <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                    {canEditSelected && (
                      <Button variant="outlined" onClick={openRenameDialog}>
                        Переименовать
                      </Button>
                    )}
                    {canRestoreSelected && (
                      <Button
                        variant="contained"
                        onClick={() => void restoreSelectedRecipe()}
                        disabled={lifecyclePending}
                      >
                        Восстановить
                      </Button>
                    )}
                    {canArchiveSelected && (
                      <Button
                        color="warning"
                        variant="outlined"
                        onClick={() => void archiveSelectedRecipe()}
                        disabled={lifecyclePending}
                      >
                        Архивировать
                      </Button>
                    )}
                    {canDeleteSelected && (
                      <Button
                        color="error"
                        variant="outlined"
                        onClick={() => void deleteSelectedRecipe()}
                        disabled={lifecyclePending}
                      >
                        Удалить
                      </Button>
                    )}
                  </Stack>
                </Stack>

                <Box>
                  <Stack
                    direction={{ xs: "column", sm: "row" }}
                    spacing={2}
                    justifyContent="space-between"
                    alignItems={{ xs: "stretch", sm: "center" }}
                    mb={1.5}
                  >
                    <Typography variant="h6">Состав</Typography>
                    {canEditSelected && (
                      <Button size="small" variant="contained" onClick={openAddComponent}>
                        Добавить компонент
                      </Button>
                    )}
                  </Stack>
                  {deleteComponentMutation.isError && (
                    <Alert severity="error" sx={{ mb: 1.5 }}>
                      {getApiErrorMessage(deleteComponentMutation.error)}
                    </Alert>
                  )}
                  {selectedRecipe.components.length === 0 ? (
                    <Typography color="text.secondary">Компоненты пока не добавлены.</Typography>
                  ) : (
                    <Stack spacing={1.5}>
                      {selectedRecipe.components.map((component) => (
                        <Paper key={component.id} variant="outlined" sx={{ p: 2 }}>
                          <Stack spacing={1.5}>
                            <Stack
                              direction={{ xs: "column", sm: "row" }}
                              spacing={1}
                              justifyContent="space-between"
                            >
                              <Box>
                                <Typography fontWeight={600}>{component.product.name}</Typography>
                                <Typography variant="body2" color="text.secondary">
                                  {component.product.category ?? "Без категории"}
                                </Typography>
                              </Box>
                              <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
                                <Chip
                                  size="small"
                                  label={
                                    componentTypeLabels[component.component_type] ??
                                    component.component_type
                                  }
                                />
                                <Chip
                                  size="small"
                                  variant="outlined"
                                  label={`${component.amount} ${component.unit}`}
                                />
                              </Stack>
                            </Stack>
                            <Typography variant="body2">
                              Расчёт:{" "}
                              {calculationTypeLabels[component.calculation_type] ??
                                component.calculation_type}
                              {component.people_count
                                ? `, на ${component.people_count} чел.`
                                : ""}
                            </Typography>
                            {component.product.package_size && (
                              <Typography variant="body2" color="text.secondary">
                                Упаковка: {component.product.package_size} {component.product.unit}
                              </Typography>
                            )}
                            {canEditSelected && (
                              <Stack direction="row" spacing={1} justifyContent="flex-end">
                                <Button size="small" onClick={() => openEditComponent(component)}>
                                  Изменить
                                </Button>
                                <Button
                                  size="small"
                                  color="error"
                                  onClick={() => void deleteComponent(component)}
                                  disabled={deleteComponentMutation.isPending}
                                >
                                  Удалить
                                </Button>
                              </Stack>
                            )}
                          </Stack>
                        </Paper>
                      ))}
                    </Stack>
                  )}
                </Box>

                <RecipeNotesSection
                  recipeId={selectedRecipe.id}
                  notes={selectedRecipe.notes}
                  readOnly={!canEditSelected}
                />
              </Stack>
            )}
          </Paper>
        </Box>
      )}

      <Dialog
        open={nameDialogMode !== null}
        onClose={nameMutation.isPending ? undefined : () => setNameDialogMode(null)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>
          {nameDialogMode === "create" ? "Новый личный рецепт" : "Переименовать рецепт"}
        </DialogTitle>
        <DialogContent>
          <Stack spacing={2} sx={{ mt: 1 }}>
            {nameDialogMode === "create" && (
              <Alert severity="info">
                Рецепт будет личным и доступным для редактирования владельцу. Публикация в клубную
                библиотеку появится в следующем этапе.
              </Alert>
            )}
            {(nameValidationError || nameMutation.isError) && (
              <Alert severity="error">
                {nameValidationError ?? getApiErrorMessage(nameMutation.error)}
              </Alert>
            )}
            <TextField
              autoFocus
              label="Название"
              value={recipeName}
              onChange={(event) => setRecipeName(event.target.value)}
              onKeyDown={(event) => {
                if (event.key === "Enter") void submitRecipeName();
              }}
              fullWidth
            />
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setNameDialogMode(null)} disabled={nameMutation.isPending}>
            Отмена
          </Button>
          <Button
            variant="contained"
            onClick={() => void submitRecipeName()}
            disabled={nameMutation.isPending}
          >
            {nameMutation.isPending ? "Сохранение…" : "Сохранить"}
          </Button>
        </DialogActions>
      </Dialog>

      <RecipeComponentDialog
        open={componentDialogOpen}
        products={productsQuery.data?.items ?? []}
        component={editingComponent}
        isSubmitting={componentMutation.isPending}
        errorMessage={
          productsQuery.isError ? "Не удалось загрузить справочник продуктов." : componentError
        }
        onClose={() => {
          setComponentDialogOpen(false);
          setEditingComponent(null);
        }}
        onCreateProduct={() => {
          setProductError(null);
          createProductMutation.reset();
          setProductDialogOpen(true);
        }}
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
