import { Button, Card, CardContent, Typography } from "@mui/material";

import { useProjectWorkflow } from "@/features/project-workflow";

import {
  downloadDocumentPackage,
  downloadPurchaseDocument,
} from "../api/documentsApi";

function saveBlob(blob: Blob, filename: string) {
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");

  link.href = url;
  link.download = filename;
  link.click();

  URL.revokeObjectURL(url);
}

export default function DocumentsWidget() {
  const { projectId, preparationResult } = useProjectWorkflow();

  const ready = Boolean(projectId && preparationResult);

  async function handleDownload(format: "pdf" | "excel") {
    if (!projectId) return;

    const blob = await downloadPurchaseDocument(projectId, format);
    saveBlob(blob, `purchase-${format}`);
  }

  async function handlePackageDownload() {
    if (!projectId) return;

    const blob = await downloadDocumentPackage(projectId);
    saveBlob(blob, "project-documents.zip");
  }

  return (
    <Card>
      <CardContent>
        <Typography variant="h6">Documents</Typography>

        <Typography>
          {ready
            ? `Documents ready for project ${projectId}`
            : "Generate expedition documents."}
        </Typography>

        {ready && (
          <>
            <Button onClick={() => handleDownload("pdf")}>Export PDF</Button>
            <Button onClick={() => handleDownload("excel")}>Export Excel</Button>
            <Button onClick={handlePackageDownload}>Download Package</Button>
          </>
        )}
      </CardContent>
    </Card>
  );
}
