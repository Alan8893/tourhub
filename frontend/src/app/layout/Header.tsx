import { AppBar, Box, IconButton, Toolbar, Typography } from "@mui/material";

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  return (
    <AppBar position="static">
      <Toolbar>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="Открыть меню"
          onClick={onMenuClick}
          sx={{ display: { xs: "inline-flex", sm: "none" }, mr: 1 }}
        >
          <Box component="span" aria-hidden sx={{ fontSize: 26, lineHeight: 1 }}>
            ☰
          </Box>
        </IconButton>
        <Typography variant="h6">TourHub</Typography>
      </Toolbar>
    </AppBar>
  );
}
