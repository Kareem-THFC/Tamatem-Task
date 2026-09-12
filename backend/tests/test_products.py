"""Tests for the product listing and product details endpoints."""

from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import event

from app.extensions import db
from app.models import Product


def seed_products(app, count: int = 25) -> None:
    """Create ``count`` products alternating between the two CSV locations."""
    with app.app_context():
        for number in range(1, count + 1):
            db.session.add(
                Product(
                    id=number,
                    title=f"Product {number}",
                    description=f"Description {number}",
                    price=Decimal("10.00") * number,
                    location="JO" if number % 2 else "SA",
                )
            )

        db.session.commit()


@pytest.fixture()
def products(app):
    """Seed a predictable catalogue for the listing tests."""
    seed_products(app)


def product_ids(response) -> list[int]:
    """Extract the ids returned in a listing response, in order."""
    return [product["id"] for product in response.get_json()["data"]]


def test_listing_returns_the_first_page_by_default(client, products):
    response = client.get("/api/products")

    assert response.status_code == 200
    assert response.get_json()["pagination"] == {
        "page": 1,
        "page_size": 20,
        "total": 25,
        "pages": 2,
    }
    assert product_ids(response) == list(range(1, 21))


def test_listing_serialises_a_product_completely(client, products):
    response = client.get("/api/products?page_size=1")

    product = response.get_json()["data"][0]

    assert product["id"] == 1
    assert product["title"] == "Product 1"
    assert product["description"] == "Description 1"
    # Money is exposed as a string so no precision is lost converting to a float.
    assert product["price"] == "10.00"
    assert product["location"] == "JO"
    # Timestamps carry an explicit UTC offset, so a client cannot mistake them
    # for local time. `fromisoformat` only yields an aware datetime if one is there.
    assert datetime.fromisoformat(product["created_at"]).tzinfo is not None


def test_listing_returns_the_requested_page(client, products):
    response = client.get("/api/products?page=2&page_size=10")

    assert product_ids(response) == list(range(11, 21))
    assert response.get_json()["pagination"]["pages"] == 3


def test_listing_returns_an_empty_page_past_the_last_one(client, products):
    response = client.get("/api/products?page=99")

    assert response.status_code == 200
    assert response.get_json()["data"] == []
    assert response.get_json()["pagination"]["total"] == 25


def test_listing_filters_by_location(client, products):
    response = client.get("/api/products?location=SA")

    locations = {product["location"] for product in response.get_json()["data"]}

    assert locations == {"SA"}
    assert response.get_json()["pagination"]["total"] == 12


def test_location_filter_ignores_casing_and_surrounding_space(client, products):
    response = client.get("/api/products?location=+jo+")

    assert response.get_json()["pagination"]["total"] == 13


def test_an_unknown_location_returns_an_empty_result(client, products):
    response = client.get("/api/products?location=XX")

    assert response.status_code == 200
    assert response.get_json()["data"] == []
    assert response.get_json()["pagination"] == {
        "page": 1,
        "page_size": 20,
        "total": 0,
        "pages": 0,
    }


def test_a_blank_location_lists_every_product(client, products):
    response = client.get("/api/products?location=")

    assert response.get_json()["pagination"]["total"] == 25


def test_location_and_pagination_apply_together(client, products):
    response = client.get("/api/products?location=JO&page=2&page_size=5")

    assert product_ids(response) == [11, 13, 15, 17, 19]
    assert response.get_json()["pagination"]["total"] == 13


@pytest.mark.parametrize(
    "query_string",
    [
        "page=0",
        "page=-1",
        "page=abc",
        "page=1.5",
        "page_size=0",
        "page_size=101",
        "page_size=many",
        "location=" + "A" * 11,
    ],
)
def test_listing_rejects_invalid_query_parameters(client, query_string):
    response = client.get(f"/api/products?{query_string}")

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_listing_accepts_the_maximum_page_size(client, products):
    """The largest allowed page size is served rather than silently reduced.

    The bound is enforced only by ProductListQuery, so this pins the accepted
    edge of that single check next to the tests for the rejected values.
    """
    response = client.get("/api/products?page_size=100")

    assert response.status_code == 200
    assert response.get_json()["pagination"]["page_size"] == 100
    assert len(response.get_json()["data"]) == 25


def test_listing_reports_the_query_parameter_that_failed(client):
    response = client.get("/api/products?page=0")

    assert response.get_json()["error"]["details"] == [
        {"field": "page", "message": "Input should be greater than or equal to 1"}
    ]


