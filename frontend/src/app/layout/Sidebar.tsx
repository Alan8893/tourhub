import { Drawer, List, ListItemButton, ListItemText } from "@mui/material";
import { NavLink } from "react-router-dom";

const drawerWidth = 240;

const menuItems = [
  { label: "Проекты", path: "/projects" },
  { label: "Блюда", path: "/dishes" },
  { label: "Рецепты", path: "/recipes" },
  { label: "Импорт", path: "/catalog-import" },
  { label: "Настройки", path: "/settings" },
];

interface SidebarProps {
  mobileOpen: boolean;
  onMobileClose: () => void;
}

function NavigationList({ onNavigate }: { onNavigate?: () => void }) {
  return (
    <List sx={{ width: "100%", pt: 1 }}>
      {menuItems.map((item) => (
        <ListItemButton
          key={item.path}
          component={NavLink}
          to={item.path}
          onClick={onNavigate}
          sx={{ px: 3, py: 1.5, "&.active": { bgcolor: "action.selected" } }}
        >
          <ListItemText primary={item.label} />
        </ListItemButton>
      ))}
    </List>
  );
}

export default function Sidebar({ mobileOpen, onMobileClose }: SidebarProps) {
  return (
    <>
      <Drawer
        variant="temporary"
        open={mobileOpen}
        onClose={onMobileClose}
        ModalProps={{ keepMounted: true }}
        sx={{
          display: { xs: "block", sm: "none" },
          "& .MuiDrawer-paper": {
            boxSizing: "border-box",
            width: "min(78vw, 280px)",
          },
        }}
      >
        <NavigationList onNavigate={onMobileClose} />
      </Drawer>

      <Drawer
        variant="permanent"
        sx={{
          display: { xs: "none", sm: "block" },
          width: drawerWidth,
          flexShrink: 0,
          "& .MuiDrawer-paper": {
            boxSizing: "border-box",
            width: drawerWidth,
          },
        }}
        open
      >
        <NavigationList />
      </Drawer>
    </>
  );
}
