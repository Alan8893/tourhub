from app.engines.documents.dto import GeneratedDocument
from app.engines.documents.excel import ExcelDocumentGenerator
from app.engines.documents.pdf import PDFDocumentGenerator
from app.engines.documents.printer import PrintDocumentGenerator
from app.services.document_mapper import PurchaseDocumentMapper
from app.modules.projects.models.project import ProjectORM


class ProjectDocumentService:
    """Coordinates document generation for a project workflow."""

    def __init__(
        self,
        document_mapper: PurchaseDocumentMapper | None = None,
        pdf_generator: PDFDocumentGenerator | None = None,
        excel_generator: ExcelDocumentGenerator | None = None,
        print_generator: PrintDocumentGenerator | None = None,
    ):
        self.document_mapper = document_mapper or PurchaseDocumentMapper()
        self.pdf_generator = pdf_generator or PDFDocumentGenerator()
        self.excel_generator = excel_generator or ExcelDocumentGenerator()
        self.print_generator = print_generator or PrintDocumentGenerator()

    def generate_purchase_pdf(
        self,
        project: ProjectORM,
    ) -> GeneratedDocument:
        purchase_list = self._get_purchase_list(project)
        dto = self.document_mapper.to_dto(purchase_list)
        return self.pdf_generator.generate(dto)

    def generate_purchase_excel(
        self,
        project: ProjectORM,
    ) -> GeneratedDocument:
        purchase_list = self._get_purchase_list(project)
        dto = self.document_mapper.to_dto(purchase_list)
        return self.excel_generator.generate(dto)

    def generate_purchase_print(
        self,
        project: ProjectORM,
    ) -> GeneratedDocument:
        purchase_list = self._get_purchase_list(project)
        dto = self.document_mapper.to_dto(purchase_list)
        return self.print_generator.generate(dto)

    def _get_purchase_list(self, project: ProjectORM):
        if not project.purchase_lists:
            raise ValueError("Purchase list not found")

        return project.purchase_lists[0]
