"""Custom commands attached to the ``flask`` command line tool."""

import os
from pathlib import Path

import click
from flask import Flask
from flask.cli import with_appcontext

from app.extensions import db
from app.models.user import DEFAULT_GEM_BALANCE, User
from app.services.product_importer import CsvFormatError, import_products

DEMO_USERNAME = "demo"
DEMO_EMAIL = "demo@example.com"
DEFAULT_DEMO_PASSWORD = "demo-password"


def register_cli_commands(app: Flask) -> None:
    """Make the project's commands available as ``flask <command>``."""
    app.cli.add_command(seed_demo_user)
    app.cli.add_command(import_products_command)


@click.command("seed-demo-user")
@with_appcontext
def seed_demo_user() -> None:
    """Create or reset the demo account used to sign in locally.
    """
    password = os.getenv("DEMO_USER_PASSWORD", DEFAULT_DEMO_PASSWORD)

    user = User.query.filter_by(username=DEMO_USERNAME).first()

    if user is None:
        user = User(username=DEMO_USERNAME, email=DEMO_EMAIL)
        action = "Created"
    else:
        action = "Updated"

    user.set_password(password)
    user.gem_balance = DEFAULT_GEM_BALANCE

    db.session.add(user)
    db.session.commit()

    click.echo(f"{action} demo user: {DEMO_USERNAME} / {DEMO_EMAIL}")
    click.echo(f"Password: {password}")
    click.echo(f"Gem balance: {user.gem_balance}")


@click.command("import-products")
@click.argument(
    "csv_path", type=click.Path(exists=True, dir_okay=False, path_type=Path)
)
@with_appcontext
def import_products_command(csv_path: Path) -> None:
    """Import products from CSV_PATH, reporting anything that was skipped."""
    with csv_path.open(newline="", encoding="utf-8-sig") as stream:
        try:
            report = import_products(stream)
        except CsvFormatError as error:
            raise click.ClickException(str(error)) from error

    click.echo(
        f"Imported {report.imported} products "
        f"({report.created} created, {report.updated} updated)."
    )
    click.echo(f"Skipped {report.skipped} rows.")

    for row_error in report.errors:
        click.echo(
            f"  line {row_error.line_number}: "
            f"{row_error.field}: {row_error.message}",
            err=True,
        )
