import { useId } from "react";

import {
  FormControl,
  FormHelperText,
  InputLabel,
  MenuItem,
  Select,
} from "@mui/material";

import { useDishes } from "../hooks/useDishes";

interface DishSelectorProps {
  value: string;
  onChange: (dishId: string) => void;
  label?: string;
  disabled?: boolean;
  fullWidth?: boolean;
}

export default function DishSelector({
  value,
  onChange,
  label = "Блюдо",
  disabled = false,
  fullWidth = false,
}: DishSelectorProps) {
  const selectorId = useId();
  const { data: dishes = [], isError, isLoading } = useDishes();

  return (
    <FormControl
      size="small"
      fullWidth={fullWidth}
      error={isError}
      sx={{ minWidth: fullWidth ? undefined : { xs: "100%", sm: 220 } }}
    >
      <InputLabel id={`${selectorId}-label`} shrink>
        {label}
      </InputLabel>
      <Select
        labelId={`${selectorId}-label`}
        id={selectorId}
        value={value}
        label={label}
        displayEmpty
        disabled={disabled || isLoading || isError}
        onChange={(event) => onChange(String(event.target.value))}
      >
        <MenuItem value="">
          <em>{isLoading ? "Загрузка блюд…" : "Выберите блюдо"}</em>
        </MenuItem>
        {dishes.map((dish) => (
          <MenuItem key={dish.id} value={dish.id}>
            {dish.name}
          </MenuItem>
        ))}
      </Select>
      {isError && <FormHelperText>Не удалось загрузить список блюд.</FormHelperText>}
    </FormControl>
  );
}
