import { AppBar, Box, Button, IconButton, Stack, Toolbar, Typography } from "@mui/material";
import { useLocation, useNavigate } from "react-router-dom";

import { userRoleLabel } from "@/features/auth/model/roleLabels";
import { useAuth } from "@/features/auth/providers/AuthProvider";

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const { user, logout } = useAuth();
  const location = useLocation();
  const navigate = useNavigate();

  async function signOut() {
    const destination = `${location.pathname}${location.search}${location.hash}`;
    try {
      await logout();
    } finally {
      navigate("/login", { replace: true, state: { from: destination } });
    }
  }

  return (
    <AppBar position="static">
      <Toolbar sx={{ gap: 1 }}>
        <IconButton
          edge="start"
          color="inherit"
          aria-label="Открыть меню"
          onClick={onMenuClick}
          sx={{ display: { xs: "inline-flex", md: "none" }, mr: 1 }}
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
            <Stack
              spacing={0}
              sx={{ display: { xs: "none", sm: "flex" }, minWidth: 0, maxWidth: 240 }}
              aria-label={`Текущий пользователь: ${user.display_name}. Роль: ${userRoleLabel(user.role)}.`}
            >
              <Typography variant="body2" noWrap>
                {user.display_name}
              </Typography>
              <Typography variant="caption" noWrap sx={{ opacity: 0.82 }}>
                {userRoleLabel(user.role)}
              </Typography>
            </Stack>
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