def test_pagination_happens_in_the_database(app, client, products):
    """Only the requested page may be selected, never the whole table.

    The listener records every statement the request runs, which is how the
    test can assert that the database applied the limit rather than the route
    slicing a fully loaded list.
    """
    statements = []

    def record(_conn, _cursor, statement, *_args):
        statements.append(statement)

    with app.app_context():
        engine = db.engine

    event.listen(engine, "before_cursor_execute", record)
    try:
        client.get("/api/products?page=2&page_size=5")
    finally:
        event.remove(engine, "before_cursor_execute", record)

    selects = [
        statement for statement in statements if statement.lstrip().upper().startswith("SELECT")
    ]

    assert any("LIMIT" in statement.upper() for statement in selects)
    assert all(
        "COUNT" in statement.upper() or "LIMIT" in statement.upper()
        for statement in selects
    )


def test_product_details_returns_the_product(client, products):
    response = client.get("/api/products/3")

    assert response.status_code == 200
    assert response.get_json()["data"]["title"] == "Product 3"


def test_product_details_returns_404_for_an_unknown_id(client, products):
    response = client.get("/api/products/999")

    assert response.status_code == 404
    assert response.get_json() == {
        "error": {"code": "PRODUCT_NOT_FOUND", "message": "Product not found."}
    }


@pytest.mark.parametrize("product_id", ["abc", "1.5", "-1"])
def test_product_details_rejects_a_non_integer_id(client, product_id):
    """Flask's <int:...> converter refuses to match, so no route is found."""
    response = client.get(f"/api/products/{product_id}")

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "NOT_FOUND"


# ---- Ownership flag -------------------------------------------------------
#
# Browsing stays public, but a signed-in caller is also told which items they
# already own so the storefront can mark them. The flag is always present, so a
# client never has to branch on whether the key exists.


def test_products_are_not_owned_for_an_anonymous_caller(client, products):
    listed = client.get("/api/products").get_json()["data"]

    assert all(product["owned"] is False for product in listed)


def test_product_details_are_not_owned_for_an_anonymous_caller(client, products):
    assert client.get("/api/products/1").get_json()["data"]["owned"] is False


def test_listing_marks_only_the_products_the_caller_owns(client, auth_headers, products):
    client.post("/api/orders", json={"product_id": 3}, headers=auth_headers)

    listed = client.get("/api/products", headers=auth_headers).get_json()["data"]
    owned = {product["id"] for product in listed if product["owned"]}

    assert owned == {3}


def test_product_details_report_ownership(client, auth_headers, products):
    client.post("/api/orders", json={"product_id": 3}, headers=auth_headers)

    assert client.get("/api/products/3", headers=auth_headers).get_json()["data"]["owned"] is True
    assert client.get("/api/products/4", headers=auth_headers).get_json()["data"]["owned"] is False


def test_ownership_is_not_leaked_between_users(app, client, auth_headers, products):
    """One account's purchases must not mark another account's listing."""
    from flask_jwt_extended import create_access_token

    from app.models import User

    client.post("/api/orders", json={"product_id": 3}, headers=auth_headers)

    with app.app_context():
        other = User(username="stranger", email="stranger@example.com")
        other.set_password("correct-password")
        db.session.add(other)
        db.session.commit()

        other_headers = {
            "Authorization": f"Bearer {create_access_token(identity=str(other.id))}"
        }

    listed = client.get("/api/products", headers=other_headers).get_json()["data"]

    assert all(product["owned"] is False for product in listed)


def test_listing_resolves_ownership_in_a_single_query(app, client, auth_headers, products):
    """Ownership is looked up once per page, not once per product.

    Counting SELECTs is the only way to assert this: a per-product lookup would
    return identical JSON while issuing twenty extra queries.
    """
    client.post("/api/orders", json={"product_id": 3}, headers=auth_headers)

    statements = []

    def record(_conn, _cursor, statement, *_args):
        if statement.lstrip().upper().startswith("SELECT"):
            statements.append(statement)

    # db.engine resolves through the current application, so it has to be read
    # inside a context -- matching test_pagination_happens_in_the_database.
    with app.app_context():
        engine = db.engine

    event.listen(engine, "before_cursor_execute", record)
    try:
        client.get("/api/products?page_size=20", headers=auth_headers)
    finally:
        event.remove(engine, "before_cursor_execute", record)

    # A COUNT for the pagination, the page of products, and one ownership
    # lookup. Anything materially larger means a query per product crept in.
    assert len(statements) <= 4, statements


# ---- Search ---------------------------------------------------------------


