export function normalizeApiUrl(value?: string): string {
  const configured = value?.trim();

  if (!configured) {
    return "/api/v1";
  }

  if (configured === "/v1" || configured.startsWith("/v1/")) {
    return `/api${configured}`;
  }

  return configured.replace(/\/$/, "");
}
