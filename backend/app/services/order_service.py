from flask_sqlalchemy.pagination import Pagination
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import joinedload

from app.errors.api_error import ApiError
from app.extensions import db
from app.models import Order, Product, User


def create_order(user_id: int, product_id: int) -> Order:
    """Purchase a single product, charging the buyer's gem balance."""
    user = db.session.get(User, user_id)

    if user is None:
        raise ApiError("AUTHENTICATION_REQUIRED", "Authentication is required.", 401)

    product = db.session.get(Product, product_id)

    if product is None:
        raise ApiError("PRODUCT_NOT_FOUND", "Product not found.", 404)

    already_owned = (
        db.session.query(Order.id)
        .filter_by(user_id=user.id, product_id=product.id)
        .first()
    )

    if already_owned is not None:
        raise ApiError(
            "PRODUCT_ALREADY_OWNED",
            "You already own this item. It is in your orders.",
            409,
        )

    total_price = product.price

    if user.gem_balance < total_price:
        raise ApiError(
            "INSUFFICIENT_GEM_BALANCE",
            f"This purchase costs {total_price} gems "
            f"but your balance is {user.gem_balance}.",
            409,
        )

    user.gem_balance = user.gem_balance - total_price

    order = Order(
        user_id=user.id,
        product_id=product.id,
        total_price=total_price,
        gem_balance_after=user.gem_balance,
    )

    db.session.add(order)

    try:
        db.session.commit()
    except IntegrityError as error:
        
        db.session.rollback()

        raise ApiError(
            "PRODUCT_ALREADY_OWNED",
            "You already own this item. It is in your orders.",
            409,
        ) from error

    return order


def get_order_for_user(order_id: int, user_id: int) -> Order:
    """Return one of this user's orders, or raise a 404.

    """
    order = Order.query.filter_by(id=order_id, user_id=user_id).first()

    if order is None:
        raise ApiError("ORDER_NOT_FOUND", "Order not found.", 404)

    return order


def list_orders_for_user(user_id: int, page: int, page_size: int) -> Pagination:
    """Return one page of this user's own orders, newest first.
    """
    return (
        Order.query.options(joinedload(Order.product))
        .filter_by(user_id=user_id)
        .order_by(Order.created_at.desc(), Order.id.desc())
        .paginate(page=page, per_page=page_size, error_out=False)
    )


def owned_product_ids(user_id: int, product_ids: list[int]) -> set[int]:
    """Return which of ``product_ids`` this user has already bought.
    """
    if not product_ids:
        return set()

    rows = (
        db.session.query(Order.product_id)
        .filter(Order.user_id == user_id, Order.product_id.in_(product_ids))
        .all()
    )

    return {product_id for (product_id,) in rows}
