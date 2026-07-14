import react from "@vitejs/plugin-react";
import { defineConfig } from "vite";

const preserveApiPrefix = (path: string): string => {
  const normalizedPath = path.charAt(0) === "/" ? path : `/${path}`;

  if (normalizedPath === "/api" || normalizedPath.indexOf("/api/") === 0) {
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
