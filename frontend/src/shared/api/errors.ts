export interface ApiError {
  message: string;
  status?: number;
}

export function normalizeApiError(error: unknown): ApiError {
  if (typeof error === "object" && error !== null && "message" in error) {
    return {
      message: String(error.message),
    };
  }

  return {
    message: "Unknown API error",
  };
}
