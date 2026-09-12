"""Tests for authenticated purchasing, gem balances and receipt retrieval."""

from datetime import datetime
from decimal import Decimal

import pytest
from flask_jwt_extended import create_access_token
from sqlalchemy.exc import IntegrityError

from app.extensions import db
from app.models import Order, Product, User

SWORD_ID = 1
POTION_ID = 2


@pytest.fixture()
def products(app):
    """Seed one whole-number price and one fractional price."""
    with app.app_context():
        db.session.add(
            Product(
                id=SWORD_ID,
                title="Sword of Valor",
                description="A legendary sword with magical powers",
                price=Decimal("150.00"),
                location="JO",
            )
        )
        db.session.add(
            Product(
                id=POTION_ID,
                title="Potion of Healing",
                description="Restores health",
                price=Decimal("20.50"),
                location="SA",
            )
        )
        db.session.commit()


def stored_orders(app) -> list[Order]:
    """Return every order currently in the database."""
    with app.app_context():
        return Order.query.all()


def stored_gem_balance(app, user_id: int) -> Decimal:
    """Return the balance the database currently holds for a user."""
    with app.app_context():
        return db.session.get(User, user_id).gem_balance


def set_gem_balance(app, user_id: int, balance: str) -> None:
    """Put a user's balance at a known amount for a boundary test."""
    with app.app_context():
        db.session.get(User, user_id).gem_balance = Decimal(balance)
        db.session.commit()


def purchase(client, auth_headers, product_id: int) -> dict:
    """Buy one product and return the receipt, failing loudly if it was refused."""
    response = client.post(
        "/api/orders", json={"product_id": product_id}, headers=auth_headers
    )

    assert response.status_code == 201, response.get_json()

    return response.get_json()["data"]


def test_purchase_creates_an_order_and_returns_a_receipt(
    app, client, auth_headers, user, products
):
    response = client.post(
        "/api/orders", json={"product_id": SWORD_ID}, headers=auth_headers
    )

    receipt = response.get_json()["data"]

    assert response.status_code == 201
    assert receipt["user_id"] == user
    assert receipt["total_price"] == "150.00"
    # Timestamps carry an explicit UTC offset, so a client cannot mistake them
    # for local time. `fromisoformat` only yields an aware datetime if one is there.
    assert datetime.fromisoformat(receipt["created_at"]).tzinfo is not None
    assert receipt["product"]["id"] == SWORD_ID
    assert receipt["product"]["title"] == "Sword of Valor"
    assert "quantity" not in receipt
    assert "unit_price" not in receipt

    with app.app_context():
        assert db.session.get(Order, receipt["id"]).total_price == Decimal("150.00")


def test_a_fractional_price_is_recorded_exactly(client, auth_headers, products):
    """20.50 must round-trip as 20.50, which float arithmetic would not guarantee."""
    response = client.post(
        "/api/orders", json={"product_id": POTION_ID}, headers=auth_headers
    )

    receipt = response.get_json()["data"]

    assert receipt["total_price"] == "20.50"


def test_a_price_submitted_by_the_client_is_ignored(app, client, auth_headers, products):
    """The charged amount must come from the database, never from the request."""
    response = client.post(
        "/api/orders",
        json={
            "product_id": SWORD_ID,
            "price": "0.01",
            "unit_price": "0.01",
            "total_price": "0.01",
        },
        headers=auth_headers,
    )

    receipt = response.get_json()["data"]

    assert response.status_code == 201
    assert receipt["total_price"] == "150.00"

    with app.app_context():
        assert db.session.get(Order, receipt["id"]).total_price == Decimal("150.00")


def test_a_quantity_submitted_by_the_client_is_ignored(app, client, auth_headers, products):
    """A purchase is one item, so a quantity in the payload must not be honoured."""
    response = client.post(
        "/api/orders", json={"product_id": SWORD_ID, "quantity": 10}, headers=auth_headers
    )

    receipt = response.get_json()["data"]

    assert response.status_code == 201
    assert receipt["total_price"] == "150.00"

    with app.app_context():
        assert db.session.get(Order, receipt["id"]).total_price == Decimal("150.00")


