from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.dish import DishORM
from app.models.dish_meal_role import DishMealRoleORM


class DishRepository:

    def __init__(self, session: Session):
        self.session = session

    def get(self, dish_id: str) -> DishORM | None:
        return self.session.get(DishORM, dish_id)

    def list(self) -> list[DishORM]:
        return (
            self.session.query(DishORM)
            .options(
                joinedload(DishORM.recipe),
                selectinload(DishORM.meal_roles).selectinload(
                    DishMealRoleORM.meal_types
                ),
            )
            .all()
        )

    def add(self, dish: DishORM) -> None:
        self.session.add(dish)

    def commit(self) -> None:
        self.session.commit()
