import { Alert, Button, Card, CardContent, Stack, Typography } from "@mui/material";
import { useState } from "react";

import {
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
}

export default function DocumentsDownloadCard({ projectId, ready }: Props) {
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
    <Card>
      <CardContent>
        <Stack spacing={1.5}>
          <Typography variant="h6">Документы</Typography>
          <Typography>
            {ready
              ? "Русские документы закупки и оборудования готовы к скачиванию."
              : "Сначала подготовьте закупку, чек-лист и список оборудования."}
          </Typography>

          {error && <Alert severity="error">{error}</Alert>}

          {ready && (
            <Stack spacing={1.5}>
              <Stack spacing={0.75}>
                <Typography variant="subtitle2">Закупка</Typography>
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
                <Typography variant="subtitle2">Оборудование</Typography>
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

              <Button
                variant="contained"
                disabled={isDownloading}
                onClick={handlePackageDownload}
              >
                Скачать полный пакет
              </Button>
            </Stack>
          )}
        </Stack>
      </CardContent>
    </Card>
  );
}
