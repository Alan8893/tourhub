from decimal import Decimal

from app.models.dish import DishORM
from app.models.ingredient import IngredientORM
from app.models.meal_plan import MealPlanORM
from app.models.meal_plan_day import MealPlanDayORM
from app.models.meal_slot import MealSlotORM
from app.models.meal_slot_dish import MealSlotDishORM
from app.models.product import ProductORM
from app.models.purchase_checklist import PurchaseChecklistORM
from app.models.purchase_checklist_item import PurchaseChecklistItemORM
from app.models.purchase_list import PurchaseListORM
from app.models.purchase_list_item import PurchaseListItemORM
from app.models.recipe import RecipeORM
from app.modules.projects.models.project import ProjectORM


def _required_by_product(items):
    return {item.product_id: item.required_quantity for item in items}


def test_dish_recipe_change_refreshes_all_affected_purchasing(client, db_session):
    rice = ProductORM(
        id="rice",
        name="Rice",
        category="cereal",
        unit="gram",
        package_size=900,
    )
    beans = ProductORM(
        id="beans",
        name="Beans",
        category="canned",
        unit="gram",
        package_size=400,
    )
    rice_recipe = RecipeORM(id="rice-recipe", name="Rice recipe")
    beans_recipe = RecipeORM(id="beans-recipe", name="Beans recipe")
    rice_recipe.ingredients.append(
        IngredientORM(id="rice-ingredient", product=rice, amount_per_person=100)
    )
    beans_recipe.ingredients.append(
        IngredientORM(id="beans-ingredient", product=beans, amount_per_person=50)
    )
    dish = DishORM(id="dish", name="Main dish", recipe=rice_recipe)
    project = ProjectORM(
        id=20,
        name="Trip",
        participants=10,
        days=1,
        status="prepared",
    )
    meal_plan = MealPlanORM(
        id="plan",
        project=project,
        name="Trip",
        participants=10,
        days_count=1,
    )
    day = MealPlanDayORM(id="day", meal_plan=meal_plan, day_number=1)
    slot = MealSlotORM(id="slot", day=day, meal_type="dinner")
    slot.dishes.append(
        MealSlotDishORM(id="slot-dish", dish=dish, dish_id=dish.id, order=0)
    )
    purchase_list = PurchaseListORM(
        id="purchase-list",
        project=project,
        meal_plan_id=meal_plan.id,
        status="prepared",
    )
    purchase_list.items.append(
        PurchaseListItemORM(
            id="purchase-item",
            product=rice,
            required_quantity=1000,
            required_unit="gram",
            package_size=900,
            package_unit="gram",
            packages_count=2,
        )
    )
    checklist = PurchaseChecklistORM(
        id="checklist",
        project=project,
        meal_plan_id=meal_plan.id,
        status="in_progress",
    )
    checklist.items.append(
        PurchaseChecklistItemORM(
            id="checklist-item",
            product_id=rice.id,
            required_quantity=1000,
            purchased_quantity=900,
            unit="gram",
            is_checked=True,
            note="Already bought",
        )
    )
    db_session.add_all(
        [
            rice,
            beans,
            rice_recipe,
            beans_recipe,
            dish,
            project,
            meal_plan,
            day,
            slot,
            purchase_list,
            checklist,
        ]
    )
    db_session.commit()

    response = client.put(
        "/api/v1/dishes/dish",
        json={"name": "Main dish", "recipe_id": "beans-recipe"},
    )

    assert response.status_code == 200
    db_session.expire_all()
    updated_dish = db_session.get(DishORM, "dish")
    updated_list = db_session.get(PurchaseListORM, "purchase-list")
    updated_checklist = db_session.get(PurchaseChecklistORM, "checklist")
    assert updated_dish.recipe_id == "beans-recipe"
    assert _required_by_product(updated_list.items) == {"beans": Decimal("500.00")}
    assert _required_by_product(updated_checklist.items) == {"beans": Decimal("500.00")}
