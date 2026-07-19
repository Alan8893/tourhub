import { Alert, Button, Card, CardContent, Divider, Stack, Typography } from "@mui/material";
import { useState } from "react";

import {
  downloadConsolidatedDocument,
  downloadDocumentPackage,
  downloadEquipmentDocument,
  downloadPurchaseDocument,
} from "../api/documentsApi";

function saveBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  link.remove();

  URL.revokeObjectURL(url);
}

interface Props {
  projectId: number;
  ready: boolean;
  compact?: boolean;
}

export default function DocumentsDownloadCard({
  projectId,
  ready,
  compact = false,
}: Props) {
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function runDownload(action: () => Promise<Blob>, filename: string) {
    setIsDownloading(true);
    setError(null);

    try {
      const blob = await action();
      saveBlob(blob, filename);
    } catch {
      setError("Не удалось сформировать документ. Проверьте данные проекта и повторите попытку.");
    } finally {
      setIsDownloading(false);
    }
  }

  async function handleConsolidatedDownload(format: "pdf" | "excel") {
    await runDownload(
      () => downloadConsolidatedDocument(projectId, format),
      format === "pdf" ? "документы-похода.pdf" : "документы-похода.xlsx",
    );
  }

  async function handlePurchaseDownload(format: "pdf" | "excel") {
    await runDownload(
      () => downloadPurchaseDocument(projectId, format),
      format === "pdf" ? "закупка.pdf" : "закупка.xlsx",
    );
  }

  async function handleEquipmentDownload(format: "pdf" | "excel") {
    await runDownload(
      () => downloadEquipmentDocument(projectId, format),
      format === "pdf" ? "оборудование.pdf" : "оборудование.xlsx",
    );
  }

  async function handlePackageDownload() {
    await runDownload(
      () => downloadDocumentPackage(projectId),
      "документы-похода.zip",
    );
  }

  return (
    <Card
      variant={compact ? "outlined" : undefined}
      sx={{ height: compact ? "100%" : undefined, "& .MuiButton-root": { textTransform: "none" } }}
    >
      <CardContent>
        <Stack spacing={1.5} alignItems={compact ? "flex-start" : "stretch"}>
          <Typography variant="h6">Документы</Typography>
          <Typography color={compact ? "text.secondary" : undefined}>
            {ready
              ? "Русские документы закупки и оборудования готовы. Полный комплект также содержит параметры похода, меню, раскладку, предупреждения и комментарии."
              : "Сначала подготовьте закупку, чек-лист и список оборудования."}
          </Typography>

          {error && <Alert severity="error">{error}</Alert>}

          {ready && compact && (
            <Button
              variant="contained"
              disabled={isDownloading}
              onClick={handlePackageDownload}
            >
              Скачать полный пакет
            </Button>
          )}

          {ready && !compact && (
            <Stack spacing={2}>
              <Stack spacing={0.75}>
                <Typography variant="subtitle2">Полный комплект</Typography>
                <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                  <Button
                    variant="contained"
                    disabled={isDownloading}
                    onClick={() => handleConsolidatedDownload("pdf")}
                  >
                    Полный PDF
                  </Button>
                  <Button
                    variant="contained"
                    disabled={isDownloading}
                    onClick={() => handleConsolidatedDownload("excel")}
                  >
                    Полный Excel
                  </Button>
                </Stack>
                <Button
                  variant="outlined"
                  disabled={isDownloading}
                  onClick={handlePackageDownload}
                >
                  Скачать полный пакет
                </Button>
              </Stack>

              <Divider />

              <Typography variant="subtitle2">Отдельные документы</Typography>
              <Stack spacing={0.75}>
                <Typography variant="body2" color="text.secondary">
                  Закупка
                </Typography>
                <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                  <Button
                    disabled={isDownloading}
                    onClick={() => handlePurchaseDownload("pdf")}
                  >
                    Закупка PDF
                  </Button>
                  <Button
                    disabled={isDownloading}
                    onClick={() => handlePurchaseDownload("excel")}
                  >
                    Закупка Excel
                  </Button>
                </Stack>
              </Stack>

              <Stack spacing={0.75}>
                <Typography variant="body2" color="text.secondary">
                  Оборудование
                </Typography>
                <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
                  <Button
                    disabled={isDownloading}
                    onClick={() => handleEquipmentDownload("pdf")}
                  >
                    Оборудование PDF
                  </Button>
                  <Button
                    disabled={isDownloading}
                    onClick={() => handleEquipmentDownload("excel")}
                  >
                    Оборудование Excel
                  </Button>
                </Stack>
              </Stack>
            </Stack>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
