import { apiClient } from "@/api/client";

export async function downloadPurchaseDocument(
  projectId: number,
  format: "pdf" | "excel" | "print",
) {
  const response = await apiClient.get(
    `/projects/${projectId}/documents/purchase/${format}`,
    {
      responseType: "blob",
    },
  );

  return response.data;
}

export async function downloadDocumentPackage(projectId: number) {
  const response = await apiClient.get(
    `/projects/${projectId}/documents/package`,
    {
      responseType: "blob",
    },
  );

  return response.data;
}
