import type {
  DishMealRole,
  DishMealRolesWriteInput,
  DishWriteInput,
  MealRole,
  MealType,
} from "../api/dishApi";

export interface DishFormState {
  name: string;
  recipeId: string;
}

export interface MealTypeOption {
  mealType: MealType;
  label: string;
  shortLabel: string;
}

export interface MealRoleOption {
  role: MealRole;
  label: string;
  shortLabel: string;
  description: string;
  allowedMealTypes: readonly MealType[];
}

export interface MealRoleDraftItem {
  selected: boolean;
  isRepeatable: boolean;
  allowedMealTypes: Record<MealType, boolean>;
}

export type MealRoleDraft = Record<MealRole, MealRoleDraftItem>;

export const MEAL_TYPE_OPTIONS: readonly MealTypeOption[] = [
  { mealType: "breakfast", label: "Завтрак", shortLabel: "завтрак" },
  { mealType: "snack", label: "Перекус", shortLabel: "перекус" },
  { mealType: "lunch", label: "Обед", shortLabel: "обед" },
  { mealType: "dinner", label: "Ужин", shortLabel: "ужин" },
];

const MAIN_MEAL_TYPES: readonly MealType[] = ["breakfast", "lunch", "dinner"];

export const MEAL_ROLE_OPTIONS: readonly MealRoleOption[] = [
  {
    role: "main",
    label: "Основное блюдо",
    shortLabel: "Основное",
    description: "Главное приготовленное или сытное блюдо приёма пищи.",
    allowedMealTypes: MAIN_MEAL_TYPES,
  },
  {
    role: "addition",
    label: "Дополнение",
    shortLabel: "Дополнение",
    description: "Хлеб, салат, бутерброды или другое сопровождение.",
    allowedMealTypes: MAIN_MEAL_TYPES,
  },
  {
    role: "drink",
    label: "Напиток",
    shortLabel: "Напиток",
    description: "Чай, кофе, компот или другой напиток.",
    allowedMealTypes: MAIN_MEAL_TYPES,
  },
  {
    role: "snack",
    label: "Перекус",
    shortLabel: "Перекус",
    description: "Фрукты, сладости, орехи, сухофрукты или другой перекус.",
    allowedMealTypes: ["snack"],
  },
];

function emptyMealTypeDraft(): Record<MealType, boolean> {
  return {
    breakfast: false,
    snack: false,
    lunch: false,
    dinner: false,
  };
}

function emptyMealRoleDraftItem(): MealRoleDraftItem {
  return {
    selected: false,
    isRepeatable: false,
    allowedMealTypes: emptyMealTypeDraft(),
  };
}

function emptyMealRoleDraft(): MealRoleDraft {
  return {
    main: emptyMealRoleDraftItem(),
    addition: emptyMealRoleDraftItem(),
    drink: emptyMealRoleDraftItem(),
    snack: emptyMealRoleDraftItem(),
  };
}

export function toDishWriteInput(state: DishFormState): DishWriteInput {
  const name = state.name.trim();
  if (!name) throw new Error("Введите название блюда.");
  if (!state.recipeId) throw new Error("Выберите рецепт.");
  return { name, recipe_id: state.recipeId };
}

export function createMealRoleDraft(assignments: DishMealRole[]): MealRoleDraft {
  const draft = emptyMealRoleDraft();
  for (const assignment of assignments) {
    const allowedMealTypes = emptyMealTypeDraft();
    for (const mealType of assignment.allowed_meal_types) {
      allowedMealTypes[mealType] = true;
    }
    draft[assignment.role] = {
      selected: true,
      isRepeatable: assignment.is_repeatable,
      allowedMealTypes,
    };
  }
  return draft;
}

export function setMealRoleSelected(
  draft: MealRoleDraft,
  role: MealRole,
  selected: boolean,
): MealRoleDraft {
  return {
    ...draft,
    [role]: selected
      ? { ...draft[role], selected: true }
      : emptyMealRoleDraftItem(),
  };
}

export function setMealRoleRepeatable(
  draft: MealRoleDraft,
  role: MealRole,
  isRepeatable: boolean,
): MealRoleDraft {
  if (!draft[role].selected) return draft;
  return {
    ...draft,
    [role]: {
      ...draft[role],
      isRepeatable,
    },
  };
}

export function setMealRoleMealTypeSelected(
  draft: MealRoleDraft,
  role: MealRole,
  mealType: MealType,
  selected: boolean,
): MealRoleDraft {
  const option = getMealRoleOption(role);
  if (!draft[role].selected || !option.allowedMealTypes.includes(mealType)) return draft;
  return {
    ...draft,
    [role]: {
      ...draft[role],
      allowedMealTypes: {
        ...draft[role].allowedMealTypes,
        [mealType]: selected,
      },
    },
  };
}

export function toDishMealRolesWriteInput(draft: MealRoleDraft): DishMealRolesWriteInput {
  return {
    roles: MEAL_ROLE_OPTIONS.filter(({ role }) => draft[role].selected).map((option) => {
      const allowedMealTypes = MEAL_TYPE_OPTIONS
        .filter(({ mealType }) => (
          option.allowedMealTypes.includes(mealType)
          && draft[option.role].allowedMealTypes[mealType]
        ))
        .map(({ mealType }) => mealType);
      if (allowedMealTypes.length === 0) {
        throw new Error(`Выберите хотя бы один приём пищи для роли «${option.label}».`);
      }
      return {
        role: option.role,
        is_repeatable: draft[option.role].isRepeatable,
        allowed_meal_types: allowedMealTypes,
      };
    }),
  };
}

export function getMealRoleOption(role: MealRole): MealRoleOption {
  const option = MEAL_ROLE_OPTIONS.find((candidate) => candidate.role === role);
  if (!option) throw new Error(`Unknown meal role: ${role}`);
  return option;
}

export function formatMealTypeSummary(mealTypes: MealType[]): string {
  const selected = new Set(mealTypes);
  return MEAL_TYPE_OPTIONS.filter(({ mealType }) => selected.has(mealType))
    .map(({ shortLabel }) => shortLabel)
    .join(", ");
}

export function formatMealRoleSummary(assignments: DishMealRole[]): string {
  if (assignments.length === 0) return "Роли не назначены";
  const byRole = new Map(assignments.map((assignment) => [assignment.role, assignment]));
  return MEAL_ROLE_OPTIONS.filter(({ role }) => byRole.has(role))
    .map(({ role, shortLabel }) => {
      const assignment = byRole.get(role)!;
      return `${shortLabel}: ${formatMealTypeSummary(assignment.allowed_meal_types)}`;
    })
    .join("; ");
}
