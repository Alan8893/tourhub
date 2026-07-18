import { Alert, Box, CircularProgress, Paper, Stack, Typography } from "@mui/material";
import { PropsWithChildren } from "react";
import { Navigate, useLocation } from "react-router-dom";

import { useAuth } from "../providers/AuthProvider";

export default function RequireAdministrator({ children }: PropsWithChildren) {
  const { user, isLoading } = useAuth();
  const location = useLocation();

  if (isLoading) {
    return (
      <Box sx={{ py: 10, display: "grid", placeItems: "center" }}>
        <CircularProgress aria-label="Проверка доступа" />
      </Box>
    );
  }

  if (!user) {
    const destination = `${location.pathname}${location.search}${location.hash}`;
    return <Navigate to="/login" replace state={{ from: destination }} />;
  }

  if (user.role !== "administrator") {
    return (
      <Paper variant="outlined" sx={{ p: { xs: 2, md: 3 } }}>
        <Stack spacing={2}>
          <Typography variant="h5">Недостаточно прав</Typography>
          <Alert severity="warning">
            Системные настройки доступны только пользователю с ролью «Администратор».
          </Alert>
        </Stack>
      </Paper>
    );
  }

  return children;
}
