from dataclasses import dataclass


@dataclass
class Dish:
    """
    A dish that can be part of meal planning.
    """

    id: str
    name: str
    recipe_id: str