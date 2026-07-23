import { FormEvent, useEffect, useRef, useState } from "react";
import { useNavigate, useSearchParams } from "react-router-dom";
import {
  Alert,
  Box,
  Button,
  FormControl,
  FormControlLabel,
  FormLabel,
  Paper,
  Radio,
  RadioGroup,
  TextField,
  Typography,
} from "@mui/material";

import { useCopyProject } from "../features/project/hooks/useCopyProject";
import { useCreateProject } from "../features/project/hooks/useCreateProject";
import { useProject } from "../features/project/hooks/useProject";
import {
  buildProjectCopyDefaults,
  projectCopySummary,
} from "../features/project/model/projectCopy";
import {
  RECIPE_GENERATION_MODE_OPTIONS,
  type RecipeGenerationMode,
} from "../features/project/model/recipeGenerationMode";

const mealOptions = [
  { value: "breakfast", label: "Завтрак" },
  { value: "snack", label: "Перекус" },
  { value: "lunch", label: "Обед" },
  { value: "dinner", label: "Ужин" },
] as const;

function copySourceIdFromSearch(searchParams: URLSearchParams): number | null {
  const raw = searchParams.get("copyFrom");
  if (!raw) return null;
  const value = Number(raw);
  return Number.isInteger(value) && value > 0 ? value : null;
}

