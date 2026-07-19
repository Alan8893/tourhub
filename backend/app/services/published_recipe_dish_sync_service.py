from uuid import uuid4

from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.models.dish import DishORM
from app.models.dish_recipe_variant import DishRecipeVariantORM
from app.models.recipe import RecipeORM


class PublishedRecipeDishSyncService:
    """Synchronize one published CLUB Recipe into the active Dish catalogue.

    This service never commits. Its caller owns the publication transaction.
    """

    def __init__(self, session: Session):
        self.session = session

    def synchronize(self, recipe: RecipeORM) -> DishORM:
        attached = self._find_attached_dish(recipe.id)
        if attached is not None:
            return attached

        same_name = self._find_active_same_name_dish(recipe.name)
        if same_name is not None:
            next_position = max(
                (variant.position for variant in same_name.recipe_variants),
                default=-1,
            ) + 1
            same_name.recipe_variants.append(
                DishRecipeVariantORM(
                    dish_id=same_name.id,
                    recipe_id=recipe.id,
                    position=next_position,
                )
            )
            self.session.flush()
            return same_name

        dish = DishORM(
            id=str(uuid4()),
            name=recipe.name,
            recipe_id=recipe.id,
        )
        dish.recipe_variants = [
            DishRecipeVariantORM(
                dish_id=dish.id,
                recipe_id=recipe.id,
                position=0,
            )
        ]
        self.session.add(dish)
        self.session.flush()
        return dish

    def _find_attached_dish(self, recipe_id: str) -> DishORM | None:
        statement = (
            select(DishORM)
            .outerjoin(
                DishRecipeVariantORM,
                DishRecipeVariantORM.dish_id == DishORM.id,
            )
            .options(selectinload(DishORM.recipe_variants))
            .where(
                or_(
                    DishORM.recipe_id == recipe_id,
                    DishRecipeVariantORM.recipe_id == recipe_id,
                )
            )
            .order_by(DishORM.is_archived, DishORM.name, DishORM.id)
            .with_for_update()
        )
        return self.session.scalars(statement).unique().first()

    def _find_active_same_name_dish(self, name: str) -> DishORM | None:
        statement = (
            select(DishORM)
            .options(selectinload(DishORM.recipe_variants))
            .where(
                DishORM.name == name,
                DishORM.is_archived.is_(False),
            )
            .order_by(DishORM.id)
            .with_for_update()
        )
        return self.session.scalar(statement)
