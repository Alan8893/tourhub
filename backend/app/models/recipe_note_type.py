from enum import Enum


class RecipeNoteType(str, Enum):
    COOKING_TIP = "cooking_tip"
    EXPEDITION_TIP = "expedition_tip"
    SERVING_TIP = "serving_tip"
