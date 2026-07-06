from dataclasses import dataclass
from datetime import date


@dataclass
class Trip:
    """
    Represents a concrete hiking trip inside a project.
    """

    id: str
    project_id: str
    start_date: date
    days: int