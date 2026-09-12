"""Helpers for consistently shaped JSON API responses.

Every endpoint returns its payload through this module so the envelope the API
promises -- ``{"data": ...}`` for success, ``{"error": {...}}`` for failure --
is defined in exactly one place instead of being retyped in each route.
"""

from typing import Any, Callable

from flask import Response, jsonify
from flask_sqlalchemy.pagination import Pagination


def success_response(
    data: Any, status_code: int = 200
) -> tuple[Response, int]:
    """Return a successful payload wrapped in the API's ``data`` envelope.

    Returning a ``(body, status)`` tuple is a Flask convention: the framework
    unpacks it into a real response, which is why routes can simply return the
    result of this function.
    """
    return jsonify({"data": data}), status_code


def paginated_response(
    page: Pagination, serialize: Callable[[Any], dict] | None = None
) -> tuple[Response, int]:
    """Return one page of records alongside the metadata a client needs.
    """
    to_dict = serialize or (lambda item: item.to_dict())

    return jsonify(
        {
            "data": [to_dict(item) for item in page.items],
            "pagination": {
                "page": page.page,
                "page_size": page.per_page,
                "total": page.total,
                "pages": page.pages,
            },
        }
    ), 200


def error_response(
    code: str,
    message: str,
    status_code: int,
    details: list[dict] | None = None,
) -> tuple[Response, int]:
    """Return a JSON error response using the API's common contract.
    """
    error: dict = {"code": code, "message": message}

    if details:
        error["details"] = details

    return jsonify({"error": error}), status_code
