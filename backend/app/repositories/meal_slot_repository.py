from sqlalchemy.orm import Session

from app.models.meal_slot import MealSlotORM


class MealSlotRepository:
    """Repository for meal slot editing."""

    def __init__(self, session: Session):
        self.session = session

    def get(self, slot_id: str) -> MealSlotORM | None:
        return (
            self.session.query(MealSlotORM)
            .filter(MealSlotORM.id == slot_id)
            .first()
        )

    def save(self, slot: MealSlotORM) -> None:
        self.session.add(slot)
        self.session.commit()
