from types import SimpleNamespace

from app.services.project_preparation_status_service import ProjectPreparationStatusService


class FakeMealPlanRepository:
    def __init__(self, value: object | None) -> None:
        self.value = value

    def get_by_project_id(self, project_id: int) -> object | None:
        assert project_id > 0
        return self.value


class FakePurchaseListRepository(FakeMealPlanRepository):
    pass


class FakePurchaseChecklistRepository(FakeMealPlanRepository):
    pass


class FakeEquipmentListRepository(FakeMealPlanRepository):
    pass


def test_preparation_status_returns_persisted_ids():
    service = ProjectPreparationStatusService(
        FakeMealPlanRepository(SimpleNamespace(id="meal-plan-77")),
        FakePurchaseListRepository(SimpleNamespace(id="purchase-list-77")),
        FakePurchaseChecklistRepository(SimpleNamespace(id="checklist-77")),
        FakeEquipmentListRepository(SimpleNamespace(id="equipment-list-77")),
    )

    status = service.get(77)

    assert status.project_id == 77
    assert status.meal_plan_id == "meal-plan-77"
    assert status.purchase_list_id == "purchase-list-77"
    assert status.purchase_checklist_id == "checklist-77"
    assert status.equipment_list_id == "equipment-list-77"


def test_preparation_status_uses_empty_ids_for_missing_documents():
    service = ProjectPreparationStatusService(
        FakeMealPlanRepository(None),
        FakePurchaseListRepository(None),
        FakePurchaseChecklistRepository(None),
        FakeEquipmentListRepository(None),
    )

    status = service.get(5)

    assert status.meal_plan_id == ""
    assert status.purchase_list_id == ""
    assert status.purchase_checklist_id == ""
    assert status.equipment_list_id == ""
