import { Box, CircularProgress } from "@mui/material";
import { PropsWithChildren } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../providers/AuthProvider";

export default function RequireAuthenticated({ children }: PropsWithChildren) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <Box sx={{ minHeight: "100vh", display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Проверка входа" />
      </Box>
    );
  }

  if (!user) {
    const destination = `${location.pathname}${location.search}${location.hash}`;
    return <Navigate to="/login" replace state={{ from: destination }} />;
  }

  return children;
}
