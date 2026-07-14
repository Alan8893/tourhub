import csv
from dataclasses import dataclass
from io import StringIO
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import ProductORM
from app.models.recipe import RecipeORM
from app.models.recipe_component import RecipeComponentORM
from app.models.recipe_component_type import RecipeComponentType
from app.models.recipe_note import RecipeNoteORM
from app.models.recipe_note_type import RecipeNoteType
from app.schemas.catalog_import import CatalogImportError, CatalogImportResult
from app.services.recipe_command_service import CALCULATION_TYPES

PRODUCT_HEADERS = {"name", "category", "unit", "package_size"}
RECIPE_HEADERS = {
    "recipe_name",
    "product_name",
    "component_type",
    "amount",
    "unit",
    "calculation_type",
    "people_count",
    "note_type",
    "note_text",
    "note_priority",
}


@dataclass(frozen=True)
class ProductRow:
    row: int
    name: str
    category: str | None
    unit: str
    package_size: int | None


@dataclass(frozen=True)
class RecipeRow:
    row: int
    recipe_name: str
    product_name: str
    component_type: str
    amount: int
    unit: str
    calculation_type: str
    people_count: int | None
    note_type: str | None
    note_text: str | None
    note_priority: int


class CatalogImportService:
    def __init__(self, session: Session):
        self.session = session

    def preview(self, kind: str, content: str) -> CatalogImportResult:
        if kind == "products":
            rows, errors = self._parse_products(content)
            existing = self._existing_product_names()
            skipped = sum(row.name.casefold() in existing for row in rows)
            return CatalogImportResult(
                kind="products",
                valid=not errors,
                row_count=len(rows),
                create_count=len(rows) - skipped,
                skip_count=skipped,
                errors=errors,
            )

        rows, errors = self._parse_recipes(content)
        existing_recipes = self._existing_recipe_names()
        recipe_names = {row.recipe_name.casefold() for row in rows}
        for name in sorted(recipe_names & existing_recipes):
            errors.append(
                CatalogImportError(
                    row=0,
                    field="recipe_name",
                    message=f"Рецепт уже существует: {name}",
                )
            )
        product_names = self._existing_product_names()
        for row in rows:
            if row.product_name.casefold() not in product_names:
                errors.append(
                    CatalogImportError(
                        row=row.row,
                        field="product_name",
                        message=f"Продукт не найден: {row.product_name}",
                    )
                )
        note_keys = {
            (row.recipe_name.casefold(), row.note_type, row.note_text, row.note_priority)
            for row in rows
            if row.note_text
        }
        return CatalogImportResult(
            kind="recipes",
            valid=not errors,
            row_count=len(rows),
            create_count=len(recipe_names),
            skip_count=0,
            component_count=len(rows),
            note_count=len(note_keys),
            errors=errors,
        )

    def apply(self, kind: str, content: str) -> CatalogImportResult:
        preview = self.preview(kind, content)
        if not preview.valid:
            return preview

        try:
            if kind == "products":
                rows, _ = self._parse_products(content)
                existing = self._existing_product_names()
                for row in rows:
                    if row.name.casefold() in existing:
                        continue
                    self.session.add(
                        ProductORM(
                            id=str(uuid4()),
                            name=row.name,
                            category=row.category,
                            unit=row.unit,
                            package_size=row.package_size,
                        )
                    )
                self.session.commit()
                return preview

            rows, _ = self._parse_recipes(content)
            products = {
                product.name.casefold(): product
                for product in self.session.scalars(select(ProductORM)).all()
            }
            recipes: dict[str, RecipeORM] = {}
            notes: set[tuple[str, str, str, int]] = set()
            for row in rows:
                recipe_key = row.recipe_name.casefold()
                recipe = recipes.get(recipe_key)
                if recipe is None:
                    recipe = RecipeORM(id=str(uuid4()), name=row.recipe_name)
                    recipes[recipe_key] = recipe
                    self.session.add(recipe)

                product = products[row.product_name.casefold()]
                self.session.add(
                    RecipeComponentORM(
                        id=str(uuid4()),
                        recipe_id=recipe.id,
                        product_id=product.id,
                        component_type=row.component_type,
                        amount=row.amount,
                        unit=row.unit,
                        calculation_type=row.calculation_type,
                        people_count=row.people_count,
                    )
                )

                if row.note_text and row.note_type:
                    note_key = (recipe.id, row.note_type, row.note_text, row.note_priority)
                    if note_key not in notes:
                        notes.add(note_key)
                        self.session.add(
                            RecipeNoteORM(
                                id=str(uuid4()),
                                recipe_id=recipe.id,
                                type=row.note_type,
                                text=row.note_text,
                                priority=row.note_priority,
                            )
                        )
            self.session.commit()
            return preview
        except Exception:
            self.session.rollback()
            raise

    def _parse_products(self, content: str) -> tuple[list[ProductRow], list[CatalogImportError]]:
        reader, errors = self._reader(content, PRODUCT_HEADERS)
        if reader is None:
            return [], errors

        rows: list[ProductRow] = []
        names: set[str] = set()
        for row_number, raw in enumerate(reader, start=2):
            name = (raw.get("name") or "").strip()
            category = (raw.get("category") or "").strip() or None
            unit = (raw.get("unit") or "").strip()
            package_size = self._positive_int(raw.get("package_size"), row_number, "package_size", errors)
            if not name:
                errors.append(CatalogImportError(row=row_number, field="name", message="Название обязательно"))
            if not unit:
                errors.append(CatalogImportError(row=row_number, field="unit", message="Единица обязательна"))
            key = name.casefold()
            if key and key in names:
                errors.append(CatalogImportError(row=row_number, field="name", message="Дубликат продукта в файле"))
            names.add(key)
            if name and unit and package_size is not False:
                rows.append(
                    ProductRow(
                        row=row_number,
                        name=name,
                        category=category,
                        unit=unit,
                        package_size=package_size if isinstance(package_size, int) else None,
                    )
                )
        return rows, errors

    def _parse_recipes(self, content: str) -> tuple[list[RecipeRow], list[CatalogImportError]]:
        reader, errors = self._reader(content, RECIPE_HEADERS)
        if reader is None:
            return [], errors

        rows: list[RecipeRow] = []
        component_types = {item.value for item in RecipeComponentType}
        note_types = {item.value for item in RecipeNoteType}
        for row_number, raw in enumerate(reader, start=2):
            recipe_name = (raw.get("recipe_name") or "").strip()
            product_name = (raw.get("product_name") or "").strip()
            component_type = (raw.get("component_type") or "").strip()
            unit = (raw.get("unit") or "").strip()
            calculation_type = (raw.get("calculation_type") or "").strip()
            note_type = (raw.get("note_type") or "").strip() or None
            note_text = (raw.get("note_text") or "").strip() or None
            amount = self._positive_int(raw.get("amount"), row_number, "amount", errors)
            people_count = self._positive_int(raw.get("people_count"), row_number, "people_count", errors)
            note_priority = self._non_negative_int(raw.get("note_priority"), row_number, "note_priority", errors, default=100)

            required = {
                "recipe_name": recipe_name,
                "product_name": product_name,
                "component_type": component_type,
                "unit": unit,
                "calculation_type": calculation_type,
            }
            for field, value in required.items():
                if not value:
                    errors.append(CatalogImportError(row=row_number, field=field, message="Поле обязательно"))
            if component_type and component_type not in component_types:
                errors.append(CatalogImportError(row=row_number, field="component_type", message="Неизвестный тип компонента"))
            if calculation_type and calculation_type not in CALCULATION_TYPES:
                errors.append(CatalogImportError(row=row_number, field="calculation_type", message="Неизвестный способ расчёта"))
            if calculation_type == "package_per_people" and not isinstance(people_count, int):
                errors.append(CatalogImportError(row=row_number, field="people_count", message="Укажите число человек"))
            if note_text and not note_type:
                errors.append(CatalogImportError(row=row_number, field="note_type", message="Для заметки укажите тип"))
            if note_type and note_type not in note_types:
                errors.append(CatalogImportError(row=row_number, field="note_type", message="Неизвестный тип заметки"))

            if (
                all(required.values())
                and isinstance(amount, int)
                and people_count is not False
                and isinstance(note_priority, int)
                and component_type in component_types
                and calculation_type in CALCULATION_TYPES
                and (not note_type or note_type in note_types)
            ):
                rows.append(
                    RecipeRow(
                        row=row_number,
                        recipe_name=recipe_name,
                        product_name=product_name,
                        component_type=component_type,
                        amount=amount,
                        unit=unit,
                        calculation_type=calculation_type,
                        people_count=people_count if isinstance(people_count, int) else None,
                        note_type=note_type,
                        note_text=note_text,
                        note_priority=note_priority,
                    )
                )
        return rows, errors

    @staticmethod
    def _reader(
        content: str,
        expected_headers: set[str],
    ) -> tuple[csv.DictReader[str] | None, list[CatalogImportError]]:
        errors: list[CatalogImportError] = []
        text = content.lstrip("\ufeff").strip()
        if not text:
            return None, [CatalogImportError(row=1, message="Файл пуст")]
        try:
            dialect = csv.Sniffer().sniff(text[:2048], delimiters=",;")
        except csv.Error:
            dialect = csv.excel
        reader = csv.DictReader(StringIO(text), dialect=dialect)
        headers = {header.strip() for header in (reader.fieldnames or [])}
        missing = expected_headers - headers
        if missing:
            errors.append(
                CatalogImportError(
                    row=1,
                    message=f"Отсутствуют столбцы: {', '.join(sorted(missing))}",
                )
            )
            return None, errors
        return reader, errors

    @staticmethod
    def _positive_int(
        raw: str | None,
        row: int,
        field: str,
        errors: list[CatalogImportError],
    ) -> int | None | bool:
        value = (raw or "").strip()
        if not value:
            return None
        try:
            parsed = int(value)
        except ValueError:
            errors.append(CatalogImportError(row=row, field=field, message="Ожидается целое число"))
            return False
        if parsed <= 0:
            errors.append(CatalogImportError(row=row, field=field, message="Число должно быть больше нуля"))
            return False
        return parsed

    @staticmethod
    def _non_negative_int(
        raw: str | None,
        row: int,
        field: str,
        errors: list[CatalogImportError],
        default: int,
    ) -> int | bool:
        value = (raw or "").strip()
        if not value:
            return default
        try:
            parsed = int(value)
        except ValueError:
            errors.append(CatalogImportError(row=row, field=field, message="Ожидается целое число"))
            return False
        if parsed < 0:
            errors.append(CatalogImportError(row=row, field=field, message="Число не может быть отрицательным"))
            return False
        return parsed

    def _existing_product_names(self) -> set[str]:
        return {
            name.casefold()
            for name in self.session.scalars(select(ProductORM.name)).all()
        }

    def _existing_recipe_names(self) -> set[str]:
        return {
            name.casefold()
            for name in self.session.scalars(select(RecipeORM.name)).all()
        }
