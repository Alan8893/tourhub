import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const preserveApiPrefix = (path: string): string => {
  const normalizedPath = path.startsWith("/") ? path : `/${path}`;

  if (normalizedPath === "/api" || normalizedPath.startsWith("/api/")) {
    return normalizedPath;
  }

  return `/api${normalizedPath}`;
};

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
