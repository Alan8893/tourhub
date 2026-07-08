import { useQuery } from "@tanstack/react-query";

import { getMeta } from "../../../api/meta";

export function useMeta() {
  return useQuery({
    queryKey: ["meta"],
    queryFn: getMeta,
  });
}
