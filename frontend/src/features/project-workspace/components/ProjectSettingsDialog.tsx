import {
  Alert,
  Autocomplete,
  Box,
  Button,
  Dialog,
  DialogActions,
  DialogContent,
  DialogTitle,
  Divider,
  MenuItem,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { useEffect, useMemo, useState } from "react";

import { userRoleLabel } from "@/features/auth/model/roleLabels";
import {
  RECIPE_GENERATION_MODE_OPTIONS,
  type RecipeGenerationMode,
  useCompleteProject,
  useDeleteProject,
  useProjectTeam,
  useProjectTeamCandidates,
  useTransferProjectOwnership,
  useUpdateProjectRecipeGenerationMode,
  useUpdateProjectTeam,
} from "@/features/project";
import type {
  Project,
  ProjectTeamCandidate,
} from "@/features/project/api/projectApi";

interface Props {
  open: boolean;
  project: Project;
  onClose: () => void;
  onDeleted: () => void;
}

export default function ProjectSettingsDialog({ open, project, onClose, onDeleted }: Props) {
  const canManage = Boolean(project.capabilities?.can_manage_project);
  const canManageTeam = Boolean(project.capabilities?.can_manage_team);
  const canTransfer = Boolean(project.capabilities?.can_transfer_ownership);
  const canDelete = Boolean(project.capabilities?.can_delete);
  const teamQuery = useProjectTeam(project.id);
  const candidatesQuery = useProjectTeamCandidates(project.id, open && canManageTeam);
  const updateMode = useUpdateProjectRecipeGenerationMode(project.id);
  const updateTeam = useUpdateProjectTeam(project.id);
  const transferOwner = useTransferProjectOwnership(project.id);
  const completeMutation = useCompleteProject(project.id);
  const deleteMutation = useDeleteProject(project.id);
  const [generationMode, setGenerationMode] = useState<RecipeGenerationMode>(
    project.recipe_generation_mode,
  );
  const [selectedIds, setSelectedIds] = useState<number[]>([]);
  const [newOwnerId, setNewOwnerId] = useState<number | "">("");
  const [confirmAction, setConfirmAction] = useState<"complete" | "delete" | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setGenerationMode(project.recipe_generation_mode);
  }, [project.recipe_generation_mode]);

  useEffect(() => {
    if (teamQuery.data) {
      setSelectedIds(teamQuery.data.instructors.map((member) => member.id));
    }
  }, [teamQuery.data]);

  const options = useMemo<ProjectTeamCandidate[]>(() => {
    const result = [...(candidatesQuery.data ?? [])];
    const known = new Set(result.map((item) => item.id));
    for (const member of teamQuery.data?.instructors ?? []) {
      if (!known.has(member.id)) {
        result.push({
          id: member.id,
          email: member.email,
          display_name: member.display_name,
          role: member.role,
          is_active: member.is_active,
        });
      }
    }
    return result.sort((left, right) =>
      left.display_name.localeCompare(right.display_name, "ru"),
    );
  }, [candidatesQuery.data, teamQuery.data]);

  const selectedOptions = options.filter((option) => selectedIds.includes(option.id));
  const isSaving = updateMode.isPending || updateTeam.isPending;

  async function save() {
    setError(null);
    try {
      if (generationMode !== project.recipe_generation_mode) {
        await updateMode.mutateAsync(generationMode);
      }
      const currentIds = teamQuery.data?.instructors.map((item) => item.id).sort() ?? [];
      const nextIds = [...selectedIds].sort();
      if (JSON.stringify(currentIds) !== JSON.stringify(nextIds)) {
        await updateTeam.mutateAsync(nextIds);
      }
      onClose();
    } catch {
      setError("Не удалось сохранить настройки проекта.");
    }
  }

  async function transfer() {
    if (newOwnerId === "") return;
    setError(null);
    try {
      await transferOwner.mutateAsync(newOwnerId);
      setNewOwnerId("");
    } catch {
      setError("Не удалось передать владение проектом.");
    }
  }

  async function confirm() {
    if (confirmAction === "complete") {
      try {
        await completeMutation.mutateAsync();
        setConfirmAction(null);
        onClose();
      } catch {
        setError("Не удалось завершить проект.");
      }
      return;
    }
    if (confirmAction === "delete") {
      try {
        await deleteMutation.mutateAsync();
        setConfirmAction(null);
        onDeleted();
      } catch {
        setError("Не удалось удалить проект.");
      }
    }
  }

  return (
    <>
      <Dialog open={open} onClose={onClose} fullWidth maxWidth="md">
        <DialogTitle>Настройки проекта</DialogTitle>
        <DialogContent>
          <Stack spacing={2.5} sx={{ pt: 1 }}>
            {project.status === "completed" && (
              <Alert severity="info">
                Завершённый проект доступен только для чтения. Копирование проекта будет
                реализовано отдельной задачей.
              </Alert>
            )}
            {error && <Alert severity="error">{error}</Alert>}

            {canManageTeam && (
              <>
                <Box>
                  <Typography variant="h6">Доступ и команда</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Владелец и администраторы управляют командой. Приглашённые инструкторы
                    работают с закупками, снаряжением и документами, а меню видят без права
                    изменения.
                  </Typography>
                </Box>
                <TextField
                  label="Владелец проекта"
                  value={teamQuery.data?.owner.display_name ?? "Загрузка…"}
                  InputProps={{ readOnly: true }}
                />
                <Autocomplete
                  multiple
                  options={options}
                  value={selectedOptions}
                  loading={candidatesQuery.isLoading || teamQuery.isLoading}
                  getOptionLabel={(option) => `${option.display_name} · ${option.email}`}
                  isOptionEqualToValue={(option, value) => option.id === value.id}
                  getOptionDisabled={(option) => !option.is_active && !selectedIds.includes(option.id)}
                  groupBy={(option) =>
                    option.role === "administrator" ? "Администраторы" : "Инструкторы"
                  }
                  onChange={(_, values) => setSelectedIds(values.map((value) => value.id))}
                  renderInput={(params) => (
                    <TextField
                      {...params}
                      label="Дополнительные инструкторы"
                      helperText="Можно выбрать нескольких активных пользователей. Неактивного участника можно только удалить из команды."
                    />
                  )}
                  renderOption={(props, option) => (
                    <li {...props} key={option.id}>
                      <Stack spacing={0.25}>
                        <Typography>{option.display_name}</Typography>
                        <Typography variant="caption" color="text.secondary">
                          {userRoleLabel(option.role)} · {option.email}
                          {!option.is_active ? " · Неактивен" : ""}
                        </Typography>
                      </Stack>
                    </li>
                  )}
                />

                {canTransfer && (
                  <Stack spacing={1.5}>
                    <Divider />
                    <Typography variant="h6">Передача владения</Typography>
                    <Typography variant="body2" color="text.secondary">
                      Прежний владелец останется дополнительным инструктором проекта.
                    </Typography>
                    <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
                      <TextField
                        select
                        fullWidth
                        label="Новый владелец"
                        value={newOwnerId}
                        onChange={(event) => setNewOwnerId(Number(event.target.value))}
                      >
                        {options.filter((option) => option.is_active).map((option) => (
                          <MenuItem key={option.id} value={option.id}>
                            {option.display_name} · {userRoleLabel(option.role)}
                          </MenuItem>
                        ))}
                      </TextField>
                      <Button
                        variant="outlined"
                        disabled={newOwnerId === "" || transferOwner.isPending}
                        onClick={() => void transfer()}
                      >
                        {transferOwner.isPending ? "Передача…" : "Передать"}
                      </Button>
                    </Stack>
                  </Stack>
                )}
              </>
            )}

            {canManage && (
              <>
                <Divider />
                <Box>
                  <Typography variant="h6">Рецепты и меню</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Режим определяет порядок выбора рецептов при следующей генерации меню.
                    Ручные назначения не меняются.
                  </Typography>
                </Box>
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
                <Divider />
                <Box>
                  <Typography variant="h6">Состояние проекта</Typography>
                  <Typography variant="body2" color="text.secondary">
                    После завершения проект останется доступен только для чтения и будет
                    скрыт из списка по умолчанию.
                  </Typography>
                </Box>
                <Button
                  color="warning"
                  variant="outlined"
                  onClick={() => setConfirmAction("complete")}
                  sx={{ alignSelf: "flex-start" }}
                >
                  Завершить проект
                </Button>
              </>
            )}

            {canDelete && (
              <>
                <Divider />
                <Box>
                  <Typography variant="h6">Удаление проекта</Typography>
                  <Typography variant="body2" color="text.secondary">
                    Удаление необратимо и удалит связанные результаты подготовки.
                  </Typography>
                </Box>
                <Button
                  color="error"
                  variant="outlined"
                  onClick={() => setConfirmAction("delete")}
                  sx={{ alignSelf: "flex-start" }}
                >
                  Удалить проект
                </Button>
              </>
            )}
          </Stack>
        </DialogContent>
        <DialogActions>
          <Button onClick={onClose}>Отмена</Button>
          {canManage && (
            <Button variant="contained" disabled={isSaving} onClick={() => void save()}>
              {isSaving ? "Сохраняем…" : "Сохранить"}
            </Button>
          )}
        </DialogActions>
      </Dialog>

      <Dialog open={confirmAction !== null} onClose={() => setConfirmAction(null)}>
        <DialogTitle>
          {confirmAction === "complete" ? "Завершить проект?" : "Удалить проект?"}
        </DialogTitle>
        <DialogContent>
          <Typography>
            {confirmAction === "complete"
              ? "Проект станет доступен только для чтения и не сможет быть возобновлён."
              : "Проект и связанные данные будут удалены без возможности восстановления."}
          </Typography>
        </DialogContent>
        <DialogActions>
          <Button onClick={() => setConfirmAction(null)}>Отмена</Button>
          <Button
            color={confirmAction === "delete" ? "error" : "warning"}
            variant="contained"
            disabled={completeMutation.isPending || deleteMutation.isPending}
            onClick={() => void confirm()}
          >
            Подтвердить
          </Button>
        </DialogActions>
      </Dialog>
    </>
  );
}
