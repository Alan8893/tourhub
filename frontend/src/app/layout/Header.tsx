import { AppBar, Box, Button, IconButton, Stack, Toolbar, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

import { useAuth } from "@/features/auth/providers/AuthProvider";

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  async function signOut() {
    await logout();
    navigate("/login", { replace: true });
  }

  return (
    <AppBar position="static">
      <Toolbar sx={{ gap: 1 }}>
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
        <Typography variant="h6" sx={{ flexGrow: 1 }}>
          TourHub
        </Typography>
        {user ? (
          <Stack direction="row" spacing={1} alignItems="center" sx={{ minWidth: 0 }}>
            <Typography
              variant="body2"
              noWrap
              sx={{ display: { xs: "none", sm: "block" }, maxWidth: 220 }}
            >
              {user.display_name}
            </Typography>
            <Button color="inherit" size="small" onClick={() => void signOut()}>
              Выйти
            </Button>
          </Stack>
        ) : (
          <Button color="inherit" size="small" onClick={() => navigate("/login")}>
            Войти
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
}
