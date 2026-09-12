"""Tests for the CSV product importer."""

import io
from decimal import Decimal
from pathlib import Path

import pytest

from app.extensions import db
from app.models import Product
from app.services.product_importer import (
    CsvFormatError,
    ImportReport,
    import_products,
)

HEADER = "id,title,description,price,location\n"
VALID_ROW = "1,Sword of Valor,A legendary sword,150,JO\n"

SUPPLIED_CSV = Path(__file__).resolve().parents[2] / "items.csv"


def run_import(app, body: str) -> ImportReport:
    """Import a CSV assembled from the standard header and ``body``."""
    with app.app_context():
        return import_products(io.StringIO(HEADER + body))


def test_import_persists_valid_rows(app):
    report = run_import(
        app,
        VALID_ROW + "2,Shield of Aegis,An indestructible shield,120.75,SA\n",
    )

    assert (report.created, report.updated, report.skipped) == (2, 0, 0)
    assert report.imported == 2
    assert report.errors == []

    with app.app_context():
        shield = db.session.get(Product, 2)

        assert shield.title == "Shield of Aegis"
        assert shield.price == Decimal("120.75")
        assert shield.location == "SA"


def test_import_accepts_a_fractional_price(app):
    """The supplied CSV contains prices such as 20.5, so this must round-trip."""
    report = run_import(app, "73,Potion of Healing,Restores health,20.5,JO\n")

    assert report.created == 1

    with app.app_context():
        # Expiring forces a reload, so the value is read back from the database
        # rather than from the object still cached in the session.
        db.session.expire_all()

        assert db.session.get(Product, 73).price == Decimal("20.50")


def test_import_normalizes_whitespace_and_location_case(app):
    run_import(app, "5,  Mystic Wand  ,  Casts spells  ,200,  jo  \n")

    with app.app_context():
        product = db.session.get(Product, 5)

        assert product.title == "Mystic Wand"
        assert product.description == "Casts spells"
        assert product.location == "JO"


@pytest.mark.parametrize(
    "row,expected_field",
    [
        ("1,Sword,A sword,,JO\n", "price"),
        ("1,Sword,A sword,free,JO\n", "price"),
        ("1,Sword,A sword,-10,JO\n", "price"),
        ("1,Sword,A sword,10.999,JO\n", "price"),
        ("1,,A sword,150,JO\n", "title"),
        ("1,Sword,,150,JO\n", "description"),
        ("1,Sword,A sword,150,\n", "location"),
        (",Sword,A sword,150,JO\n", "id"),
        ("0,Sword,A sword,150,JO\n", "id"),
        ("abc,Sword,A sword,150,JO\n", "id"),
    ],
)
def test_import_skips_invalid_rows_and_names_the_bad_field(app, row, expected_field):
    report = run_import(app, row)

    assert (report.imported, report.skipped) == (0, 1)
    assert [error.field for error in report.errors] == [expected_field]

    with app.app_context():
        assert db.session.query(Product).count() == 0


def test_one_invalid_row_does_not_prevent_the_others(app):
    report = run_import(
        app,
        VALID_ROW
        + "2,Broken Item,Has no price,,SA\n"
        + "3,Potion of Healing,Restores health,20,JO\n",
    )

    assert (report.created, report.skipped) == (2, 1)

    with app.app_context():
        assert sorted(p.id for p in db.session.query(Product).all()) == [1, 3]


def test_import_reports_the_line_number_of_each_error(app):
    report = run_import(app, VALID_ROW + "2,Broken Item,Has no price,,SA\n")

    # Line 1 is the header and line 2 is the first valid row, so the bad row is
    # reported at line 3 of the file.
    assert [(error.line_number, error.field) for error in report.errors] == [
        (3, "price")
    ]


def test_import_reports_every_invalid_field_in_a_row(app):
    report = run_import(app, "1,,A sword,not-a-price,JO\n")

    assert report.skipped == 1
    assert sorted(error.field for error in report.errors) == ["price", "title"]


def test_import_skips_a_duplicate_id_within_the_same_file(app):
    report = run_import(app, VALID_ROW + "1,Copied Sword,A duplicate,999,SA\n")

    assert (report.created, report.skipped) == (1, 1)
    assert report.errors[0].field == "id"

    with app.app_context():
        # The first occurrence wins, so the duplicate must not overwrite it.
        assert db.session.get(Product, 1).title == "Sword of Valor"


def test_import_skips_a_row_with_more_columns_than_the_header(app):
    report = run_import(app, "1,Sword,A sword,150,JO,unexpected\n")

    assert (report.imported, report.skipped) == (0, 1)
    assert report.errors[0].field == "row"


def test_import_ignores_blank_lines(app):
    report = run_import(app, "\n" + VALID_ROW + "\n")

    assert (report.created, report.skipped) == (1, 0)


def test_reimporting_updates_products_instead_of_duplicating_them(app):
    with app.app_context():
        import_products(io.StringIO(HEADER + VALID_ROW))
        report = import_products(
            io.StringIO(HEADER + "1,Sword of Valor,A sharper sword,175,SA\n")
        )

        assert (report.created, report.updated, report.skipped) == (0, 1, 0)
        assert db.session.query(Product).count() == 1

        product = db.session.get(Product, 1)

        assert product.description == "A sharper sword"
        assert product.price == Decimal("175")
        assert product.location == "SA"


def test_import_rejects_a_file_missing_required_columns(app):
    with app.app_context():
        with pytest.raises(CsvFormatError) as excinfo:
            import_products(io.StringIO("id,title,price\n1,Sword,150\n"))

    assert "description" in str(excinfo.value)
    assert "location" in str(excinfo.value)


def test_the_supplied_csv_file_imports_completely(app):
    """Guards the assumptions the importer was written against."""
    with app.app_context():
        with SUPPLIED_CSV.open(newline="", encoding="utf-8-sig") as stream:
            report = import_products(stream)

        assert (report.created, report.skipped) == (100, 0)
        assert report.errors == []
        assert db.session.query(Product).filter_by(location="JO").count() == 50
        assert db.session.query(Product).filter_by(location="SA").count() == 50
