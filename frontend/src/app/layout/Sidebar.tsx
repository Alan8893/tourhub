import { Drawer, List, ListItemButton, ListItemText } from "@mui/material";
import { NavLink } from "react-router-dom";

import { useModuleVisibility } from "@/features/system-settings/providers/ModuleVisibilityProvider";

const drawerWidth = 240;

interface SidebarProps {
  mobileOpen: boolean;
  onMobileClose: () => void;
}

function NavigationList({ onNavigate }: { onNavigate?: () => void }) {
  const { settings } = useModuleVisibility();
  const menuItems = [
    { label: "Проекты", path: "/projects", visible: settings.projects_visible },
    { label: "Блюда", path: "/dishes", visible: settings.catalogue_visible },
    { label: "Рецепты", path: "/recipes", visible: settings.catalogue_visible },
    { label: "Импорт", path: "/catalog-import", visible: settings.catalog_import_visible },
    { label: "Настройки", path: "/settings", visible: true },
  ].filter((item) => item.visible);

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
