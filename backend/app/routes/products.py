"""Product browsing routes."""

from flask import Blueprint, request
from flask_jwt_extended import get_jwt_identity, jwt_required
from sqlalchemy import or_

from app.errors.api_error import ApiError
from app.extensions import db
from app.models import Product
from app.schemas.product import ProductListQuery, ProductSort
from app.services.order_service import owned_product_ids
from app.utils.responses import paginated_response, success_response

products_bp = Blueprint("products", __name__)


def optional_user_id() -> int | None:
    """Return the caller's id when they sent a valid token, otherwise None.

    Used with ``@jwt_required(optional=True)``: browsing is public, so there is
    no identity to read when a request arrives without an Authorization header.
    """
    identity = get_jwt_identity()

    return int(identity) if identity is not None else None


@products_bp.get("/products")
@jwt_required(optional=True)
def list_products():
    """List products, newest CSV ids last, filtered and paginated by the database."""
    # request.args is a MultiDict that can hold repeated keys; to_dict() keeps
    # the first value of each, which is the shape the schema expects.
    query_params = ProductListQuery.model_validate(request.args.to_dict())

    query = Product.query

    if query_params.location is not None:
        query = query.filter(Product.location == query_params.location)

    if query_params.search is not None:
        query = query.filter(_search_filter(query_params.search))

    query = query.order_by(*_ordering(query_params.sort))

    
    page = query.paginate(
        page=query_params.page,
        per_page=query_params.page_size,
        error_out=False,
    )

    return paginated_response(page, serialize=_with_ownership(page.items))


@products_bp.get("/products/<int:product_id>")
@jwt_required(optional=True)
def get_product(product_id: int):
    """Return a single product, or a 404 in the shared error format."""
    product = db.session.get(Product, product_id)

    if product is None:
        raise ApiError("PRODUCT_NOT_FOUND", "Product not found.", 404)

    return success_response(_with_ownership([product])(product))


def _search_filter(term: str):
    """Match ``term`` anywhere in a product's title or description.
    """
    escaped = (
        term.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
    )
    pattern = f"%{escaped}%"
    return or_(
        Product.title.ilike(pattern, escape="\\"),
        Product.description.ilike(pattern, escape="\\"),
    )


def _ordering(sort: ProductSort) -> tuple:
    """Return the ORDER BY columns for a sort option.

    """
    if sort is ProductSort.PRICE_ASC:
        return (Product.price.asc(), Product.id.asc())

    if sort is ProductSort.PRICE_DESC:
        return (Product.price.desc(), Product.id.asc())

    return (Product.id.asc(),)


def _with_ownership(products: list[Product]):
    """Build a serialiser that adds ``owned`` to each product in ``products``.
    """
    user_id = optional_user_id()

    owned: set[int] = (
        owned_product_ids(user_id, [product.id for product in products])
        if user_id is not None
        else set()
    )

    def serialize(product: Product) -> dict:
        return {**product.to_dict(), "owned": product.id in owned}

    return serialize
