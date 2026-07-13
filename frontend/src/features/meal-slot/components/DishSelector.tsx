import { MenuItem, Select } from "@mui/material";

import { useDishes } from "../hooks/useDishes";

interface DishSelectorProps {
  value: string;
  onChange: (dishId: string) => void;
}

export default function DishSelector({ value, onChange }: DishSelectorProps) {
  const { data: dishes = [] } = useDishes();

  return (
    <Select
      size="small"
      value={value}
      displayEmpty
      onChange={(event) => onChange(String(event.target.value))}
      sx={{ minWidth: 220 }}
    >
      <MenuItem value="">
        <em>Select dish</em>
      </MenuItem>
      {dishes.map((dish) => (
        <MenuItem key={dish.id} value={dish.id}>
          {dish.name}
        </MenuItem>
      ))}
    </Select>
  );
}
