"""Tests for centralized API error formatting."""

from app import create_app


def test_unknown_api_route_returns_the_standard_error_contract(client):
    response = client.get("/api/does-not-exist")

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "NOT_FOUND"


def test_unsupported_method_returns_the_standard_error_contract(client):
    response = client.get("/api/auth/login")

    assert response.status_code == 405
    assert response.get_json()["error"]["code"] == "METHOD_NOT_ALLOWED"


def test_unexpected_errors_return_a_generic_json_500():
    # TESTING is deliberately omitted here. The handler re-raises while testing
    # or debugging so genuine bugs stay visible, which means this behaviour can
    # only be observed on an app configured the way production would be.
    app = create_app(
        {
            "SQLALCHEMY_DATABASE_URI": "sqlite://",
            "SECRET_KEY": "test-secret-that-is-at-least-32-bytes-long",
            "JWT_SECRET_KEY": "test-jwt-secret-that-is-at-least-32-bytes-long",
        }
    )

    @app.get("/api/unexpected-failure")
    def unexpected_failure():
        raise RuntimeError("connection string that must not reach the client")

    response = app.test_client().get("/api/unexpected-failure")

    assert response.status_code == 500
    assert response.get_json() == {
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred.",
        }
    }
    assert "connection string" not in response.get_data(as_text=True)


def test_missing_required_configuration_fails_on_startup():
    try:
        create_app({"SECRET_KEY": None, "JWT_SECRET_KEY": None})
    except RuntimeError as error:
        assert "SECRET_KEY" in str(error)
        assert "JWT_SECRET_KEY" in str(error)
    else:
        raise AssertionError("create_app should refuse to start without secrets")
