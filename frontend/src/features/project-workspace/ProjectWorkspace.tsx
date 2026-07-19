import {
  Alert,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  MenuItem,
  Paper,
  Stack,
  Tab,
  Tabs,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";

import {
  RECIPE_GENERATION_MODE_OPTIONS,
  type RecipeGenerationMode,
  useProject,
  useUpdateProjectRecipeGenerationMode,
} from "@/features/project";
import { ProjectWorkflowProvider } from "@/features/project-workflow";
import { useModuleVisibility } from "@/features/system-settings/providers/ModuleVisibilityProvider";

import ProjectOverview from "./components/ProjectOverview";
import WorkflowModules from "./components/WorkflowModules";
import {
  buildProjectWorkspacePath,
  normalizeProjectWorkspaceSection,
  PROJECT_WORKSPACE_SECTIONS,
  type ProjectWorkspaceSection,
} from "./model/projectWorkspaceNavigation";

const mealLabels: Record<string, string> = {
  breakfast: "Завтрак",
  snack: "Перекус",
  lunch: "Обед",
  dinner: "Ужин",
};

function ProjectWorkspaceContent({
  projectId,
  section,
}: {
  projectId: number;
  section: ProjectWorkspaceSection;
}) {
  const { data: project, isLoading, isError } = useProject(projectId);
  const updateGenerationMode = useUpdateProjectRecipeGenerationMode(projectId);
  const { settings } = useModuleVisibility();
  const [settingsOpen, setSettingsOpen] = useState(false);
  const [generationMode, setGenerationMode] = useState<RecipeGenerationMode>(
    "club_only",
  );

  useEffect(() => {
    if (project) setGenerationMode(project.recipe_generation_mode);
  }, [project]);

  const visibleSections = useMemo(
    () =>
      PROJECT_WORKSPACE_SECTIONS.filter((item) => {
        if (item.id === "shopping") return settings.shopping_visible;
        if (item.id === "equipment") return settings.equipment_visible;
        if (item.id === "documents") return settings.documents_visible;
        return true;
      }),
    [settings],
  );

  if (isLoading) {
    return <Typography>Загружаем проект…</Typography>;
  }

  if (isError || !project) {
    return <Alert severity="error">Не удалось загрузить проект.</Alert>;
  }

  return (
    <Stack spacing={2.5}>
      <Box component="header">
        <Typography variant="body2" color="text.secondary" sx={{ mb: 1 }}>
          <Link to="/projects" style={{ color: "inherit" }}>
            Проекты
          </Link>{" "}
          › {project.name}
        </Typography>

        <Stack
          direction={{ xs: "column", md: "row" }}
          spacing={2}
          alignItems={{ xs: "stretch", md: "flex-start" }}
          justifyContent="space-between"
        >
          <Stack spacing={0.75} sx={{ minWidth: 0 }}>
            <Typography variant="h4" component="h1" noWrap>
              {project.name}
            </Typography>
            <Stack
              direction="row"
              spacing={1}
              useFlexGap
              flexWrap="wrap"
              color="text.secondary"
            >
              <Typography variant="body2">{project.participants} участников</Typography>
              <Typography variant="body2">•</Typography>
              <Typography variant="body2">{project.days} дня</Typography>
              {project.start_date && (
                <>
                  <Typography variant="body2">•</Typography>
                  <Typography variant="body2">с {project.start_date}</Typography>
                </>
              )}
              <Typography variant="body2">•</Typography>
              <Typography variant="body2">{project.status}</Typography>
            </Stack>
            {project.first_meal && (
              <Typography variant="caption" color="text.secondary">
                Первый приём пищи: {mealLabels[project.first_meal] ?? project.first_meal}
              </Typography>
            )}
          </Stack>

          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
            <Button variant="outlined" onClick={() => setSettingsOpen(true)}>
              Настройки проекта
            </Button>
            {section !== "overview" && (
              <Button
                component={Link}
                to={buildProjectWorkspacePath(projectId, "overview")}
                variant="contained"
              >
                К обзору
              </Button>
            )}
          </Stack>
        </Stack>
      </Box>

      <Paper
        variant="outlined"
        sx={{
          position: "sticky",
          top: 0,
          zIndex: 2,
          bgcolor: "background.paper",
        }}
      >
        <Tabs
          value={section}
          variant="scrollable"
          scrollButtons="auto"
          allowScrollButtonsMobile
          aria-label="Разделы проекта"
        >
          {visibleSections.map((item) => (
            <Tab
              key={item.id}
              value={item.id}
              component={Link}
              to={buildProjectWorkspacePath(projectId, item.id)}
              label={`${item.icon} ${item.label}`}
            />
          ))}
        </Tabs>
      </Paper>

      {section === "overview" ? (
        <ProjectOverview />
      ) : (
        <WorkflowModules section={section} />
      )}

      <Dialog
        open={settingsOpen}
        onClose={() => setSettingsOpen(false)}
        fullWidth
        maxWidth="sm"
      >
        <DialogTitle>Настройки проекта</DialogTitle>
        <DialogContent>
          <Stack spacing={1.5} sx={{ pt: 1 }}>
            <Typography variant="body2" color="text.secondary">
              Режим определяет порядок выбора вариантов рецепта при следующей генерации меню. Ручные назначения не меняются.
            </Typography>
            {updateGenerationMode.isError && (
              <Alert severity="error">
                Не удалось изменить режим генерации рецептов.
              </Alert>
            )}
            <TextField
              select
              label="Рецепты при генерации меню"
              value={generationMode}
              onChange={(event) =>
                setGenerationMode(event.target.value as RecipeGenerationMode)
              }
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
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setSettingsOpen(false)}>Отмена</Button>
          <Button
            variant="contained"
            disabled={
              updateGenerationMode.isPending ||
              generationMode === project.recipe_generation_mode
            }
            onClick={() =>
              updateGenerationMode.mutate(generationMode, {
                onSuccess: () => setSettingsOpen(false),
              })
            }
          >
            {updateGenerationMode.isPending ? "Сохраняем…" : "Сохранить"}
          </Button>
        </DialogActions>
      </Dialog>
    </Stack>
  );
}

export default function ProjectWorkspace() {
  const { id, section: rawSection } = useParams();
  const navigate = useNavigate();
  const projectId = Number(id ?? 0);
  const section = normalizeProjectWorkspaceSection(rawSection);

  useEffect(() => {
    if (rawSection && rawSection !== section && projectId > 0) {
      navigate(buildProjectWorkspacePath(projectId, "overview"), { replace: true });
    }
  }, [navigate, projectId, rawSection, section]);

  if (!Number.isInteger(projectId) || projectId <= 0) {
    return <Alert severity="error">Некорректный идентификатор проекта.</Alert>;
  }

  return (
    <ProjectWorkflowProvider projectId={projectId}>
      <ProjectWorkspaceContent projectId={projectId} section={section} />
    </ProjectWorkflowProvider>
  );
}
