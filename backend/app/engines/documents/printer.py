from datetime import UTC, datetime

from app.engines.documents.branding import ClubBrandingDTO
from app.engines.documents.dto import GeneratedDocument, PurchaseDocumentDTO


class PrintDocumentGenerator:
    """Generate printable text representation."""

    def generate(
        self,
        document: PurchaseDocumentDTO,
        branding: ClubBrandingDTO | None = None,
    ) -> GeneratedDocument:
        lines = [document.title, ""]
        if branding is not None:
            lines = [branding.club_name, *branding.contact_lines, "", document.title, ""]

        for item in document.items:
            package_text = ""
            if item.packages_count:
                package_text = f" (packages: {item.packages_count}"
                if item.package_size:
                    package_text += f" x {item.package_size}"
                package_text += ")"

            lines.append(
                f"{item.product_name}: {item.quantity} {item.unit}{package_text}"
            )

        if branding is not None:
            lines.extend(
                [
                    "",
                    branding.footer_text
                    or f"Сформировано для {branding.club_name} в TourHub",
                ]
            )

        return GeneratedDocument(
            filename="purchase_list.txt",
            content_type="text/plain",
            generated_at=datetime.now(UTC),
            content="\n".join(lines),
        )
