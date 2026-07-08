import { List, ListItemButton, ListItemText, Drawer } from "@mui/material";

const menuItems = [
  { label: "Projects", path: "/projects" },
  { label: "Dashboard", path: "/dashboard" },
];

export default function Sidebar() {
  return (
    <Drawer variant="permanent">
      <List sx={{ width: 240 }}>
        {menuItems.map((item) => (
          <ListItemButton key={item.path}>
            <ListItemText primary={item.label} />
          </ListItemButton>
        ))}
      </List>
    </Drawer>
  );
}
