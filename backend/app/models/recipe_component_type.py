from enum import Enum


class RecipeComponentType(str, Enum):
    """
    Defines the role of a product inside a recipe.
    """

    BASE = "base"
    COOKING = "cooking"
    OPTIONAL = "optional"
    SERVING_ADD_ON = "serving_add_on"
