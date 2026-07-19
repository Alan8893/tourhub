import { Box } from "@mui/material";

import AppRouter from "./router";

export default function App() {
  return (
    <Box sx={{ minHeight: "100vh", width: "100%" }}>
      <AppRouter />
    </Box>
  );
}
