import { apiClient } from "@/api/client";

export async function downloadPurchaseDocument(
  projectId: number,
  format: "pdf" | "excel" | "print",
) {
  const response = await apiClient.get(
    `/api/v1/projects/${projectId}/documents/purchase/${format}`,
    {
      responseType: "blob",
    },
  );

  return response.data;
}

export async function downloadDocumentPackage(projectId: number) {
  const response = await apiClient.get(
    `/api/v1/projects/${projectId}/documents/package`,
    {
      responseType: "blob",
    },
  );

  return response.data;
}
