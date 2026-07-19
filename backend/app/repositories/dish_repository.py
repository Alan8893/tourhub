from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload, selectinload

from app.models.dish import DishORM
from app.models.dish_meal_role import DishMealRoleORM
from app.models.dish_recipe_variant import DishRecipeVariantORM


class DishRepository:
    def __init__(self, session: Session):
        self.session = session

    def get(self, dish_id: str) -> DishORM | None:
        return self.session.scalar(
            select(DishORM)
            .options(
                joinedload(DishORM.recipe),
                selectinload(DishORM.recipe_variants).joinedload(
                    DishRecipeVariantORM.recipe
                ),
                selectinload(DishORM.meal_roles).selectinload(
                    DishMealRoleORM.meal_types
                ),
            )
            .where(DishORM.id == dish_id, DishORM.is_archived.is_(False))
        )

    def list(self) -> list[DishORM]:
        return list(
            self.session.scalars(
                select(DishORM)
                .options(
                    joinedload(DishORM.recipe),
                    selectinload(DishORM.recipe_variants).joinedload(
                        DishRecipeVariantORM.recipe
                    ),
                    selectinload(DishORM.meal_roles).selectinload(
                        DishMealRoleORM.meal_types
                    ),
                )
                .where(DishORM.is_archived.is_(False))
                .order_by(DishORM.name)
            )
            .unique()
            .all()
        )

    def add(self, dish: DishORM) -> None:
        self.session.add(dish)

    def commit(self) -> None:
        self.session.commit()
