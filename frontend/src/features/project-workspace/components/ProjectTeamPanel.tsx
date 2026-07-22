import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Paper,
  Stack,
  Typography,
} from "@mui/material";
import { useState } from "react";

import {
  downloadProjectTeamVcard,
  type ProjectTeamMember,
} from "@/features/project/api/projectApi";
import { useProjectTeam } from "@/features/project";
import { userRoleLabel } from "@/features/auth/model/roleLabels";

function projectRoleLabel(member: ProjectTeamMember): string {
  return member.project_role === "owner"
    ? "Владелец проекта"
    : "Дополнительный инструктор";
}

function ContactCard({ projectId, member }: { projectId: number; member: ProjectTeamMember }) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function saveContact() {
    setError(null);
    setIsDownloading(true);
    try {
      const blob = await downloadProjectTeamVcard(projectId, member.id);
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `tourhub-project-${projectId}-contact-${member.id}.vcf`;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      URL.revokeObjectURL(url);
    } catch {
      setError("Не удалось подготовить контакт.");
    } finally {
      setIsDownloading(false);
    }
  }

  return (
    <Paper variant="outlined" sx={{ p: 2, minWidth: 0 }}>
      <Stack spacing={1.25} alignItems="flex-start">
        <Box sx={{ minWidth: 0, width: "100%" }}>
          <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap" alignItems="center">
            <Typography variant="h6" sx={{ overflowWrap: "anywhere" }}>
              {member.display_name}
            </Typography>
            {!member.is_active && <Chip size="small" color="default" label="Неактивен" />}
          </Stack>
          <Typography variant="body2" color="text.secondary">
            {projectRoleLabel(member)} · {userRoleLabel(member.role)}
          </Typography>
        </Box>

        {member.is_active ? (
          <>
            <Button
              component="a"
              href={`mailto:${member.email}`}
              variant="text"
              sx={{ p: 0, textTransform: "none", overflowWrap: "anywhere" }}
            >
              {member.email}
            </Button>
            {member.phone && (
              <Button component="a" href={`tel:${member.phone}`} variant="outlined">
                Позвонить: {member.phone}
              </Button>
            )}
            <Stack direction="row" spacing={1} useFlexGap flexWrap="wrap">
              {member.telegram_url && (
                <Button component="a" href={member.telegram_url} target="_blank" rel="noreferrer">
                  Telegram
                </Button>
              )}
              {member.max_url && (
                <Button component="a" href={member.max_url} target="_blank" rel="noreferrer">
                  MAX
                </Button>
              )}
              {member.vk_url && (
                <Button component="a" href={member.vk_url} target="_blank" rel="noreferrer">
                  VK
                </Button>
              )}
            </Stack>
            <Button variant="outlined" disabled={isDownloading} onClick={() => void saveContact()}>
              {isDownloading ? "Подготовка…" : "Сохранить контакт"}
            </Button>
          </>
        ) : (
          <Typography variant="body2" color="text.secondary">
            Пользователь неактивен, контактные действия временно недоступны.
          </Typography>
        )}
        {error && <Alert severity="error">{error}</Alert>}
      </Stack>
    </Paper>
  );
}

export default function ProjectTeamPanel({ projectId }: { projectId: number }) {
  const teamQuery = useProjectTeam(projectId);

  if (teamQuery.isLoading) {
    return (
      <Paper variant="outlined" sx={{ p: 3, display: "grid", placeItems: "center" }}>
        <CircularProgress size={28} aria-label="Загрузка команды проекта" />
      </Paper>
    );
  }

  if (teamQuery.isError || !teamQuery.data) {
    return <Alert severity="error">Не удалось загрузить команду проекта.</Alert>;
  }

  const members = [teamQuery.data.owner, ...teamQuery.data.instructors];
  return (
    <Stack spacing={1.5}>
      <Box>
        <Typography variant="h5">Команда проекта</Typography>
        <Typography variant="body2" color="text.secondary">
          Контакты владельца и приглашённых инструкторов доступны только участникам проекта.
        </Typography>
      </Box>
      <Box
        sx={{
          display: "grid",
          gridTemplateColumns: { xs: "minmax(0, 1fr)", lg: "repeat(2, minmax(0, 1fr))" },
          gap: 2,
        }}
      >
        {members.map((member) => (
          <ContactCard key={`${member.project_role}-${member.id}`} projectId={projectId} member={member} />
        ))}
      </Box>
    </Stack>
  );
}
