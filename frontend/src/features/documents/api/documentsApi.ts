import { apiClient } from "@/shared/api/client";

export async function downloadPurchaseDocument(
  projectId: number,
  format: "pdf" | "excel" | "print",
): Promise<Blob> {
  const response = await apiClient.get<Blob>(
    `/projects/${projectId}/documents/purchase/${format}`,
    {
      responseType: "blob",
    },
  );

  return response.data;
}

export async function downloadDocumentPackage(projectId: number): Promise<Blob> {
  const response = await apiClient.get<Blob>(
    `/projects/${projectId}/documents/package`,
    {
      responseType: "blob",
    },
  );

  return response.data;
}
