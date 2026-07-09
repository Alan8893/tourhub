import { useQuery } from "@tanstack/react-query";

import { getDishes } from "../api/dishApi";

export function useDishes() {
  return useQuery({
    queryKey: ["dishes"],
    queryFn: getDishes,
  });
}
