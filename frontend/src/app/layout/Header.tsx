import { AppBar, Box, Button, IconButton, Stack, Toolbar, Typography } from "@mui/material";
import { useNavigate } from "react-router-dom";

import { userRoleLabel } from "@/features/auth/model/roleLabels";
import { useAuth } from "@/features/auth/providers/AuthProvider";

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
  const { user } = useAuth();
  const navigate = useNavigate();

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
          <Button
            color="inherit"
            onClick={() => navigate("/account")}
            aria-label={`Открыть личный кабинет. ${user.display_name}. Роль: ${userRoleLabel(user.role)}.`}
            sx={{ minWidth: 0, maxWidth: { xs: 112, sm: 280 }, textTransform: "none" }}
          >
            <Stack direction="row" spacing={1} alignItems="center" sx={{ minWidth: 0 }}>
              <Box
                aria-hidden
                sx={{
                  width: 30,
                  height: 30,
                  borderRadius: "50%",
                  display: "grid",
                  placeItems: "center",
                  bgcolor: "rgba(255,255,255,0.18)",
                  flexShrink: 0,
                  fontWeight: 700,
                }}
              >
                {user.display_name.trim().slice(0, 1).toUpperCase() || "Л"}
              </Box>
              <Typography sx={{ display: { xs: "block", sm: "none" } }}>ЛК</Typography>
              <Stack spacing={0} sx={{ display: { xs: "none", sm: "flex" }, minWidth: 0 }}>
                <Typography variant="body2" noWrap>
                  {user.display_name}
                </Typography>
                <Typography variant="caption" noWrap sx={{ opacity: 0.82 }}>
                  {userRoleLabel(user.role)}
                </Typography>
              </Stack>
            </Stack>
          </Button>
        ) : (
          <Button color="inherit" size="small" onClick={() => navigate("/login")}>
            Войти
          </Button>
        )}
      </Toolbar>
    </AppBar>
  );
}
