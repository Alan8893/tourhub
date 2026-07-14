import { Alert, Button, Card, CardContent, Stack, Typography } from "@mui/material";
import { useState } from "react";

import { useProjectWorkflow } from "@/features/project-workflow";

import {
  downloadDocumentPackage,
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

export default function DocumentsWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();
  const [isDownloading, setIsDownloading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const ready = Boolean(
    projectId &&
      preparationResult?.purchase_list_id &&
      preparationResult.purchase_checklist_id,
  );

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

  async function handleDownload(format: "pdf" | "excel") {
    if (!projectId) return;

    await runDownload(
      () => downloadPurchaseDocument(projectId, format),
      format === "pdf" ? "закупка.pdf" : "закупка.xlsx",
    );
  }

  async function handlePackageDownload() {
    if (!projectId) return;

    await runDownload(
      () => downloadDocumentPackage(projectId),
      "документы-похода.zip",
    );
  }

  return (
    <Card>
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="h6">Документы</Typography>

          <Typography>
            {ready
              ? "Документы готовы к формированию и скачиванию."
              : "Сначала рассчитайте закупку и создайте чек-лист."}
          </Typography>

          {error && <Alert severity="error">{error}</Alert>}

          {ready && (
            <Stack direction={{ xs: "column", sm: "row" }} spacing={1}>
              <Button disabled={isDownloading} onClick={() => handleDownload("pdf")}>
                Скачать PDF
              </Button>
              <Button disabled={isDownloading} onClick={() => handleDownload("excel")}>
                Скачать Excel
              </Button>
              <Button disabled={isDownloading} onClick={handlePackageDownload}>
                Скачать пакет
              </Button>
            </Stack>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
