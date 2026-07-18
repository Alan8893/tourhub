from enum import Enum


class RecipeGenerationMode(str, Enum):
    CLUB_ONLY = "club_only"
    CLUB_AND_PERSONAL = "club_and_personal"
    PERSONAL_PREFERRED = "personal_preferred"
