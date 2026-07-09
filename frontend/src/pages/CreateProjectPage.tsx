import { FormEvent, useState } from "react";
import { useNavigate } from "react-router-dom";
import { Box, Button, FormControl, FormControlLabel, FormLabel, Paper, Radio, RadioGroup, TextField, Typography } from "@mui/material";

import { useCreateProject } from "../features/project/hooks/useCreateProject";

export default function CreateProjectPage() {
  const navigate = useNavigate();
  const createProject = useCreateProject();

  const [name, setName] = useState("");
  const [participants, setParticipants] = useState(1);
  const [days, setDays] = useState(1);
  const [startDate, setStartDate] = useState("");
  const [firstMeal, setFirstMeal] = useState("dinner");

  async function submit(event: FormEvent) {
    event.preventDefault();

    const project = await createProject.mutateAsync({
      name,
      participants,
      days,
      start_date: startDate || undefined,
      first_meal: firstMeal,
    });

    navigate(`/projects/${project.id}`);
  }

  return (
    <Paper sx={{ maxWidth: 560, mx: "auto", mt: 5, p: 4 }}>
      <Typography variant="h4" sx={{ mb: 1 }}>
        Создание похода
      </Typography>

      <Typography variant="body2" sx={{ mb: 3 }}>
        Укажите параметры похода. Они будут использоваться при подготовке меню и документов.
      </Typography>

      <Box component="form" onSubmit={submit} sx={{ display: "flex", flexDirection: "column", gap: 2 }}>
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
          <RadioGroup
            value={firstMeal}
            onChange={(event) => setFirstMeal(event.target.value)}
          >
            <FormControlLabel value="breakfast" control={<Radio />} label="Завтрак" />
            <FormControlLabel value="lunch" control={<Radio />} label="Обед" />
            <FormControlLabel value="dinner" control={<Radio />} label="Ужин" />
          </RadioGroup>
        </FormControl>

        <Button
          type="submit"
          variant="contained"
          disabled={createProject.isPending}
        >
          {createProject.isPending ? "Создание..." : "Создать поход"}
        </Button>
      </Box>
    </Paper>
  );
}
