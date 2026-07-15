export interface DishOption {
  id: string;
  name: string;
}

export interface DishListResponse {
  items: DishOption[];
}

export function extractDishOptions(response: DishListResponse): DishOption[] {
  return response.items;
}
