from dataclasses import dataclass


@dataclass
class Product:
    """
    Base food product used in recipes.
    """

    id: str
    name: str
    unit: str  # g, ml, pcs