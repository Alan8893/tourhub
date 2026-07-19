from decimal import Decimal

from sqlalchemy import select

from app.models.audit_event import AuditEventORM
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


def test_meal_slot_edits_refresh_existing_purchase_data(client, db_session):
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
    rice_ingredient = IngredientORM(
        id="rice-ingredient",
        recipe=rice_recipe,
        product=rice,
        amount_per_person=100,
    )
    beans_ingredient = IngredientORM(
        id="beans-ingredient",
        recipe=beans_recipe,
        product=beans,
        amount_per_person=50,
    )
    rice_dish = DishORM(id="rice-dish", name="Rice", recipe=rice_recipe)
    beans_dish = DishORM(id="beans-dish", name="Beans", recipe=beans_recipe)
    project = ProjectORM(
        id=10,
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
    slot_dish = MealSlotDishORM(
        id="slot-dish",
        slot=slot,
        dish=rice_dish,
        dish_id=rice_dish.id,
        recipe=rice_recipe,
        recipe_id=rice_recipe.id,
        order=0,
    )
    purchase_list = PurchaseListORM(
        id="purchase-list",
        project=project,
        meal_plan_id=meal_plan.id,
        status="prepared",
    )
    purchase_list.items = [
        PurchaseListItemORM(
            id="purchase-item",
            product=rice,
            required_quantity=1000,
            required_unit="gram",
            package_size=900,
            package_unit="gram",
            packages_count=2,
        )
    ]
    checklist = PurchaseChecklistORM(
        id="checklist",
        project=project,
        meal_plan_id=meal_plan.id,
        status="in_progress",
    )
    checklist.items = [
        PurchaseChecklistItemORM(
            id="checklist-item",
            product_id=rice.id,
            required_quantity=1000,
            purchased_quantity=900,
            unit="gram",
            is_checked=True,
            note="Already bought",
        )
    ]

    db_session.add_all(
        [
            rice,
            beans,
            rice_recipe,
            beans_recipe,
            rice_ingredient,
            beans_ingredient,
            rice_dish,
            beans_dish,
            project,
            meal_plan,
            day,
            slot,
            slot_dish,
            purchase_list,
            checklist,
        ]
    )
    db_session.commit()

    replace_response = client.put(
        "/api/v1/meal-slots/slot/dishes/slot-dish/beans-dish"
    )
    assert replace_response.status_code == 200

    db_session.expire_all()
    updated_list = db_session.get(PurchaseListORM, "purchase-list")
    updated_checklist = db_session.get(PurchaseChecklistORM, "checklist")
    assert _required_by_product(updated_list.items) == {
        "beans": Decimal("500.00")
    }
    assert _required_by_product(updated_checklist.items) == {
        "beans": Decimal("500.00")
    }

    add_response = client.post("/api/v1/meal-slots/slot/dishes/rice-dish")
    assert add_response.status_code == 200
    added_slot_dish_id = add_response.json()["id"]

    db_session.expire_all()
    updated_list = db_session.get(PurchaseListORM, "purchase-list")
    updated_checklist = db_session.get(PurchaseChecklistORM, "checklist")
    assert _required_by_product(updated_list.items) == {
        "beans": Decimal("500.00"),
        "rice": Decimal("1000.00"),
    }
    assert _required_by_product(updated_checklist.items) == {
        "beans": Decimal("500.00"),
        "rice": Decimal("1000.00"),
    }

    remove_response = client.delete(
        f"/api/v1/meal-slots/slot/dishes/{added_slot_dish_id}"
    )
    assert remove_response.status_code == 200

    db_session.expire_all()
    updated_list = db_session.get(PurchaseListORM, "purchase-list")
    updated_checklist = db_session.get(PurchaseChecklistORM, "checklist")
    assert _required_by_product(updated_list.items) == {
        "beans": Decimal("500.00")
    }
    assert _required_by_product(updated_checklist.items) == {
        "beans": Decimal("500.00")
    }

    events = list(
        db_session.scalars(
            select(AuditEventORM)
            .where(AuditEventORM.entity_type == "meal_slot")
            .order_by(AuditEventORM.id)
        ).all()
    )
    assert [event.action for event in events] == [
        "meal_slot_dish_replaced",
        "meal_slot_dish_added",
        "meal_slot_dish_removed",
    ]
    assert all(event.entity_id == "slot" for event in events)
    assert all(event.actor_user_id == 1 for event in events)
    replaced, added, removed = events
    assert replaced.before_data["dishes"][0]["dish_id"] == "rice-dish"
    assert replaced.after_data["dishes"][0]["dish_id"] == "beans-dish"
    assert replaced.context_data["previous_dish_id"] == "rice-dish"
    assert replaced.context_data["dish_id"] == "beans-dish"
    assert added.before_data["dish_count"] == 1
    assert added.after_data["dish_count"] == 2
    assert added.context_data["dish_id"] == "rice-dish"
    assert removed.before_data["dish_count"] == 2
    assert removed.after_data["dish_count"] == 1
    assert removed.context_data["slot_dish_id"] == added_slot_dish_id
