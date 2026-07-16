from app.engines.packaging import PackagedShoppingItem, PackagedShoppingResult
from app.models.meal_plan import MealPlanORM
from app.models.product import ProductORM
from app.models.purchase_list import PurchaseListORM
from app.services.meal_plan_purchasing_refresh_service import MealPlanPurchasingRefreshService


class _PurchaseListRepository:
    def __init__(self, purchase_list, product):
        self.purchase_list = purchase_list
        self.product = product

    def get_by_meal_plan_id(self, meal_plan_id):
        assert meal_plan_id == self.purchase_list.meal_plan_id
        return self.purchase_list

    def get_product_by_name(self, product_name):
        assert product_name == self.product.name
        return self.product


class _ChecklistRepository:
    def get_by_meal_plan_id(self, meal_plan_id):
        return None


class _ShoppingService:
    def calculate_packaged(self, meal_plan):
        return PackagedShoppingResult(
            items=[
                PackagedShoppingItem(
                    product_name="Рис",
                    amount=1000,
                    unit="gram",
                    package_size=400,
                    packages=3,
                )
            ]
        )


def test_refresh_preserves_purchase_list_responsible_person():
    meal_plan = MealPlanORM(id="meal-plan-72", project_id=72)
    product = ProductORM(
        id="product-rice",
        name="Рис",
        unit="gram",
        package_size=400,
    )
    purchase_list = PurchaseListORM(
        id="purchase-list-72",
        project_id=72,
        meal_plan_id=meal_plan.id,
        status="prepared",
        responsible_person="Анна Петрова",
    )

    service = MealPlanPurchasingRefreshService(
        purchase_list_repository=_PurchaseListRepository(purchase_list, product),
        checklist_repository=_ChecklistRepository(),
        shopping_service=_ShoppingService(),
    )

    service.refresh(meal_plan)

    assert purchase_list.responsible_person == "Анна Петрова"
    assert len(purchase_list.items) == 1
    assert purchase_list.items[0].product_id == product.id
    assert purchase_list.items[0].packages_count == 3
