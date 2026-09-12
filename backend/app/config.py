"""Configuration values loaded by the Flask application factory."""

import os
from datetime import timedelta
from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(ENV_FILE)


DEFAULT_CORS_ORIGINS = "http://localhost:3000,http://127.0.0.1:3000"


DEFAULT_ACCESS_TOKEN_HOURS = 12


class Config:
    """Default configuration shared by local development and production."""

    SECRET_KEY = os.getenv("SECRET_KEY")
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY")
    SQLALCHEMY_DATABASE_URI = os.getenv("DATABASE_URL", "sqlite:///commerce.db")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(
        hours=int(os.getenv("ACCESS_TOKEN_HOURS", DEFAULT_ACCESS_TOKEN_HOURS))
    )

    # A deployed frontend lives on a different origin than a local one, so the
    # allowlist is configuration rather than a constant. It is a list of exact
    # origins rather than "*" so that switching the token to a cookie later
    # does not require revisiting this: a wildcard is rejected by browsers as
    # soon as credentials are involved.
    CORS_ORIGINS = [
        origin.strip()
        for origin in os.getenv("CORS_ORIGINS", DEFAULT_CORS_ORIGINS).split(",")
        if origin.strip()
    ]
