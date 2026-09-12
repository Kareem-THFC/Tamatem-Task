"""CSV product import, kept independent of HTTP and CLI concerns.

The importer reads from any text stream rather than a path so it can be driven
by the CLI command in production and by an in-memory string in tests.
"""

import csv
from dataclasses import dataclass, field
from typing import TextIO

from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError

from app.extensions import db
from app.models import Product
from app.schemas.product import ProductRow

REQUIRED_COLUMNS = ("id", "title", "description", "price", "location")


class CsvFormatError(Exception):
    """The file itself is unusable, so no row can be imported from it."""


@dataclass(frozen=True)
class RowError:
    """One reason a single CSV row was rejected."""

    line_number: int
    field: str
    message: str


@dataclass
class ImportReport:
    """Counts and per-row errors produced by one import run."""

    created: int = 0
    updated: int = 0
    skipped: int = 0
    errors: list[RowError] = field(default_factory=list)

    @property
    def imported(self) -> int:
        return self.created + self.updated


def import_products(stream: TextIO) -> ImportReport:
    """Validate every row in ``stream`` and persist the valid products.
    """
    reader = csv.DictReader(stream)
    _require_columns(reader.fieldnames)

    report = ImportReport()
    seen_ids: set[int] = set()

    for raw_row in reader:
        line_number = reader.line_num

        if None in raw_row:
            _reject(report, line_number, "row", "Row has more columns than the header.")
            continue

        try:
            row = ProductRow.model_validate(raw_row)
        except ValidationError as error:
            report.skipped += 1
            report.errors.extend(_row_errors(line_number, error))
            continue

        if row.id in seen_ids:
            _reject(report, line_number, "id", f"Duplicate id {row.id} in this file.")
            continue

        seen_ids.add(row.id)
        _save_product(row, report)

    try:
        db.session.commit()
    except SQLAlchemyError:
        db.session.rollback()
        raise

    return report


def _require_columns(fieldnames: list[str] | None) -> None:
    """Reject a file whose header cannot describe a product at all."""
    present = set(fieldnames or ())
    missing = [column for column in REQUIRED_COLUMNS if column not in present]

    if missing:
        raise CsvFormatError(
            f"CSV is missing required columns: {', '.join(missing)}."
        )


def _reject(report: ImportReport, line_number: int, field_name: str, message: str) -> None:
    """Record a skipped row that failed a check outside the row schema."""
    report.skipped += 1
    report.errors.append(RowError(line_number, field_name, message))


def _row_errors(line_number: int, error: ValidationError) -> list[RowError]:
    """Flatten a Pydantic validation failure into one entry per bad field."""
    return [
        RowError(
            line_number,
            ".".join(str(part) for part in issue["loc"]) or "row",
            issue["msg"],
        )
        for issue in error.errors()
    ]


def _save_product(row: ProductRow, report: ImportReport) -> None:
    """Insert the product, or refresh it when its CSV id already exists.
    """
    product = db.session.get(Product, row.id)

    if product is None:
        product = Product(id=row.id)
        db.session.add(product)
        report.created += 1
    else:
        report.updated += 1

    product.title = row.title
    product.description = row.description
    product.price = row.price
    product.location = row.location
