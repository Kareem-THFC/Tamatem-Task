"""Central registration of JSON error handlers."""

from flask import Flask, current_app
from flask_jwt_extended import JWTManager
from pydantic import ValidationError
from werkzeug.exceptions import HTTPException

from app.errors.api_error import ApiError
from app.utils.responses import error_response

HTTP_ERROR_CODES = {
    400: "BAD_REQUEST",
    401: "UNAUTHORIZED",
    403: "FORBIDDEN",
    404: "NOT_FOUND",
    405: "METHOD_NOT_ALLOWED",
    409: "CONFLICT",
    415: "UNSUPPORTED_MEDIA_TYPE",
    422: "UNPROCESSABLE_ENTITY",
}


def register_error_handlers(app: Flask) -> None:
    """Register handlers that make expected API errors consistently JSON.
    """
    app.register_error_handler(ApiError, handle_api_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(HTTPException, handle_http_exception)
    app.register_error_handler(Exception, handle_unexpected_error)


def register_jwt_error_handlers(jwt: JWTManager) -> None:
    """Configure Flask-JWT-Extended errors to use the same JSON contract."""

    @jwt.unauthorized_loader
    def handle_missing_token(_reason: str):
        return error_response(
            "AUTHENTICATION_REQUIRED", "Authentication is required.", 401
        )

    @jwt.invalid_token_loader
    def handle_invalid_token(_reason: str):
        return error_response("INVALID_TOKEN", "Token is invalid.", 401)

    @jwt.expired_token_loader
    def handle_expired_token(_jwt_header: dict, _jwt_payload: dict):
        return error_response("TOKEN_EXPIRED", "Token has expired.", 401)


def handle_api_error(error: ApiError):
    """Render expected application errors using the shared response contract."""
    return error_response(
        error.code, error.message, error.status_code, error.details
    )


def handle_validation_error(error: ValidationError):
    """Render Pydantic request-schema failures as a field-level 422 response.
    """
    details = [
        {
            "field": ".".join(str(part) for part in issue["loc"]) or "body",
            "message": issue["msg"],
        }
        for issue in error.errors()
    ]

    return error_response(
        "VALIDATION_ERROR", "Request validation failed.", 422, details
    )


def handle_http_exception(error: HTTPException):
    """Render Flask and Werkzeug HTTP errors as JSON instead of HTML."""
    code = HTTP_ERROR_CODES.get(error.code, "HTTP_ERROR")
    return error_response(code, error.description, error.code)


def handle_unexpected_error(error: Exception):
    """Render unanticipated failures as a generic 500 without leaking details."""
    # Re-raising while debugging or testing preserves Flask's interactive
    # debugger and lets a failing test report the original exception.
    if current_app.debug or current_app.testing:
        raise error

    current_app.logger.exception("Unhandled exception while handling a request")

    return error_response(
        "INTERNAL_SERVER_ERROR", "An unexpected error occurred.", 500
    )