@pytest.fixture()
def searchable(app):
    """Products with distinct words in the title and in the description."""
    with app.app_context():
        db.session.add_all(
            [
                Product(
                    id=1,
                    title="Sword of Valor",
                    description="A legendary blade",
                    price=Decimal("150.00"),
                    location="JO",
                ),
                Product(
                    id=2,
                    title="Potion of Healing",
                    description="Restores health completely",
                    price=Decimal("20.00"),
                    location="SA",
                ),
                Product(
                    id=3,
                    title="Shield of Aegis",
                    description="Blocks a legendary amount of damage",
                    price=Decimal("120.00"),
                    location="JO",
                ),
                Product(
                    id=4,
                    title="100% Luck Charm",
                    description="A charm with an odd_name",
                    price=Decimal("50.00"),
                    location="SA",
                ),
            ]
        )
        db.session.commit()


def search_ids(client, term: str, **params) -> list[int]:
    """Return the ids a search returns, in the order the API returned them."""
    query = "".join(f"&{key}={value}" for key, value in params.items())
    body = client.get(f"/api/products?search={term}{query}").get_json()

    return [product["id"] for product in body["data"]]


def test_search_matches_the_title(client, searchable):
    assert search_ids(client, "sword") == [1]


def test_search_is_case_insensitive(client, searchable):
    assert search_ids(client, "SWORD") == [1]
    assert search_ids(client, "sWoRd") == [1]


def test_search_matches_part_of_a_word(client, searchable):
    assert search_ids(client, "heal") == [2]


def test_search_also_matches_the_description(client, searchable):
    """"legendary" is in one title's description and another's, not its title."""
    assert search_ids(client, "legendary") == [1, 3]


def test_search_returns_an_empty_page_when_nothing_matches(client, searchable):
    body = client.get("/api/products?search=nothingmatchesthis").get_json()

    assert body["data"] == []
    assert body["pagination"]["total"] == 0


def test_blank_search_lists_everything(client, searchable):
    """An emptied search box sends the parameter with no value."""
    assert search_ids(client, "") == [1, 2, 3, 4]


def test_search_is_combined_with_the_location_filter(client, searchable):
    """The two filters narrow together rather than replacing one another."""
    assert search_ids(client, "of", location="JO") == [1, 3]


def test_a_percent_sign_is_matched_literally(client, searchable):
    """Unescaped, "%" is a LIKE wildcard and would match every product."""
    assert search_ids(client, "100%") == [4]


def test_an_underscore_is_matched_literally(client, searchable):
    """Unescaped, "_" is a LIKE wildcard matching any single character."""
    assert search_ids(client, "odd_name") == [4]
    # The wildcard meaning would make this match "odd_name" too.
    assert search_ids(client, "oddxname") == []


def test_search_is_rejected_when_too_long(client, searchable):
    response = client.get(f"/api/products?search={'x' * 101}")

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


# ---- Sorting --------------------------------------------------------------


def sorted_prices(client, sort: str) -> list[str]:
    body = client.get(f"/api/products?sort={sort}&page_size=100").get_json()

    return [product["price"] for product in body["data"]]


def test_default_sort_is_by_id(client, searchable):
    assert search_ids(client, "") == [1, 2, 3, 4]


def test_sort_by_price_ascending(client, searchable):
    assert sorted_prices(client, "price_asc") == ["20.00", "50.00", "120.00", "150.00"]


def test_sort_by_price_descending(client, searchable):
    assert sorted_prices(client, "price_desc") == ["150.00", "120.00", "50.00", "20.00"]


def test_an_unknown_sort_is_rejected(client, searchable):
    response = client.get("/api/products?sort=price")

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.get_json()["error"]["details"][0]["field"] == "sort"


def test_sorting_is_stable_across_pages_when_prices_tie(app, client):
    """A tied ORDER BY is free to reorder rows, which breaks pagination.

    Every product here costs the same, so only the id tie-break keeps a product
    from appearing on two pages or on none.
    """
    with app.app_context():
        for number in range(1, 11):
            db.session.add(
                Product(
                    id=number,
                    title=f"Tied {number}",
                    description="Same price as every other",
                    price=Decimal("10.00"),
                    location="JO",
                )
            )
        db.session.commit()

    seen = []
    for page in (1, 2):
        body = client.get(
            f"/api/products?sort=price_asc&page={page}&page_size=5"
        ).get_json()
        seen.extend(product["id"] for product in body["data"])

    assert seen == list(range(1, 11))


def test_sorting_happens_in_the_database(app, client, searchable):
    """The ORDER BY has to reach SQL, not be applied to a loaded page."""
    statements = []

    def record(_conn, _cursor, statement, *_args):
        statements.append(statement)

    with app.app_context():
        engine = db.engine

    event.listen(engine, "before_cursor_execute", record)
    try:
        client.get("/api/products?sort=price_desc&page_size=2")
    finally:
        event.remove(engine, "before_cursor_execute", record)

    selects = [s for s in statements if s.lstrip().upper().startswith("SELECT")]

    assert any("ORDER BY" in s.upper() and "LIMIT" in s.upper() for s in selects)
