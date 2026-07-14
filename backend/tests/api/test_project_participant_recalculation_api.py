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


def test_update_participants_recalculates_existing_purchase_data(
    client,
    db_session,
):
    product = ProductORM(
        id="rice",
        name="Rice",
        category="cereal",
        unit="gram",
        package_size=900,
    )
    recipe = RecipeORM(id="recipe", name="Rice recipe")
    ingredient = IngredientORM(
        id="ingredient",
        recipe=recipe,
        product=product,
        amount_per_person=100,
    )
    dish = DishORM(id="dish", name="Rice", recipe=recipe)
    project = ProjectORM(
        id=1,
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
        dish=dish,
        dish_id=dish.id,
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
            product=product,
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
        status="completed",
    )
    checklist.items = [
        PurchaseChecklistItemORM(
            id="checklist-item",
            product_id=product.id,
            required_quantity=1000,
            purchased_quantity=900,
            unit="gram",
            is_checked=True,
            note="Already bought",
        )
    ]

    db_session.add_all(
        [
            product,
            recipe,
            ingredient,
            dish,
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

    response = client.patch(
        "/api/v1/projects/1/participants",
        json={"participants": 20},
    )

    assert response.status_code == 200
    assert response.json()["participants"] == 20

    db_session.expire_all()
    updated_project = db_session.get(ProjectORM, 1)
    updated_plan = db_session.get(MealPlanORM, "plan")
    updated_list = db_session.get(PurchaseListORM, "purchase-list")
    updated_checklist = db_session.get(PurchaseChecklistORM, "checklist")

    assert updated_project.participants == 20
    assert updated_plan.participants == 20
    assert len(updated_list.items) == 1
    assert updated_list.items[0].required_quantity == Decimal("2000.00")
    assert updated_list.items[0].packages_count == 3
    assert len(updated_checklist.items) == 1
    assert updated_checklist.items[0].required_quantity == Decimal("2000.00")
    assert updated_checklist.items[0].purchased_quantity == Decimal("900.00")
    assert updated_checklist.items[0].is_checked is True
    assert updated_checklist.items[0].note == "Already bought"
    assert updated_checklist.status == "completed"


def test_update_participants_rejects_invalid_value(client, db_session):
    project = ProjectORM(
        id=2,
        name="Trip",
        participants=10,
        days=1,
        status="draft",
    )
    db_session.add(project)
    db_session.commit()

    response = client.patch(
        "/api/v1/projects/2/participants",
        json={"participants": 0},
    )

    assert response.status_code == 400
    assert response.json()["error"] == "Participants must be greater than zero"
