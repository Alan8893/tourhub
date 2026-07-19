from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.dish import DishORM
from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM
from app.models.recipe_component_type import RecipeComponentType
from app.models.recipe_lifecycle_status import RecipeLifecycleStatus
from app.models.recipe_scope import RecipeScope
from app.models.user import UserORM
from app.policies.alcohol_policy import AlcoholPolicy, AlcoholPolicyViolation
from app.services.recipe_access_service import RecipeAccessService

CALCULATION_TYPES = {"per_person", "fixed_group", "package_per_people"}


class RecipeCommandService:
    def __init__(self, session: Session, actor: UserORM | None = None):
        self.session = session
        self.actor = actor

    def create_recipe(self, name: str) -> RecipeORM:
        normalized_name = name.strip()
        AlcoholPolicy.require_recipe_name_allowed(normalized_name)
        is_interactive = self.actor is not None
        recipe = RecipeORM(
            id=str(uuid4()),
            name=normalized_name,
            scope=(
                RecipeScope.PERSONAL.value
                if is_interactive
                else RecipeScope.CLUB.value
            ),
            owner_user_id=self.actor.id if self.actor is not None else None,
            lifecycle_status=(
                RecipeLifecycleStatus.DRAFT.value
                if is_interactive
                else RecipeLifecycleStatus.PUBLISHED.value
            ),
        )
        self.session.add(recipe)
        self._commit()
        self.session.refresh(recipe)
        return recipe

    def rename_recipe(self, recipe_id: str, name: str) -> RecipeORM:
        normalized_name = name.strip()
        AlcoholPolicy.require_recipe_name_allowed(normalized_name)
        recipe = self._get_editable_recipe(recipe_id)
        recipe.name = normalized_name
        self._commit()
        self.session.refresh(recipe)
        return recipe

    def archive_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self._get_visible_recipe(recipe_id)
        RecipeAccessService.require_archivable(recipe, self.actor)
        recipe.is_archived = True
        self._commit()
        self.session.refresh(recipe)
        return recipe

    def restore_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self._get_visible_recipe(recipe_id)
        RecipeAccessService.require_restorable(recipe, self.actor)
        if recipe.archived_by_alcohol_policy:
            raise AlcoholPolicyViolation(
                "Рецепт архивирован центральной политикой запрета алкоголя и не может быть восстановлен."
            )
        AlcoholPolicy.require_recipe_content_allowed(recipe)
        recipe.is_archived = False
        self._commit()
        self.session.refresh(recipe)
        return recipe

    def delete_recipe(self, recipe_id: str) -> None:
        recipe = self._get_visible_recipe(recipe_id)
        RecipeAccessService.require_deletable(recipe, self.actor)
        linked_dish = self.session.scalar(
            select(DishORM.id).where(DishORM.recipe_id == recipe_id).limit(1)
        )
        if linked_dish is not None:
            raise ValueError("Recipe is used by a dish and cannot be deleted")
        self.session.delete(recipe)
        self._commit()

    def add_component(
        self,
        recipe_id: str,
        product_id: str,
        component_type: str,
        amount: int,
        unit: str,
        calculation_type: str,
        people_count: int | None,
    ) -> RecipeComponentORM:
        recipe = self._get_editable_recipe(recipe_id)
        AlcoholPolicy.require_recipe_name_allowed(recipe.name)
        self._get_product(product_id)
        self._validate_component(component_type, calculation_type, people_count)
        component = RecipeComponentORM(
            id=str(uuid4()),
            recipe_id=recipe_id,
            product_id=product_id,
            component_type=component_type,
            amount=amount,
            unit=unit.strip(),
            calculation_type=calculation_type,
            people_count=people_count,
        )
        self.session.add(component)
        self._commit()
        self.session.refresh(component)
        return component

    def update_component(
        self,
        recipe_id: str,
        component_id: str,
        product_id: str,
        component_type: str,
        amount: int,
        unit: str,
        calculation_type: str,
        people_count: int | None,
    ) -> RecipeComponentORM:
        recipe = self._get_editable_recipe(recipe_id)
        AlcoholPolicy.require_recipe_name_allowed(recipe.name)
        component = self._get_component(recipe_id, component_id)
        self._get_product(product_id)
        self._validate_component(component_type, calculation_type, people_count)
        component.product_id = product_id
        component.component_type = component_type
        component.amount = amount
        component.unit = unit.strip()
        component.calculation_type = calculation_type
        component.people_count = people_count
        self._commit()
        self.session.refresh(component)
        return component

    def delete_component(self, recipe_id: str, component_id: str) -> None:
        self._get_editable_recipe(recipe_id)
        component = self._get_component(recipe_id, component_id)
        self.session.delete(component)
        self._commit()

    def _get_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self.session.get(RecipeORM, recipe_id)
        if recipe is None:
            raise LookupError("Recipe not found")
        return recipe

    def _get_visible_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self._get_recipe(recipe_id)
        return RecipeAccessService.require_visible(recipe, self.actor)

    def _get_editable_recipe(self, recipe_id: str) -> RecipeORM:
        recipe = self._get_visible_recipe(recipe_id)
        return RecipeAccessService.require_editable(recipe, self.actor)

    def _get_product(self, product_id: str) -> ProductORM:
        product = self.session.get(ProductORM, product_id)
        if product is None:
            raise LookupError("Product not found")
        AlcoholPolicy.require_product_record_allowed(product)
        return product

    def _get_component(self, recipe_id: str, component_id: str) -> RecipeComponentORM:
        component = self.session.get(RecipeComponentORM, component_id)
        if component is None or component.recipe_id != recipe_id:
            raise LookupError("Recipe component not found")
        return component

    @staticmethod
    def _validate_component(
        component_type: str,
        calculation_type: str,
        people_count: int | None,
    ) -> None:
        if component_type not in {item.value for item in RecipeComponentType}:
            raise ValueError("Unsupported component type")
        if calculation_type not in CALCULATION_TYPES:
            raise ValueError("Unsupported calculation type")
        if calculation_type == "package_per_people" and not people_count:
            raise ValueError("people_count is required for package_per_people")

    def _commit(self) -> None:
        try:
            self.session.commit()
        except IntegrityError as exc:
            self.session.rollback()
            raise ValueError("Recipe name must be unique") from exc
        except Exception:
            self.session.rollback()
            raise
