from typing import cast

from app.engines.documents.dto import GeneratedDocument
from app.engines.documents.equipment_excel import EquipmentExcelDocumentGenerator
from app.engines.documents.equipment_pdf import EquipmentPDFDocumentGenerator
from app.engines.documents.excel import ExcelDocumentGenerator
from app.engines.documents.pdf import PDFDocumentGenerator
from app.engines.documents.printer import PrintDocumentGenerator
from app.models.equipment_list import EquipmentListORM
from app.models.purchase_list import PurchaseListORM
from app.modules.projects.models.project import ProjectORM
from app.repositories.equipment_list_repository import EquipmentListRepository
from app.repositories.purchase_list_repository import PurchaseListRepository
from app.services.document_mapper import PurchaseDocumentMapper
from app.services.equipment_document_mapper import EquipmentDocumentMapper


class ProjectDocumentService:
    """Coordinates document generation for a project workflow."""

    def __init__(
        self,
        document_mapper: PurchaseDocumentMapper | None = None,
        pdf_generator: PDFDocumentGenerator | None = None,
        excel_generator: ExcelDocumentGenerator | None = None,
        print_generator: PrintDocumentGenerator | None = None,
        purchase_list_repository: PurchaseListRepository | None = None,
        equipment_document_mapper: EquipmentDocumentMapper | None = None,
        equipment_pdf_generator: EquipmentPDFDocumentGenerator | None = None,
        equipment_excel_generator: EquipmentExcelDocumentGenerator | None = None,
        equipment_list_repository: EquipmentListRepository | None = None,
    ) -> None:
        self.document_mapper = document_mapper or PurchaseDocumentMapper()
        self.pdf_generator = pdf_generator or PDFDocumentGenerator()
        self.excel_generator = excel_generator or ExcelDocumentGenerator()
        self.print_generator = print_generator or PrintDocumentGenerator()
        self.purchase_list_repository = purchase_list_repository
        self.equipment_document_mapper = (
            equipment_document_mapper or EquipmentDocumentMapper()
        )
        self.equipment_pdf_generator = (
            equipment_pdf_generator or EquipmentPDFDocumentGenerator()
        )
        self.equipment_excel_generator = (
            equipment_excel_generator or EquipmentExcelDocumentGenerator()
        )
        self.equipment_list_repository = equipment_list_repository

    def generate_purchase_pdf(self, project: ProjectORM) -> GeneratedDocument:
        purchase_list = self._get_purchase_list(project)
        return self.pdf_generator.generate(self.document_mapper.to_dto(purchase_list))

    def generate_purchase_excel(self, project: ProjectORM) -> GeneratedDocument:
        purchase_list = self._get_purchase_list(project)
        return self.excel_generator.generate(self.document_mapper.to_dto(purchase_list))

    def generate_purchase_print(self, project: ProjectORM) -> GeneratedDocument:
        purchase_list = self._get_purchase_list(project)
        return self.print_generator.generate(self.document_mapper.to_dto(purchase_list))

    def generate_equipment_pdf(self, project: ProjectORM) -> GeneratedDocument:
        equipment_list = self._get_equipment_list(project)
        dto = self.equipment_document_mapper.to_dto(equipment_list, project.name)
        return self.equipment_pdf_generator.generate(dto)

    def generate_equipment_excel(self, project: ProjectORM) -> GeneratedDocument:
        equipment_list = self._get_equipment_list(project)
        dto = self.equipment_document_mapper.to_dto(equipment_list, project.name)
        return self.equipment_excel_generator.generate(dto)

    def _get_purchase_list(self, project: ProjectORM) -> PurchaseListORM:
        purchase_lists = cast(list[PurchaseListORM], project.purchase_lists)
        if purchase_lists:
            return purchase_lists[0]

        if self.purchase_list_repository is not None:
            purchase_list = self.purchase_list_repository.get_by_project_id(project.id)
            if purchase_list is not None:
                return purchase_list

            for meal_plan in project.meal_plans:
                purchase_list = self.purchase_list_repository.get_by_meal_plan_id(
                    str(meal_plan.id)
                )
                if purchase_list is not None:
                    return purchase_list

        raise ValueError("Purchase list not found")

    def _get_equipment_list(self, project: ProjectORM) -> EquipmentListORM:
        if self.equipment_list_repository is not None:
            equipment_list = self.equipment_list_repository.get_by_project_id(project.id)
            if equipment_list is not None:
                return equipment_list
        raise ValueError("Equipment list not found")
