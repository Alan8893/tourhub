import { normalizeApiUrl } from "@/shared/config/apiUrl";

const apiUrl = normalizeApiUrl(import.meta.env.VITE_API_URL);

export const env = {
  apiUrl,
};