def test_a_later_price_change_does_not_rewrite_a_past_receipt(
    app, client, auth_headers, products
):
    """Prices are copied onto the order, so a receipt stays historically accurate."""
    order_id = client.post(
        "/api/orders", json={"product_id": SWORD_ID}, headers=auth_headers
    ).get_json()["data"]["id"]

    with app.app_context():
        db.session.get(Product, SWORD_ID).price = Decimal("999.00")
        db.session.commit()

    receipt = client.get(f"/api/orders/{order_id}", headers=auth_headers).get_json()[
        "data"
    ]

    assert receipt["total_price"] == "150.00"


def test_purchase_requires_a_token(app, client, products):
    response = client.post("/api/orders", json={"product_id": SWORD_ID})

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
    assert stored_orders(app) == []


def test_purchase_rejects_a_malformed_token(app, client, products):
    response = client.post(
        "/api/orders",
        json={"product_id": SWORD_ID},
        headers={"Authorization": "Bearer not-a-real-token"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "INVALID_TOKEN"
    assert stored_orders(app) == []


def test_purchase_rejects_a_token_for_a_deleted_user(app, client, products):
    """A signed token can outlive the account it was issued for."""
    with app.app_context():
        token = create_access_token(identity="999")

    response = client.post(
        "/api/orders",
        json={"product_id": SWORD_ID},
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "AUTHENTICATION_REQUIRED"
    assert stored_orders(app) == []


def test_purchase_rejects_an_unknown_product(app, client, auth_headers, products):
    response = client.post("/api/orders", json={"product_id": 999}, headers=auth_headers)

    assert response.status_code == 404
    assert response.get_json() == {
        "error": {"code": "PRODUCT_NOT_FOUND", "message": "Product not found."}
    }
    assert stored_orders(app) == []


@pytest.mark.parametrize(
    "payload",
    [
        {},
        {"product_id": None},
        {"product_id": "1"},
        {"product_id": 1.0},
        {"product_id": True},
        {"product_id": 0},
        {"product_id": -1},
    ],
)
def test_purchase_rejects_invalid_input(app, client, auth_headers, products, payload):
    response = client.post("/api/orders", json=payload, headers=auth_headers)

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"
    assert stored_orders(app) == []


def test_purchase_reports_the_field_that_failed_validation(
    client, auth_headers, products
):
    response = client.post("/api/orders", json={}, headers=auth_headers)

    assert response.get_json()["error"]["details"] == [
        {"field": "product_id", "message": "Field required"}
    ]


def test_purchase_rejects_a_body_that_is_not_json(app, client, auth_headers, products):
    response = client.post(
        "/api/orders", data="not-json", content_type="text/plain", headers=auth_headers
    )

    assert response.status_code == 415
    assert stored_orders(app) == []


def test_receipt_returns_the_order_for_its_owner(client, auth_headers, user, products):
    order_id = client.post(
        "/api/orders", json={"product_id": POTION_ID}, headers=auth_headers
    ).get_json()["data"]["id"]

    response = client.get(f"/api/orders/{order_id}", headers=auth_headers)

    receipt = response.get_json()["data"]

    assert response.status_code == 200
    assert receipt["id"] == order_id
    assert receipt["user_id"] == user
    assert receipt["total_price"] == "20.50"
    assert receipt["product"]["title"] == "Potion of Healing"


def test_receipt_hides_an_order_belonging_to_another_user(
    app, client, auth_headers, products
):
    """Another account order must be indistinguishable from one that does not exist."""
    order_id = client.post(
        "/api/orders", json={"product_id": SWORD_ID}, headers=auth_headers
    ).get_json()["data"]["id"]

    with app.app_context():
        other = User(username="intruder", email="intruder@example.com")
        other.set_password("correct-password")
        db.session.add(other)
        db.session.commit()

        other_token = create_access_token(identity=str(other.id))

    response = client.get(
        f"/api/orders/{order_id}", headers={"Authorization": f"Bearer {other_token}"}
    )

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "ORDER_NOT_FOUND"


def test_receipt_returns_404_for_an_unknown_order(client, auth_headers):
    response = client.get("/api/orders/999", headers=auth_headers)

    assert response.status_code == 404
    assert response.get_json()["error"]["code"] == "ORDER_NOT_FOUND"


def test_receipt_requires_a_token(client, auth_headers, products):
    order_id = client.post(
        "/api/orders", json={"product_id": SWORD_ID}, headers=auth_headers
    ).get_json()["data"]["id"]

    response = client.get(f"/api/orders/{order_id}")

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


def test_purchase_debits_the_buyers_gem_balance(
    app, client, auth_headers, user, products
):
    receipt = purchase(client, auth_headers, SWORD_ID)

    assert receipt["gem_balance_before"] == "500.00"
    assert receipt["gem_balance_after"] == "350.00"
    assert stored_gem_balance(app, user) == Decimal("350.00")


def test_successive_purchases_each_debit_the_balance(
    app, client, auth_headers, user, products
):
    """A fractional price must debit exactly, which float arithmetic would not."""
    assert purchase(client, auth_headers, SWORD_ID)["gem_balance_after"] == "350.00"
    assert purchase(client, auth_headers, POTION_ID)["gem_balance_after"] == "329.50"

    assert stored_gem_balance(app, user) == Decimal("329.50")


def test_purchase_is_refused_when_the_balance_is_too_low(
    app, client, auth_headers, user, products
):
    set_gem_balance(app, user, "149.99")

    response = client.post(
        "/api/orders", json={"product_id": SWORD_ID}, headers=auth_headers
    )

    error = response.get_json()["error"]

    assert response.status_code == 409
    assert error["code"] == "INSUFFICIENT_GEM_BALANCE"
    # The message names what the purchase costs and what the caller actually has.
    assert "150.00" in error["message"]
    assert "149.99" in error["message"]

    # A refused purchase must leave nothing behind: no order, and no debit.
    assert stored_orders(app) == []
    assert stored_gem_balance(app, user) == Decimal("149.99")


def test_purchase_succeeds_when_the_balance_exactly_covers_the_price(
    app, client, auth_headers, user, products
):
    """The check is "not enough", so a balance equal to the price must pass."""
    set_gem_balance(app, user, "150.00")

    receipt = purchase(client, auth_headers, SWORD_ID)

    assert receipt["gem_balance_after"] == "0.00"
    assert stored_gem_balance(app, user) == Decimal("0.00")


def test_a_receipt_keeps_the_balance_it_recorded_at_purchase_time(
    client, auth_headers, products
):
    """The snapshot must describe the moment of purchase, not the balance now."""
    order_id = purchase(client, auth_headers, SWORD_ID)["id"]

    purchase(client, auth_headers, POTION_ID)

    receipt = client.get(f"/api/orders/{order_id}", headers=auth_headers).get_json()[
        "data"
    ]

    assert receipt["gem_balance_before"] == "500.00"
    assert receipt["gem_balance_after"] == "350.00"


def test_order_list_returns_the_users_orders_newest_first(
    client, auth_headers, user, products
):
    first_id = purchase(client, auth_headers, SWORD_ID)["id"]
    second_id = purchase(client, auth_headers, POTION_ID)["id"]

    response = client.get("/api/orders", headers=auth_headers)

    body = response.get_json()

    assert response.status_code == 200
    assert [order["id"] for order in body["data"]] == [second_id, first_id]
    assert body["pagination"] == {
        "page": 1,
        "page_size": 20,
        "total": 2,
        "pages": 1,
    }

    newest = body["data"][0]

    assert newest["user_id"] == user
    assert newest["product"]["title"] == "Potion of Healing"
    assert newest["total_price"] == "20.50"
    assert newest["gem_balance_after"] == "329.50"


def test_order_list_paginates_at_the_database_level(app, client, auth_headers, products):
    # Three distinct products, because an account may own each one only once.
    # The third is seeded here rather than in the shared fixture so no other
    # test's expectations about the catalogue shift.
    with app.app_context():
        db.session.add(
            Product(
                id=3,
                title="Shield of Aegis",
                description="An indestructible shield",
                price=Decimal("10.00"),
                location="JO",
            )
        )
        db.session.commit()

    order_ids = [
        purchase(client, auth_headers, product_id)["id"]
        for product_id in (SWORD_ID, POTION_ID, 3)
    ]

    response = client.get("/api/orders?page=2&page_size=2", headers=auth_headers)

    body = response.get_json()

    # Newest first, so the last page holds the oldest order.
    assert [order["id"] for order in body["data"]] == [order_ids[0]]
    assert body["pagination"] == {
        "page": 2,
        "page_size": 2,
        "total": 3,
        "pages": 2,
    }


def test_order_list_returns_an_empty_page_past_the_last_one(
    client, auth_headers, products
):
    """An out-of-range page is easier for a frontend to render than a 404."""
    purchase(client, auth_headers, SWORD_ID)

    body = client.get("/api/orders?page=5", headers=auth_headers).get_json()

    assert body["data"] == []
    assert body["pagination"]["total"] == 1


def test_order_list_is_empty_for_an_account_that_has_not_bought_anything(
    client, auth_headers
):
    body = client.get("/api/orders", headers=auth_headers).get_json()

    assert body["data"] == []
    assert body["pagination"] == {
        "page": 1,
        "page_size": 20,
        "total": 0,
        "pages": 0,
    }


def test_order_list_excludes_another_users_orders(app, client, auth_headers, products):
    purchase(client, auth_headers, SWORD_ID)

    with app.app_context():
        other = User(username="intruder", email="intruder@example.com")
        other.set_password("correct-password")
        db.session.add(other)
        db.session.commit()

        other_token = create_access_token(identity=str(other.id))

    body = client.get(
        "/api/orders", headers={"Authorization": f"Bearer {other_token}"}
    ).get_json()

    assert body["data"] == []
    assert body["pagination"]["total"] == 0


def test_order_list_requires_a_token(client, products):
    response = client.get("/api/orders")

    assert response.status_code == 401
    assert response.get_json()["error"]["code"] == "AUTHENTICATION_REQUIRED"


@pytest.mark.parametrize(
    "query_string",
    ["page=0", "page=-1", "page=abc", "page_size=0", "page_size=101", "page_size=abc"],
)
def test_order_list_rejects_invalid_pagination(client, auth_headers, query_string):
    response = client.get(f"/api/orders?{query_string}", headers=auth_headers)

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_a_product_cannot_be_purchased_twice(app, client, auth_headers, user, products):
    """The whole point of the rule: a second purchase of the same item is refused."""
    purchase(client, auth_headers, SWORD_ID)

    response = client.post(
        "/api/orders", json={"product_id": SWORD_ID}, headers=auth_headers
    )

    assert response.status_code == 409
    assert response.get_json()["error"]["code"] == "PRODUCT_ALREADY_OWNED"

    # One order, and the balance was debited exactly once -- a refused repeat
    # must not charge the buyer again.
    assert len(stored_orders(app)) == 1
    assert stored_gem_balance(app, user) == Decimal("350.00")


def test_owning_one_product_does_not_block_buying_another(client, auth_headers, products):
    purchase(client, auth_headers, SWORD_ID)

    assert purchase(client, auth_headers, POTION_ID)["product"]["id"] == POTION_ID


def test_another_user_can_still_buy_an_owned_product(app, client, auth_headers, products):
    """Ownership is per account, not global: one buyer must not exhaust an item."""
    purchase(client, auth_headers, SWORD_ID)

    with app.app_context():
        other = User(username="rival", email="rival@example.com")
        other.set_password("correct-password")
        db.session.add(other)
        db.session.commit()

        other_headers = {
            "Authorization": f"Bearer {create_access_token(identity=str(other.id))}"
        }

    assert purchase(client, other_headers, SWORD_ID)["product"]["id"] == SWORD_ID


def test_the_database_refuses_a_duplicate_order_even_without_the_service_check(
    app, client, auth_headers, user, products
):
    """The uq_orders_user_product constraint is the backstop for a race.

    Two simultaneous requests could both pass the service's ownership check
    before either insert lands, so the rule is asserted at the database level
    here by writing the duplicate directly, bypassing create_order entirely.
    """
    purchase(client, auth_headers, SWORD_ID)

    with app.app_context():
        db.session.add(
            Order(
                user_id=user,
                product_id=SWORD_ID,
                total_price=Decimal("150.00"),
                gem_balance_after=Decimal("200.00"),
            )
        )

        with pytest.raises(IntegrityError):
            db.session.commit()

        db.session.rollback()
