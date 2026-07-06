from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.dish import DishORM


class DishRepository:

    def __init__(self, session: Session):
        self.session = session

    def get(self, dish_id: str) -> Optional[DishORM]:
        return self.session.get(DishORM, dish_id)

    def list(self) -> List[DishORM]:
        return self.session.query(DishORM).all()

    def add(self, dish: DishORM) -> None:
        self.session.add(dish)
        self.session.commit()