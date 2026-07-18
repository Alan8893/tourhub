import axios from "axios";

import { notifySessionInvalidated } from "@/features/auth/model/sessionEvents";
import { env } from "@/shared/config/env";

const AUTH_ENTRY_PATHS = ["/auth/login", "/auth/bootstrap"];

function isAuthenticationEntryRequest(url: string | undefined): boolean {
  if (!url) return false;
  return AUTH_ENTRY_PATHS.some((path) => url.endsWith(path));
}

export const apiClient = axios.create({
  baseURL: env.apiUrl,
  withCredentials: true,
  headers: {
    "Content-Type": "application/json",
  },
});

apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (
      axios.isAxiosError(error) &&
      error.response?.status === 401 &&
      !isAuthenticationEntryRequest(error.config?.url)
    ) {
      notifySessionInvalidated();
    }
    return Promise.reject(error);
  },
);
