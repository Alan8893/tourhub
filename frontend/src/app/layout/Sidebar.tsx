import { Drawer, List, ListItemButton, ListItemText } from "@mui/material";
import { NavLink } from "react-router-dom";

const menuItems = [
  { label: "Проекты", path: "/projects" },
  { label: "Блюда", path: "/dishes" },
  { label: "Рецепты", path: "/recipes" },
  { label: "Импорт каталога", path: "/catalog-import" },
];

export default function Sidebar() {
  return (
    <Drawer variant="permanent">
      <List sx={{ width: 240 }}>
        {menuItems.map((item) => (
          <ListItemButton
            key={item.path}
            component={NavLink}
            to={item.path}
            sx={{ "&.active": { bgcolor: "action.selected" } }}
          >
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  );
}
