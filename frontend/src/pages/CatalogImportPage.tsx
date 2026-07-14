import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  Divider,
  Paper,
  Stack,
  ToggleButton,
  ToggleButtonGroup,
  Typography,
} from "@mui/material";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { useRef, useState } from "react";

import {
  applyCatalogImport,
  previewCatalogImport,
  type CatalogImportKind,
  type CatalogImportResult,
} from "@/features/catalog-import/api/catalogImportApi";
import {
  catalogImportTemplates,
  getCatalogImportFilename,
  getCatalogImportSummary,
} from "@/features/catalog-import/model/catalogImport";

function downloadTemplate(kind: CatalogImportKind) {
  const blob = new Blob(["\ufeff", catalogImportTemplates[kind]], {
    type: "text/csv;charset=utf-8",
  });
  const url = URL.createObjectURL(blob);
  const anchor = document.createElement("a");
  anchor.href = url;
  anchor.download = getCatalogImportFilename(kind);
  anchor.click();
  URL.revokeObjectURL(url);
}

export default function CatalogImportPage() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [kind, setKind] = useState<CatalogImportKind>("products");
  const [fileName, setFileName] = useState<string | null>(null);
  const [content, setContent] = useState("");
  const [preview, setPreview] = useState<CatalogImportResult | null>(null);
  const [success, setSuccess] = useState<string | null>(null);
  const [readError, setReadError] = useState<string | null>(null);

  const previewMutation = useMutation({
    mutationFn: previewCatalogImport,
    onSuccess: (result) => {
      setPreview(result);
      setSuccess(null);
    },
  });
  const applyMutation = useMutation({
    mutationFn: applyCatalogImport,
    onSuccess: async (result) => {
      setPreview(result);
      if (result.valid) {
        setSuccess(
          result.kind === "products"
            ? `Импорт завершён. Создано продуктов: ${result.create_count}.`
            : `Импорт завершён. Создано рецептов: ${result.create_count}.`,
        );
        await Promise.all([
          queryClient.invalidateQueries({ queryKey: ["recipes"] }),
          queryClient.invalidateQueries({ queryKey: ["recipe-products"] }),
        ]);
      }
    },
  });

  const resetFile = (nextKind: CatalogImportKind = kind) => {
    setKind(nextKind);
    setFileName(null);
    setContent("");
    setPreview(null);
    setSuccess(null);
    setReadError(null);
    previewMutation.reset();
    applyMutation.reset();
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  const selectFile = async (file: File | undefined) => {
    if (!file) return;
    setReadError(null);
    setSuccess(null);
    setPreview(null);
    try {
      const text = await file.text();
      setFileName(file.name);
      setContent(text);
      previewMutation.mutate({ kind, content: text });
    } catch {
      setReadError("Не удалось прочитать выбранный файл.");
    }
  };

  const isBusy = previewMutation.isPending || applyMutation.isPending;

  return (
    <Stack spacing={3} sx={{ mt: 4 }}>
      <Box>
        <Typography variant="h4" component="h1">Импорт каталога</Typography>
        <Typography color="text.secondary">
          Массовое добавление продуктов и рецептов из CSV-файлов, сохранённых в Excel.
        </Typography>
      </Box>

      <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 } }}>
        <Stack spacing={3}>
          <Box>
            <Typography variant="h6" gutterBottom>1. Выберите тип данных</Typography>
            <ToggleButtonGroup
              exclusive
              value={kind}
              onChange={(_, value: CatalogImportKind | null) => {
                if (value) resetFile(value);
              }}
              aria-label="Тип импорта"
            >
              <ToggleButton value="products">Продукты</ToggleButton>
              <ToggleButton value="recipes">Рецепты</ToggleButton>
            </ToggleButtonGroup>
          </Box>

          <Divider />

          <Box>
            <Typography variant="h6" gutterBottom>2. Заполните шаблон</Typography>
            <Typography color="text.secondary" sx={{ mb: 1.5 }}>
              Для рецептов сначала импортируйте продукты. Одна строка файла рецептов соответствует одному компоненту.
            </Typography>
            <Button variant="outlined" onClick={() => downloadTemplate(kind)}>
              Скачать CSV-шаблон
            </Button>
          </Box>

          <Divider />

          <Box>
            <Typography variant="h6" gutterBottom>3. Выберите заполненный CSV</Typography>
            <input
              ref={fileInputRef}
              hidden
              type="file"
              accept=".csv,text/csv"
              onChange={(event) => void selectFile(event.target.files?.[0])}
            />
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5} alignItems={{ xs: "stretch", sm: "center" }}>
              <Button variant="contained" onClick={() => fileInputRef.current?.click()} disabled={isBusy}>
                Выбрать файл
              </Button>
              {fileName && <Chip label={fileName} onDelete={isBusy ? undefined : () => resetFile()} />}
            </Stack>
          </Box>

          {(previewMutation.isPending || applyMutation.isPending) && (
            <Stack direction="row" spacing={1.5} alignItems="center">
              <CircularProgress size={22} />
              <Typography>{applyMutation.isPending ? "Импорт…" : "Проверка файла…"}</Typography>
            </Stack>
          )}

          {(readError || previewMutation.isError || applyMutation.isError) && (
            <Alert severity="error">
              {readError ?? "Не удалось обработать файл. Проверьте соединение с сервером."}
            </Alert>
          )}

          {preview && (
            <Stack spacing={2}>
              <Alert severity={preview.valid ? "success" : "warning"}>
                {getCatalogImportSummary(preview)}
              </Alert>

              {preview.errors.length > 0 && (
                <Paper variant="outlined" sx={{ p: 2 }}>
                  <Typography variant="subtitle1" fontWeight={600} gutterBottom>
                    Ошибки файла
                  </Typography>
                  <Stack spacing={1}>
                    {preview.errors.map((error, index) => (
                      <Typography key={`${error.row}-${error.field}-${index}`} variant="body2">
                        {error.row > 0 ? `Строка ${error.row}` : "Файл"}
                        {error.field ? `, поле ${error.field}` : ""}: {error.message}
                      </Typography>
                    ))}
                  </Stack>
                </Paper>
              )}

              <Button
                variant="contained"
                disabled={!preview.valid || isBusy || !content}
                onClick={() => applyMutation.mutate({ kind, content })}
              >
                Подтвердить импорт
              </Button>
            </Stack>
          )}

          {success && <Alert severity="success">{success}</Alert>}
        </Stack>
      </Paper>
    </Stack>
  );
}
