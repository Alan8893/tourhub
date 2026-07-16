from io import BytesIO

from openpyxl import load_workbook

from app.models.equipment_list import EquipmentListORM
from app.models.equipment_list_item import EquipmentListItemORM
from app.models.meal_plan import MealPlanORM
from app.modules.projects.models.project import ProjectORM


def _seed_equipment_project(db_session, project_id: int = 76) -> None:
    project = ProjectORM(
        id=project_id,
        name="Поход на озеро",
        participants=8,
        days=2,
        status="prepared",
    )
    meal_plan = MealPlanORM(
        id=f"plan-{project_id}",
        project=project,
        name="Меню",
        participants=8,
        days_count=2,
    )
    equipment_list = EquipmentListORM(
        id=f"equipment-{project_id}",
        project=project,
        meal_plan=meal_plan,
        status="prepared",
    )
    equipment_list.items.extend(
        [
            EquipmentListItemORM(
                id=f"pot-{project_id}",
                equipment_name="Котёл",
                required_quantity=5,
                calculated_quantity=3,
                is_manual=False,
                is_removed=False,
            ),
            EquipmentListItemORM(
                id=f"lamp-{project_id}",
                equipment_name="Фонарь",
                required_quantity=2,
                calculated_quantity=None,
                is_manual=True,
                is_removed=False,
            ),
            EquipmentListItemORM(
                id=f"removed-{project_id}",
                equipment_name="Скрытая горелка",
                required_quantity=1,
                calculated_quantity=1,
                is_manual=False,
                is_removed=True,
            ),
        ]
    )
    db_session.add_all([project, meal_plan, equipment_list])
    db_session.commit()


def test_project_equipment_documents_are_downloadable(client, db_session):
    _seed_equipment_project(db_session)

    pdf = client.get("/api/v1/projects/76/documents/equipment/pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"] == "application/pdf"
    assert pdf.content.startswith(b"%PDF")
    assert "equipment_list.pdf" in pdf.headers["content-disposition"]

    excel = client.get("/api/v1/projects/76/documents/equipment/excel")
    assert excel.status_code == 200
    workbook = load_workbook(BytesIO(excel.content))
    sheet = workbook["Оборудование"]
    assert sheet["B2"].value == "Поход на озеро"
    assert [cell.value for cell in sheet[6]] == [
        "Котёл",
        5,
        3,
        "Изменено вручную",
    ]
    assert [cell.value for cell in sheet[7]] == [
        "Фонарь",
        2,
        None,
        "Добавлено вручную",
    ]
    assert sheet["A8"].value is None


def test_project_equipment_document_requires_prepared_list(client, db_session):
    project = ProjectORM(
        id=77,
        name="Неподготовленный поход",
        participants=4,
        days=1,
        status="draft",
    )
    db_session.add(project)
    db_session.commit()

    response = client.get("/api/v1/projects/77/documents/equipment/pdf")
    assert response.status_code == 409
