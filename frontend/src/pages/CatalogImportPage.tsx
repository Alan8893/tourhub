import {
  Alert,
  Box,
  Button,
  Chip,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Paper,
  Select,
  Stack,
  TextField,
  Typography,
} from "@mui/material";
import { isAxiosError } from "axios";
import { ChangeEvent, useState } from "react";

import {
  applyCatalogImport,
  previewCatalogImport,
  type CatalogImportKind,
  type CatalogImportResult,
  type RecipeImportOwnership,
} from "@/features/catalog-import/api/catalogImportApi";
import {
  buildCatalogImportApplyRequest,
  buildCatalogImportPreviewRequest,
  recipeImportOwnershipDescription,
  recipeImportOwnershipLabel,
} from "@/features/catalog-import/model/catalogImportOwnership";
import {
  getCatalogImportFilename,
  getCatalogImportTemplate,
} from "@/features/catalog-import/model/catalogImportTemplates";

function getErrorMessage(error: unknown): string {
  if (isAxiosError<{ error?: string }>(error)) {
    return error.response?.data?.error ?? "Не удалось обработать файл.";
  }
  return "Не удалось обработать файл.";
}

export default function CatalogImportPage() {
  const [kind, setKind] = useState<CatalogImportKind>("products");
  const [ownershipScope, setOwnershipScope] =
    useState<RecipeImportOwnership>("club");
  const [content, setContent] = useState("");
  const [result, setResult] = useState<CatalogImportResult | null>(null);
  const [isPreviewing, setIsPreviewing] = useState(false);
  const [isApplying, setIsApplying] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [success, setSuccess] = useState<string | null>(null);

  const resetResult = () => {
    setResult(null);
    setError(null);
    setSuccess(null);
  };

  const selectKind = (nextKind: CatalogImportKind) => {
    setKind(nextKind);
    setContent("");
    resetResult();
  };

  const selectOwnership = (nextScope: RecipeImportOwnership) => {
    setOwnershipScope(nextScope);
    resetResult();
  };

  const readFile = async (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;
    setContent(await file.text());
    resetResult();
    event.target.value = "";
  };

  const downloadTemplate = () => {
    const blob = new Blob(["\ufeff", getCatalogImportTemplate(kind)], {
      type: "text/csv;charset=utf-8",
    });
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");
    link.href = url;
    link.download = getCatalogImportFilename(kind);
    link.click();
    URL.revokeObjectURL(url);
  };

  const preview = async () => {
    setError(null);
    setSuccess(null);
    setIsPreviewing(true);
    try {
      setResult(
        await previewCatalogImport(
          buildCatalogImportPreviewRequest(kind, content, ownershipScope),
        ),
      );
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsPreviewing(false);
    }
  };

  const apply = async () => {
    if (!result) return;
    setError(null);
    setSuccess(null);
    setIsApplying(true);
    try {
      const applied = await applyCatalogImport(
        buildCatalogImportApplyRequest(
          kind,
          content,
          ownershipScope,
          result,
        ),
      );
      setResult(applied);
      if (applied.valid) {
        setSuccess(
          kind === "products"
            ? `Импорт завершён: создано ${applied.create_count}, пропущено ${applied.skip_count}.`
            : ownershipScope === "personal"
              ? `Импорт завершён: создано личных черновиков ${applied.create_count}, компонентов ${applied.component_count}, заметок ${applied.note_count}.`
              : `Импорт завершён: создано клубных рецептов ${applied.create_count}, компонентов ${applied.component_count}, заметок ${applied.note_count}.`,
        );
      }
    } catch (requestError) {
      setError(getErrorMessage(requestError));
    } finally {
      setIsApplying(false);
    }
  };

  const canApply = Boolean(
    result?.valid &&
      (kind === "products" ||
        (result.preview_token && result.ownership_scope === ownershipScope)),
  );

  return (
    <Stack spacing={3} sx={{ mt: 4 }}>
      <Box>
        <Typography variant="h4" component="h1">
          Массовый импорт
        </Typography>
        <Typography color="text.secondary">
          Загрузите CSV, сначала проверьте данные, затем примените импорт одной
          транзакцией.
        </Typography>
      </Box>

      <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 } }}>
        <Stack spacing={2.5}>
          <FormControl fullWidth>
            <InputLabel id="catalog-import-kind-label">Тип данных</InputLabel>
            <Select
              labelId="catalog-import-kind-label"
              label="Тип данных"
              value={kind}
              onChange={(event) =>
                selectKind(event.target.value as CatalogImportKind)
              }
            >
              <MenuItem value="products">Продукты</MenuItem>
              <MenuItem value="recipes">
                Рецепты, компоненты и заметки
              </MenuItem>
            </Select>
          </FormControl>

          {kind === "recipes" && (
            <Stack spacing={1.5}>
              <FormControl fullWidth>
                <InputLabel id="catalog-import-ownership-label">
                  Область владения
                </InputLabel>
                <Select
                  labelId="catalog-import-ownership-label"
                  label="Область владения"
                  value={ownershipScope}
                  onChange={(event) =>
                    selectOwnership(
                      event.target.value as RecipeImportOwnership,
                    )
                  }
                >
                  <MenuItem value="club">Клубные рецепты</MenuItem>
                  <MenuItem value="personal">Личные рецепты</MenuItem>
                </Select>
              </FormControl>
              <Alert severity={ownershipScope === "personal" ? "info" : "success"}>
                {recipeImportOwnershipDescription(ownershipScope)}
              </Alert>
            </Stack>
          )}

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
            <Button component="label" variant="contained">
              Выбрать CSV
              <input
                hidden
                type="file"
                accept=".csv,text/csv"
                onChange={(event) => void readFile(event)}
              />
            </Button>
            <Button variant="outlined" onClick={downloadTemplate}>
              Скачать шаблон
            </Button>
          </Stack>

          <TextField
            label="Содержимое CSV"
            value={content}
            onChange={(event) => {
              setContent(event.target.value);
              resetResult();
            }}
            multiline
            minRows={10}
            fullWidth
            placeholder="Можно загрузить файл или вставить CSV из Excel."
          />

          <Stack direction={{ xs: "column", sm: "row" }} spacing={1.5}>
            <Button
              variant="outlined"
              disabled={!content.trim() || isPreviewing || isApplying}
              onClick={() => void preview()}
            >
              {isPreviewing ? "Проверка…" : "Проверить файл"}
            </Button>
            <Button
              variant="contained"
              disabled={!canApply || isPreviewing || isApplying}
              onClick={() => void apply()}
            >
              {isApplying ? "Импорт…" : "Импортировать"}
            </Button>
            {(isPreviewing || isApplying) && <CircularProgress size={24} />}
          </Stack>
        </Stack>
      </Paper>

      {error && <Alert severity="error">{error}</Alert>}
      {success && <Alert severity="success">{success}</Alert>}

      {result && (
        <Paper variant="outlined" sx={{ p: { xs: 2, sm: 3 } }}>
          <Stack spacing={2}>
            <Stack direction="row" spacing={1} flexWrap="wrap" useFlexGap>
              <Chip label={`Строк: ${result.row_count}`} />
              <Chip
                color="success"
                variant="outlined"
                label={`Будет создано: ${result.create_count}`}
              />
              <Chip
                variant="outlined"
                label={`Будет пропущено: ${result.skip_count}`}
              />
              {kind === "recipes" && (
                <Chip
                  color="primary"
                  variant="outlined"
                  label={recipeImportOwnershipLabel(
                    result.ownership_scope ?? ownershipScope,
                  )}
                />
              )}
              {kind === "recipes" && (
                <Chip
                  variant="outlined"
                  label={`Компонентов: ${result.component_count}`}
                />
              )}
              {kind === "recipes" && (
                <Chip
                  variant="outlined"
                  label={`Заметок: ${result.note_count}`}
                />
              )}
            </Stack>

            {result.valid ? (
              <Alert severity="success">
                Файл прошёл проверку и готов к импорту.
              </Alert>
            ) : (
              <Alert severity="error">
                Исправьте ошибки и повторите проверку. Ничего не импортировано.
              </Alert>
            )}

            {result.errors.map((item, index) => (
              <Alert
                key={`${item.row}-${item.field ?? "general"}-${index}`}
                severity="error"
              >
                {item.row > 0 ? `Строка ${item.row}` : "Файл"}
                {item.field ? `, поле ${item.field}` : ""}: {item.message}
              </Alert>
            ))}
          </Stack>
        </Paper>
      )}
    </Stack>
  );
}
