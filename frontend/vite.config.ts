import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

export function preserveApiPrefix(path: string): string {
  if (path === "/api" || path.startsWith("/api/")) {
    return path;
  }

  return `/api${path.startsWith("/") ? path : `/${path}`}`;
}

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      "@": "/src",
    },
  },
  server: {
    port: 5173,
    host: true,
    proxy: {
      "/api": {
        target: "http://backend:8000",
        changeOrigin: true,
        rewrite: preserveApiPrefix,
      },
    },
  },
});
