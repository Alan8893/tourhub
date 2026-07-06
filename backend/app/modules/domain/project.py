from dataclasses import dataclass
from datetime import date
from typing import List, Optional


@dataclass
class Project:
    """
    Core aggregate root for TourHub.
    Represents a hiking preparation project.
    """

    id: str
    name: str
    start_date: date
    end_date: date
    participants: int

    notes: Optional[str] = None