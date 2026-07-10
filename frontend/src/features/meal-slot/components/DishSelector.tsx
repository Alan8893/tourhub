import { MenuItem, Select } from "@mui/material";

import { useDishes } from "../hooks/useDishes";

interface DishSelectorProps {
  value?: string;
  onChange: (dishId: string) => void;
}

export default function DishSelector({
  value,
  onChange,
}: DishSelectorProps) {
  const { data: dishes = [] } = useDishes();

  return (
    <Select
      value={value ?? ""}
      displayEmpty
      onChange={(event) => onChange(event.target.value)}
    >
      <MenuItem value="">Select dish</MenuItem>

      {dishes.map((dish) => (
        <MenuItem key={dish.id} value={dish.id}>
          {dish.name}
        </MenuItem>
      ))}
    </Select>
  );
}
