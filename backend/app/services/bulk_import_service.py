import csv
from collections import defaultdict
from dataclasses import dataclass
from io import StringIO
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM
from app.models.recipe_component_type import RecipeComponentType
from app.schemas.bulk_import import BulkImportIssue, BulkImportResponse

CALCULATION_TYPES = {"per_person", "fixed_group", "package_per_people"}
PRODUCT_HEADERS = {"name", "category", "unit", "package_size"}
RECIPE_HEADERS = {
    "recipe_name",
    "product_name",
    "component_type",
    "amount",
    "unit",
    "calculation_type",
    "people_count",
}


@dataclass(frozen=True)
class ProductRow:
    row: int
    name: str
    category: str | None
    unit: str
    package_size: int | None


@dataclass(frozen=True)
class RecipeComponentRow:
    row: int
    recipe_name: str
    product_name: str
    component_type: str
    amount: int
    unit: str
    calculation_type: str
    people_count: int | None


class BulkImportService:
    def __init__(self, session: Session):
        self.session = session

    def import_products(
        self,
        content: str,
        delimiter: str,
        *,
        dry_run: bool,
        skip_existing: bool,
    ) -> BulkImportResponse:
        records, header_issues = self._read_csv(content, delimiter, PRODUCT_HEADERS)
        rows: list[ProductRow] = []
        issues = list(header_issues)
        seen_names: set[str] = set()

        for row_number, record in records:
            name = record["name"].strip()
            category = record["category"].strip() or None
            unit = record["unit"].strip()
            package_size = self._positive_int(record["package_size"], row_number, "package_size", issues)

            if not name:
                issues.append(BulkImportIssue(row=row_number, message="name is required"))
            if not unit:
                issues.append(BulkImportIssue(row=row_number, message="unit is required"))
            normalized_name = name.casefold()
            if normalized_name in seen_names:
                issues.append(BulkImportIssue(row=row_number, message="duplicate product name in file"))
            seen_names.add(normalized_name)

            if name and unit and package_size is not False:
                rows.append(
                    ProductRow(
                        row=row_number,
                        name=name,
                        category=category,
                        unit=unit,
                        package_size=package_size,
                    )
                )

        existing_names = {
            name.casefold() for name in self.session.scalars(select(ProductORM.name)).all()
        }
        skipped_names = {row.name.casefold() for row in rows if row.name.casefold() in existing_names}
        if skipped_names and not skip_existing:
            for row in rows:
                if row.name.casefold() in skipped_names:
                    issues.append(BulkImportIssue(row=row.row, message="product already exists"))

        can_import = not issues
        skipped_count = len(skipped_names) if skip_existing else 0
        creatable_rows = [row for row in rows if row.name.casefold() not in skipped_names]

        if dry_run or not can_import:
            return BulkImportResponse(
                dry_run=dry_run,
                can_import=can_import,
                parsed_count=len(rows),
                created_count=0,
                skipped_count=skipped_count,
                issues=issues,
            )

        for row in creatable_rows:
            self.session.add(
                ProductORM(
                    id=str(uuid4()),
                    name=row.name,
                    category=row.category,
                    unit=row.unit,
                    package_size=row.package_size,
                )
            )
        self._commit()
        return BulkImportResponse(
            dry_run=False,
            can_import=True,
            parsed_count=len(rows),
            created_count=len(creatable_rows),
            skipped_count=skipped_count,
            issues=[],
        )

    def import_recipes(
        self,
        content: str,
        delimiter: str,
        *,
        dry_run: bool,
        skip_existing: bool,
    ) -> BulkImportResponse:
        records, header_issues = self._read_csv(content, delimiter, RECIPE_HEADERS)
        rows: list[RecipeComponentRow] = []
        issues = list(header_issues)
        component_types = {item.value for item in RecipeComponentType}

        for row_number, record in records:
            recipe_name = record["recipe_name"].strip()
            product_name = record["product_name"].strip()
            component_type = record["component_type"].strip()
            unit = record["unit"].strip()
            calculation_type = record["calculation_type"].strip()
            amount = self._positive_int(record["amount"], row_number, "amount", issues)
            people_count = self._positive_int(
                record["people_count"], row_number, "people_count", issues
            )

            if not recipe_name:
                issues.append(BulkImportIssue(row=row_number, message="recipe_name is required"))
            if not product_name:
                issues.append(BulkImportIssue(row=row_number, message="product_name is required"))
            if component_type not in component_types:
                issues.append(BulkImportIssue(row=row_number, message="unsupported component_type"))
            if not unit:
                issues.append(BulkImportIssue(row=row_number, message="unit is required"))
            if calculation_type not in CALCULATION_TYPES:
                issues.append(BulkImportIssue(row=row_number, message="unsupported calculation_type"))
            if calculation_type == "package_per_people" and not people_count:
                issues.append(
                    BulkImportIssue(
                        row=row_number,
                        message="people_count is required for package_per_people",
                    )
                )

            if (
                recipe_name
                and product_name
                and component_type in component_types
                and unit
                and calculation_type in CALCULATION_TYPES
                and amount is not False
                and people_count is not False
            ):
                rows.append(
                    RecipeComponentRow(
                        row=row_number,
                        recipe_name=recipe_name,
                        product_name=product_name,
                        component_type=component_type,
                        amount=amount,
                        unit=unit,
                        calculation_type=calculation_type,
                        people_count=people_count,
                    )
                )

        products = self.session.scalars(select(ProductORM)).all()
        products_by_name = {product.name.casefold(): product for product in products}
        for row in rows:
            if row.product_name.casefold() not in products_by_name:
                issues.append(BulkImportIssue(row=row.row, message="product not found"))

        grouped_rows: dict[str, list[RecipeComponentRow]] = defaultdict(list)
        display_names: dict[str, str] = {}
        for row in rows:
            key = row.recipe_name.casefold()
            grouped_rows[key].append(row)
            display_names[key] = row.recipe_name

        existing_names = {
            name.casefold() for name in self.session.scalars(select(RecipeORM.name)).all()
        }
        skipped_names = set(grouped_rows).intersection(existing_names)
        if skipped_names and not skip_existing:
            for key in skipped_names:
                issues.append(
                    BulkImportIssue(
                        row=grouped_rows[key][0].row,
                        message="recipe already exists",
                    )
                )

        can_import = not issues
        skipped_count = len(skipped_names) if skip_existing else 0
        creatable_names = [key for key in grouped_rows if key not in skipped_names]

        if dry_run or not can_import:
            return BulkImportResponse(
                dry_run=dry_run,
                can_import=can_import,
                parsed_count=len(grouped_rows),
                created_count=0,
                skipped_count=skipped_count,
                issues=issues,
            )

        for key in creatable_names:
            recipe_id = str(uuid4())
            self.session.add(RecipeORM(id=recipe_id, name=display_names[key]))
            for row in grouped_rows[key]:
                product = products_by_name[row.product_name.casefold()]
                self.session.add(
                    RecipeComponentORM(
                        id=str(uuid4()),
                        recipe_id=recipe_id,
                        product_id=product.id,
                        component_type=row.component_type,
                        amount=row.amount,
                        unit=row.unit,
                        calculation_type=row.calculation_type,
                        people_count=row.people_count,
                    )
                )
        self._commit()
        return BulkImportResponse(
            dry_run=False,
            can_import=True,
            parsed_count=len(grouped_rows),
            created_count=len(creatable_names),
            skipped_count=skipped_count,
            issues=[],
        )

    @staticmethod
    def _read_csv(
        content: str,
        delimiter: str,
        required_headers: set[str],
    ) -> tuple[list[tuple[int, dict[str, str]]], list[BulkImportIssue]]:
        reader = csv.DictReader(StringIO(content.lstrip("\ufeff")), delimiter=delimiter)
        headers = set(reader.fieldnames or [])
        missing_headers = required_headers - headers
        if missing_headers:
            return [], [
                BulkImportIssue(
                    row=2,
                    message=f"missing columns: {', '.join(sorted(missing_headers))}",
                )
            ]
        records = [
            (row_number, {key: value or "" for key, value in record.items()})
            for row_number, record in enumerate(reader, start=2)
        ]
        return records, []

    @staticmethod
    def _positive_int(
        raw_value: str,
        row: int,
        field: str,
        issues: list[BulkImportIssue],
    ) -> int | None | bool:
        value = raw_value.strip()
        if not value:
            return None
        try:
            parsed = int(value)
        except ValueError:
            issues.append(BulkImportIssue(row=row, message=f"{field} must be an integer"))
            return False
        if parsed <= 0:
            issues.append(BulkImportIssue(row=row, message=f"{field} must be positive"))
            return False
        return parsed

    def _commit(self) -> None:
        try:
            self.session.commit()
        except Exception:
            self.session.rollback()
            raise
