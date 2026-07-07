from io import BytesIO
from zipfile import ZipFile


 def test_purchase_list_pdf_export_not_found(client):
    response = client.get(
        "/purchase-lists/missing/export/pdf"
    )

    assert response.status_code == 404


 def test_purchase_list_excel_export_not_found(client):
    response = client.get(
        "/purchase-lists/missing/export/excel"
    )

    assert response.status_code == 404


def test_excel_content_is_xlsx_archive():
    content = BytesIO(b"PK")

    assert content.read(2) == b"PK"
