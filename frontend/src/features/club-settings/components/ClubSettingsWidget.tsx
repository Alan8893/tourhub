import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { ChangeEvent, useEffect, useState } from "react";

import {
  getClubSettings,
  updateClubSettings,
} from "../api/clubSettingsApi";

const MAX_LOGO_BYTES = 1_000_000;
const ALLOWED_TYPES = new Set(["image/png", "image/jpeg"]);

export default function ClubSettingsWidget() {
  const [clubName, setClubName] = useState("");
  const [logoPreview, setLogoPreview] = useState<string | null>(null);
  const [pendingLogo, setPendingLogo] = useState<string | null>(null);
  const [removeLogo, setRemoveLogo] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  useEffect(() => {
    let isActive = true;
    getClubSettings()
      .then((settings) => {
        if (!isActive) return;
        setClubName(settings.club_name);
        setLogoPreview(settings.logo_data_url);
      })
      .catch(() => {
        if (isActive) setError("Не удалось загрузить настройки клуба.");
      })
      .finally(() => {
        if (isActive) setIsLoading(false);
      });
    return () => {
      isActive = false;
    };
  }, []);

  function handleLogoChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setError(null);
    setSuccess(null);
    if (!ALLOWED_TYPES.has(file.type)) {
      setError("Логотип должен быть в формате PNG или JPEG.");
      event.target.value = "";
      return;
    }
    if (file.size > MAX_LOGO_BYTES) {
      setError("Размер логотипа не должен превышать 1 МБ.");
      event.target.value = "";
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result !== "string") return;
      setLogoPreview(reader.result);
      setPendingLogo(reader.result);
      setRemoveLogo(false);
    };
    reader.onerror = () => setError("Не удалось прочитать файл логотипа.");
    reader.readAsDataURL(file);
  }

  function handleRemoveLogo() {
    setLogoPreview(null);
    setPendingLogo(null);
    setRemoveLogo(true);
    setError(null);
    setSuccess(null);
  }

  async function handleSave() {
    const normalizedName = clubName.trim();
    if (!normalizedName) {
      setError("Укажите название клуба.");
      return;
    }

    setIsSaving(true);
    setError(null);
    setSuccess(null);
    try {
      const settings = await updateClubSettings({
        club_name: normalizedName,
        logo_data_url: pendingLogo,
        remove_logo: removeLogo,
      });
      setClubName(settings.club_name);
      setLogoPreview(settings.logo_data_url);
      setPendingLogo(null);
      setRemoveLogo(false);
      setSuccess("Настройки клуба сохранены.");
    } catch {
      setError("Не удалось сохранить настройки клуба.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <Card sx={{ "& .MuiButton-root": { textTransform: "none" } }}>
      <CardContent>
        <Stack spacing={2}>
          <Typography variant="h6">Настройки клуба</Typography>
          <Typography>
            Название и логотип используются в русских PDF, Excel и полном пакете документов.
          </Typography>

          {error && <Alert severity="error">{error}</Alert>}
          {success && <Alert severity="success">{success}</Alert>}

          <TextField
            label="Название клуба"
            value={clubName}
            disabled={isLoading || isSaving}
            inputProps={{ maxLength: 255 }}
            onChange={(event) => setClubName(event.target.value)}
          />

          {logoPreview && (
            <Box
              component="img"
              src={logoPreview}
              alt="Логотип клуба"
              sx={{
                maxWidth: 220,
                maxHeight: 120,
                objectFit: "contain",
                alignSelf: "flex-start",
              }}
            />
          )}

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
            <Button component="label" variant="outlined" disabled={isLoading || isSaving}>
              Выбрать логотип
              <input
                hidden
                type="file"
                accept="image/png,image/jpeg"
                onChange={handleLogoChange}
              />
            </Button>
            {logoPreview && (
              <Button disabled={isSaving} onClick={handleRemoveLogo}>
                Удалить логотип
              </Button>
            )}
          </Stack>

          <Typography variant="caption">
            PNG или JPEG, не более 1 МБ.
          </Typography>

          <Button
            variant="contained"
            disabled={isLoading || isSaving}
            onClick={handleSave}
          >
            {isSaving ? "Сохранение…" : "Сохранить настройки"}
          </Button>
        </Stack>
      </CardContent>
    </Card>
  );
}
