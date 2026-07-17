import {
  Alert,
  Box,
  Button,
  Card,
  CardContent,
  Stack,
  Typography,
} from "@mui/material";
import { ChangeEvent, useState } from "react";

const ALLOWED_IMAGE_TYPES = new Set(["image/png", "image/jpeg", "image/webp"]);

interface ImageSettingFieldProps {
  label: string;
  description: string;
  preview: string | null;
  maxBytes: number;
  disabled: boolean;
  onUpload: (dataUrl: string) => void;
  onRemove: () => void;
}

export default function ImageSettingField({
  label,
  description,
  preview,
  maxBytes,
  disabled,
  onUpload,
  onRemove,
}: ImageSettingFieldProps) {
  const [error, setError] = useState<string | null>(null);

  function handleFileChange(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    setError(null);
    if (!ALLOWED_IMAGE_TYPES.has(file.type)) {
      setError("Поддерживаются только PNG, JPEG и WebP. SVG не разрешён.");
      event.target.value = "";
      return;
    }
    if (file.size > maxBytes) {
      setError(`Размер файла не должен превышать ${Math.ceil(maxBytes / 1_000_000)} МБ.`);
      event.target.value = "";
      return;
    }

    const reader = new FileReader();
    reader.onload = () => {
      if (typeof reader.result === "string") onUpload(reader.result);
    };
    reader.onerror = () => setError("Не удалось прочитать изображение.");
    reader.readAsDataURL(file);
  }

  return (
    <Card variant="outlined">
      <CardContent>
        <Stack spacing={1.5}>
          <Box>
            <Typography variant="subtitle1">{label}</Typography>
            <Typography variant="body2" color="text.secondary">
              {description}
            </Typography>
          </Box>

          {error && <Alert severity="error">{error}</Alert>}

          {preview ? (
            <Box
              component="img"
              src={preview}
              alt={label}
              sx={{
                width: "100%",
                maxWidth: 280,
                height: 132,
                objectFit: "contain",
                alignSelf: "flex-start",
                border: 1,
                borderColor: "divider",
                borderRadius: 1,
                p: 1,
              }}
            />
          ) : (
            <Box
              sx={{
                width: "100%",
                maxWidth: 280,
                height: 92,
                display: "grid",
                placeItems: "center",
                border: 1,
                borderStyle: "dashed",
                borderColor: "divider",
                borderRadius: 1,
              }}
            >
              <Typography variant="body2" color="text.secondary">
                Изображение не загружено
              </Typography>
            </Box>
          )}

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
            <Button component="label" variant="outlined" disabled={disabled}>
              Выбрать файл
              <input
                hidden
                type="file"
                accept="image/png,image/jpeg,image/webp"
                onChange={handleFileChange}
              />
            </Button>
            {preview && (
              <Button disabled={disabled} onClick={onRemove}>
                Удалить
              </Button>
            )}
          </Stack>

          <Typography variant="caption" color="text.secondary">
            PNG, JPEG или WebP. Максимум {Math.ceil(maxBytes / 1_000_000)} МБ.
          </Typography>
        </Stack>
      </CardContent>
    </Card>
  );
}