export default function CreateProjectPage() {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const copySourceId = copySourceIdFromSearch(searchParams);
  const isCopyMode = copySourceId !== null;
  const sourceQuery = useProject(copySourceId ?? 0, isCopyMode);
  const createProject = useCreateProject();
  const copyProject = useCopyProject(copySourceId ?? 0);
  const initializedFromSource = useRef(false);

  const [name, setName] = useState("");
  const [participants, setParticipants] = useState(1);
  const [days, setDays] = useState(1);
  const [startDate, setStartDate] = useState("");
  const [firstMeal, setFirstMeal] = useState("dinner");
  const [lastMeal, setLastMeal] = useState("dinner");
  const [recipeGenerationMode, setRecipeGenerationMode] =
    useState<RecipeGenerationMode>("club_only");
  const [validationError, setValidationError] = useState<string | null>(null);
  const [copySummary, setCopySummary] = useState<string | null>(null);

  useEffect(() => {
    if (!isCopyMode || !sourceQuery.data || initializedFromSource.current) return;
    const defaults = buildProjectCopyDefaults(sourceQuery.data);
    setName(defaults.name);
    setParticipants(defaults.participants);
    setDays(defaults.days);
    setStartDate(defaults.start_date ?? "");
    setFirstMeal(defaults.first_meal ?? "breakfast");
    setLastMeal(defaults.last_meal ?? "dinner");
    setRecipeGenerationMode(defaults.recipe_generation_mode ?? "club_only");
    initializedFromSource.current = true;
  }, [isCopyMode, sourceQuery.data]);

  async function submit(event: FormEvent) {
    event.preventDefault();

    const firstIndex = mealOptions.findIndex((meal) => meal.value === firstMeal);
    const lastIndex = mealOptions.findIndex((meal) => meal.value === lastMeal);
    if (days === 1 && firstIndex > lastIndex) {
      setValidationError("В однодневном походе последний приём пищи не может быть раньше первого.");
      return;
    }
    if (isCopyMode && sourceQuery.data?.status !== "completed") {
      setValidationError("Копировать можно только завершённый проект.");
      return;
    }

    setValidationError(null);
    setCopySummary(null);
    const payload = {
      name,
      participants,
      days,
      start_date: startDate || undefined,
      first_meal: firstMeal,
      last_meal: lastMeal,
      recipe_generation_mode: recipeGenerationMode,
    };

    if (isCopyMode && copySourceId !== null) {
      const result = await copyProject.mutateAsync(payload);
      setCopySummary(projectCopySummary(result));
      navigate(`/projects/${result.project_id}`);
      return;
    }

    const project = await createProject.mutateAsync(payload);
    navigate(`/projects/${project.id}`);
  }

  const isSaving = createProject.isPending || copyProject.isPending;
  const sourceIsNotCompleted = isCopyMode && sourceQuery.data?.status !== "completed";

  return (
    <Paper sx={{ maxWidth: 640, mx: "auto", mt: 5, p: { xs: 2.5, sm: 4 } }}>
      <Typography variant="h4" sx={{ mb: 1 }}>
        {isCopyMode ? "Копирование похода" : "Создание похода"}
      </Typography>

      <Typography variant="body2" sx={{ mb: 3 }}>
        {isCopyMode
          ? "Проверьте параметры нового похода. Завершённый источник останется без изменений."
          : "Укажите параметры похода. Они будут использоваться при подготовке меню и документов."}
      </Typography>

      <Box component="form" onSubmit={submit} sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {validationError && <Alert severity="error">{validationError}</Alert>}
        {copySummary && <Alert severity="success">{copySummary}</Alert>}
        {isCopyMode && sourceQuery.isLoading && (
          <Alert severity="info">Загружаем завершённый проект-источник…</Alert>
        )}
        {isCopyMode && sourceQuery.isError && (
          <Alert severity="error">Не удалось загрузить проект-источник для копирования.</Alert>
        )}
        {sourceIsNotCompleted && sourceQuery.data && (
          <Alert severity="warning">Копировать можно только завершённый проект.</Alert>
        )}
        {isCopyMode && sourceQuery.data?.status === "completed" && (
          <Alert severity="info">
            Из источника «{sourceQuery.data.name}» будут перенесены только совпадающие назначения меню с действующими блюдами и рецептами.
          </Alert>
        )}
        {createProject.isError && (
          <Alert severity="error">Не удалось создать поход. Проверьте параметры и повторите попытку.</Alert>
        )}
        {copyProject.isError && (
          <Alert severity="error">Не удалось скопировать проект. Проверьте доступ и параметры.</Alert>
        )}

        <TextField
          label="Название похода"
          placeholder="Например: Карелия 2026"
          value={name}
          onChange={(event) => setName(event.target.value)}
          disabled={isCopyMode && sourceQuery.isLoading}
          required
        />

        <TextField
          label="Количество участников"
          type="number"
          value={participants}
          onChange={(event) => setParticipants(Number(event.target.value))}
          inputProps={{ min: 1 }}
          disabled={isCopyMode && sourceQuery.isLoading}
          required
        />

        <TextField
          label="Количество дней"
          type="number"
          value={days}
          onChange={(event) => setDays(Number(event.target.value))}
          inputProps={{ min: 1 }}
          disabled={isCopyMode && sourceQuery.isLoading}
          required
        />

        <TextField
          label="Дата начала похода"
          type="date"
          value={startDate}
          onChange={(event) => setStartDate(event.target.value)}
          InputLabelProps={{ shrink: true }}
          disabled={isCopyMode && sourceQuery.isLoading}
        />

        <FormControl disabled={isCopyMode && sourceQuery.isLoading}>
          <FormLabel>Первый приём пищи</FormLabel>
          <RadioGroup value={firstMeal} onChange={(event) => setFirstMeal(event.target.value)}>
            {mealOptions.map((meal) => (
              <FormControlLabel key={meal.value} value={meal.value} control={<Radio />} label={meal.label} />
            ))}
          </RadioGroup>
        </FormControl>

        <FormControl disabled={isCopyMode && sourceQuery.isLoading}>
          <FormLabel>Последний приём пищи</FormLabel>
          <RadioGroup value={lastMeal} onChange={(event) => setLastMeal(event.target.value)}>
            {mealOptions.map((meal) => (
              <FormControlLabel key={meal.value} value={meal.value} control={<Radio />} label={meal.label} />
            ))}
          </RadioGroup>
        </FormControl>

        <FormControl disabled={isCopyMode && sourceQuery.isLoading}>
          <FormLabel>Какие рецепты использовать при генерации меню</FormLabel>
          <RadioGroup
            value={recipeGenerationMode}
            onChange={(event) => setRecipeGenerationMode(event.target.value as RecipeGenerationMode)}
          >
            {RECIPE_GENERATION_MODE_OPTIONS.map((option) => (
              <FormControlLabel
                key={option.value}
                value={option.value}
                control={<Radio />}
                sx={{ alignItems: "flex-start", my: 0.25 }}
                label={(
                  <Box pt={0.75}>
                    <Typography fontWeight={600}>{option.label}</Typography>
                    <Typography variant="body2" color="text.secondary">
                      {option.description}
                    </Typography>
                  </Box>
                )}
              />
            ))}
          </RadioGroup>
        </FormControl>

        <Button
          type="submit"
          variant="contained"
          disabled={isSaving || sourceIsNotCompleted || (isCopyMode && sourceQuery.isLoading)}
        >
          {isSaving
            ? isCopyMode ? "Копирование…" : "Создание..."
            : isCopyMode ? "Скопировать поход" : "Создать поход"}
        </Button>
      </Box>
    </Paper>
  );
}
