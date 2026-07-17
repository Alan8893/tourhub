import { Alert, CircularProgress, Stack } from "@mui/material";
import { useEffect, useState } from "react";

import {
  InvitationSettings,
  getInvitationSettings,
} from "../api/invitationSettingsApi";
import InvitationLifecyclePanel from "./InvitationLifecyclePanel";
import InvitationSettingsForm from "./InvitationSettingsForm";

export default function InvitationSettingsWorkspace() {
  const [settings, setSettings] = useState<InvitationSettings | null>(null);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    void getInvitationSettings()
      .then(setSettings)
      .catch(() => setFailed(true));
  }, []);

  return (
    <Stack spacing={3}>
      <InvitationSettingsForm onSaved={setSettings} />
      {failed && (
        <Alert severity="warning">
          Рабочие приглашения доступны, но начальные значения роли не удалось загрузить.
        </Alert>
      )}
      {!settings && !failed ? (
        <CircularProgress aria-label="Загрузка правил приглашений" />
      ) : (
        <InvitationLifecyclePanel
          defaultRole={settings?.default_role ?? "instructor"}
          allowReissue={settings?.allow_resend ?? true}
        />
      )}
    </Stack>
  );
}
