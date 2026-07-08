import { apiClient } from "./client";
import type { MetaResponse } from "./types/meta";

export async function getMeta(): Promise<MetaResponse> {
  const response = await apiClient.get<MetaResponse>("/meta");

  return response.data;
}
