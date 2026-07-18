from enum import Enum


class RecipeLifecycleStatus(str, Enum):
    DRAFT = "draft"
    SUBMITTED = "submitted"
    REJECTED = "rejected"
    PUBLISHED = "published"
