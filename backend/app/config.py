"""Configuration values loaded by the Flask application factory."""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_FILE)


DEFAULT_CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"


DEFAULT_ACCESS_TOKEN_HOURS = 12


def _normalise_database_url(url: str) -> str:
    """Return a URL SQLAlchemy can open with the driver this project installs.

    Managed Postgres providers hand out URLs in libpq's own spelling, which
    SQLAlchemy reads as "use the default driver for this dialect" -- psycopg2,
    which is not installed here. Naming psycopg explicitly is what makes the
    same connection string work unedited whether it was copied from Neon,
    Render, or Heroku, the last of which still issues the legacy postgres://
    scheme that SQLAlchemy dropped support for outright.
    """
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql://", 1)

    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+psycopg://", 1)

    return url


class Config:
    """Default configuration shared by local development and production."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = _normalise_database_url(
        os.getenv("DATABASE_URL", "sqlite:///commerce.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # A serverless Postgres instance suspends itself when idle and the platform
    # recycles connections behind it, so a pooled connection can be dead by the
    # time it is handed out again. pre_ping spends one round trip proving the
    # connection is alive rather than surfacing a stale one as a 500 on the
    # reviewer's first request; recycling caps how long any connection is kept.
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_pre_ping": True,
        "pool_recycle": 300,
    }

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("ACCESS_TOKEN_HOURS", DEFAULT_ACCESS_TOKEN_HOURS))
    )

    # A deployed frontend lives on a different origin than a local one, so the
    # allowlist is configuration rather than a constant. It is a list of exact
    # origins rather than "*" so that switching the token to a cookie later
    # does not require revisiting this: a wildcard is rejected by browsers as
    # soon as credentials are involved.
    #
    # The deployed build is served by this same application, so it is same
    # origin and sends no CORS request at all; this matters for local work and
    # for anyone pointing a separately hosted frontend at the API.
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
        if origin.strip()
    ]
