import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
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

import { useCreateProject } from "../features/project/hooks/useCreateProject";
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

export default function CreateProjectPage() {
  const navigate = useNavigate();
  const createProject = useCreateProject();

  const [name, setName] = useState("");
  const [participants, setParticipants] = useState(1);
  const [days, setDays] = useState(1);
  const [startDate, setStartDate] = useState("");
  const [firstMeal, setFirstMeal] = useState("dinner");
  const [lastMeal, setLastMeal] = useState("dinner");
  const [recipeGenerationMode, setRecipeGenerationMode] =
    useState<RecipeGenerationMode>("club_only");
  const [validationError, setValidationError] = useState<string | null>(null);

  async function submit(event: FormEvent) {
    event.preventDefault();

    const firstIndex = mealOptions.findIndex((meal) => meal.value === firstMeal);
    const lastIndex = mealOptions.findIndex((meal) => meal.value === lastMeal);
    if (days === 1 && firstIndex > lastIndex) {
      setValidationError("В однодневном походе последний приём пищи не может быть раньше первого.");
      return;
    }

    setValidationError(null);
    const project = await createProject.mutateAsync({
      name,
      participants,
      days,
      start_date: startDate || undefined,
      first_meal: firstMeal,
      last_meal: lastMeal,
      recipe_generation_mode: recipeGenerationMode,
    });

    navigate(`/projects/${project.id}`);
  }

  return (
    <Paper sx={{ maxWidth: 640, mx: "auto", mt: 5, p: { xs: 2.5, sm: 4 } }}>
      <Typography variant="h4" sx={{ mb: 1 }}>
        Создание похода
      </Typography>

      <Typography variant="body2" sx={{ mb: 3 }}>
        Укажите параметры похода. Они будут использоваться при подготовке меню и документов.
      </Typography>

      <Box component="form" onSubmit={submit} sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
        {validationError && <Alert severity="error">{validationError}</Alert>}
        {createProject.isError && (
          <Alert severity="error">Не удалось создать поход. Проверьте параметры и повторите попытку.</Alert>
        )}

        <TextField
          label="Название похода"
          placeholder="Например: Карелия 2026"
          value={name}
          onChange={(event) => setName(event.target.value)}
          required
        />

        <TextField
          label="Количество участников"
          type="number"
          value={participants}
          onChange={(event) => setParticipants(Number(event.target.value))}
          inputProps={{ min: 1 }}
          required
        />

        <TextField
          label="Количество дней"
          type="number"
          value={days}
          onChange={(event) => setDays(Number(event.target.value))}
          inputProps={{ min: 1 }}
          required
        />

        <TextField
          label="Дата начала похода"
          type="date"
          value={startDate}
          onChange={(event) => setStartDate(event.target.value)}
          InputLabelProps={{ shrink: true }}
        />

        <FormControl>
          <FormLabel>Первый приём пищи</FormLabel>
          <RadioGroup value={firstMeal} onChange={(event) => setFirstMeal(event.target.value)}>
            {mealOptions.map((meal) => (
              <FormControlLabel key={meal.value} value={meal.value} control={<Radio />} label={meal.label} />
            ))}
          </RadioGroup>
        </FormControl>

        <FormControl>
          <FormLabel>Последний приём пищи</FormLabel>
          <RadioGroup value={lastMeal} onChange={(event) => setLastMeal(event.target.value)}>
            {mealOptions.map((meal) => (
              <FormControlLabel key={meal.value} value={meal.value} control={<Radio />} label={meal.label} />
            ))}
          </RadioGroup>
        </FormControl>

        <FormControl>
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

        <Button type="submit" variant="contained" disabled={createProject.isPending}>
          {createProject.isPending ? "Создание..." : "Создать поход"}
        </Button>
      </Box>
    </Paper>
  );
}
