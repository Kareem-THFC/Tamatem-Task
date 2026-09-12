"""Purchase and receipt routes."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required

from app.schemas.order import CreateOrderRequest
from app.schemas.pagination import PaginationQuery
from app.services.order_service import (
    create_order,
    get_order_for_user,
    list_orders_for_user,
)
from app.utils.responses import paginated_response, success_response

orders_bp = Blueprint("orders", __name__)


def current_user_id() -> int:
    """Return the authenticated user's id from the verified token.

    Flask-JWT-Extended requires the token subject to be a string, so the login
    route stores ``str(user.id)`` and it is converted back here.
    """
    return int(get_jwt_identity())


@orders_bp.post("/orders")
@jwt_required()
def create_order_route():
    """Purchase a single product and return the resulting receipt."""
    order_request = CreateOrderRequest.model_validate(request.get_json())

    order = create_order(
        user_id=current_user_id(), product_id=order_request.product_id
    )

    return success_response(order.to_dict(), 201)


@orders_bp.get("/orders")
@jwt_required()
def list_orders_route():
    """List the authenticated user's own orders, newest first."""
    query_params = PaginationQuery.model_validate(request.args.to_dict())

    page = list_orders_for_user(
        user_id=current_user_id(),
        page=query_params.page,
        page_size=query_params.page_size,
    )

    return paginated_response(page)


@orders_bp.get("/orders/<int:order_id>")
@jwt_required()
def get_order_route(order_id: int):
    """Return one of the authenticated user's orders as a receipt."""
    order = get_order_for_user(order_id, current_user_id())

    return success_response(order.to_dict())
