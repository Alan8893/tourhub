from dataclasses import dataclass
from typing import Dict


@dataclass
class Recipe:
    """
    Logical recipe definition (not DB entity yet).
    """

    id: str
    name: str

    ingredients: Dict[str, float]
    # product_id -> amount per person