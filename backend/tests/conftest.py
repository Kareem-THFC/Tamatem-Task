"""Shared pytest fixtures for the backend test suite."""

import pytest
from flask_jwt_extended import create_access_token

from app import create_app
from app.extensions import db
from app.models import User


@pytest.fixture()
def app():
    """Provide an isolated Flask application for each test."""
    # Secrets are supplied explicitly so the suite passes on a clean checkout
    # that has no local .env file. "sqlite://" is an in-memory database, so each
    # test starts from empty tables.
    # CORS_ORIGINS is pinned for the same reason as the secrets: the allowlist
    # is read once when the extension is initialised, so it has to be supplied
    # here rather than reassigned on app.config afterwards.
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SECRET_KEY": "test-secret-that-is-at-least-32-bytes-long",
            "JWT_SECRET_KEY": "test-jwt-secret-that-is-at-least-32-bytes-long",
            "CORS_ORIGINS": ["http://localhost:3000"],
        }
    )

    with application.app_context():
        db.create_all()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def client(app):
    """Provide Flask's HTTP test client."""
    return app.test_client()


@pytest.fixture()
def user(app):
    """Persist a user for tests that need an authenticated caller."""
    with app.app_context():
        account = User(username="buyer", email="buyer@example.com")
        account.set_password("correct-password")

        db.session.add(account)
        db.session.commit()

        # The id is returned instead of the model because the object becomes
        # detached once this application context exits.
        return account.id


@pytest.fixture()
def auth_headers(app, user):
    """Return the Authorization header for the ``user`` fixture."""
    with app.app_context():
        # Signing the token directly keeps these tests focused on the endpoint
        # under test rather than re-exercising the login route.
        token = create_access_token(identity=str(user))

    return {"Authorization": f"Bearer {token}"}
