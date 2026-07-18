import {
  Alert,
  MenuItem,
  Paper,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useParams } from "react-router-dom";

import {
  ProjectHeader,
  RECIPE_GENERATION_MODE_OPTIONS,
  type RecipeGenerationMode,
  useProject,
  useUpdateProjectRecipeGenerationMode,
} from "@/features/project";
import {
  ProjectWorkflowProvider,
} from "@/features/project-workflow";

import NextWorkflowAction from "./components/NextWorkflowAction";
import ProjectWorkflowPanel from "./components/ProjectWorkflowPanel";
import WorkflowModules from "./components/WorkflowModules";

function ProjectWorkspaceContent({ projectId }: { projectId: number }) {
  const { data: project, isLoading } = useProject(projectId);
  const updateGenerationMode = useUpdateProjectRecipeGenerationMode(projectId);

  if (isLoading || !project) {
    return <Typography>Загружаем проект…</Typography>;
  }

  return (
    <>
      <ProjectHeader project={project} />

      <Typography variant="body1" sx={{ mt: 1 }}>
        Единое рабочее пространство для подготовки похода.
      </Typography>

      <Paper variant="outlined" sx={{ p: { xs: 2, sm: 2.5 }, mt: 2 }}>
        <Stack spacing={1.5}>
          <Typography variant="h6">Рецепты при генерации меню</Typography>
          <Typography variant="body2" color="text.secondary">
            Режим определяет порядок выбора вариантов рецепта для каждого блюда. Уже сохранённые ручные назначения не меняются.
          </Typography>
          {updateGenerationMode.isError && (
            <Alert severity="error">Не удалось изменить режим генерации рецептов.</Alert>
          )}
          <TextField
            select
            label="Режим генерации"
            value={project.recipe_generation_mode}
            disabled={updateGenerationMode.isPending}
            onChange={(event) => {
              updateGenerationMode.mutate(event.target.value as RecipeGenerationMode);
            }}
            sx={{ maxWidth: 520 }}
          >
            {RECIPE_GENERATION_MODE_OPTIONS.map((option) => (
              <MenuItem key={option.value} value={option.value}>
                <Stack spacing={0.25} sx={{ py: 0.5, whiteSpace: "normal" }}>
                  <Typography fontWeight={600}>{option.label}</Typography>
                  <Typography variant="caption" color="text.secondary">
                    {option.description}
                  </Typography>
                </Stack>
              </MenuItem>
            ))}
          </TextField>
        </Stack>
      </Paper>

      <NextWorkflowAction />
      <ProjectWorkflowPanel />
      <WorkflowModules />
    </>
  );
}

export default function ProjectWorkspace() {
  const { id } = useParams();
  const projectId = Number(id ?? 1);

  return (
    <ProjectWorkflowProvider projectId={projectId}>
      <ProjectWorkspaceContent projectId={projectId} />
    </ProjectWorkflowProvider>
  );
}
