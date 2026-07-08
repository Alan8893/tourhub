from io import BytesIO
from zipfile import ZIP_DEFLATED, ZipFile

from app.engines.documents.dto import GeneratedDocument
from app.modules.projects.models.project import ProjectORM
from app.services.project_document_service import ProjectDocumentService


class ProjectDocumentPackageService:
    """Creates a downloadable package with project documents."""

    def __init__(
        self,
        document_service: ProjectDocumentService | None = None,
    ):
        self.document_service = document_service or ProjectDocumentService()

    def generate_package(
        self,
        project: ProjectORM,
    ) -> GeneratedDocument:
        documents = [
            self.document_service.generate_purchase_pdf(project),
            self.document_service.generate_purchase_excel(project),
            self.document_service.generate_purchase_print(project),
        ]

        archive = BytesIO()

        with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
            for document in documents:
                content = document.content

                if isinstance(content, str):
                    content = content.encode("utf-8")

                zip_file.writestr(document.filename, content)

        return GeneratedDocument(
            filename=f"tourhub_project_{project.id}_documents.zip",
            content_type="application/zip",
            generated_at=documents[0].generated_at,
            content=archive.getvalue(),
        )
