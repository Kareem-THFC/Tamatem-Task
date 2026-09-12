"""Tests for registration and JWT login authentication."""

from decimal import Decimal

import pytest
from flask_jwt_extended import decode_token

from app.extensions import db
from app.models import User


def stored_users(app) -> list[tuple[str, str]]:
    """Return every account as (username, email), oldest first."""
    with app.app_context():
        return [
            (account.username, account.email)
            for account in User.query.order_by(User.id).all()
        ]


VALID_SIGNUP = {
    "username": "new-player",
    "email": "new.player@example.com",
    "password": "a-good-password",
}


def create_user(app, password="correct-password"):
    """Persist a user with a real password hash for authentication tests."""
    with app.app_context():
        user = User(username="demo-user", email="demo@example.com")
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        return user.id, user.password_hash


@pytest.mark.parametrize("identifier", ["demo-user", "demo@example.com"])
def test_login_returns_a_jwt_for_valid_credentials(app, client, identifier):
    user_id, password_hash = create_user(app)

    response = client.post(
        "/api/auth/login",
        json={"identifier": identifier, "password": "correct-password"},
    )

    response_data = response.get_json()["data"]

    assert response.status_code == 200
    assert password_hash != "correct-password"
    assert response_data["user"] == {
        "id": user_id,
        "username": "demo-user",
        "email": "demo@example.com",
        "gem_balance": "500.00",
    }

    with app.app_context():
        assert decode_token(response_data["access_token"])["sub"] == str(user_id)


def test_login_rejects_a_missing_identifier(client):
    response = client.post("/api/auth/login", json={"password": "correct-password"})

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_rejects_a_missing_password(client):
    response = client.post("/api/auth/login", json={"identifier": "demo-user"})

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize("identifier", ["", "   "])
def test_login_rejects_a_blank_identifier(client, identifier):
    response = client.post(
        "/api/auth/login",
        json={"identifier": identifier, "password": "correct-password"},
    )

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_rejects_non_string_fields(client):
    response = client.post(
        "/api/auth/login", json={"identifier": 1, "password": "correct-password"}
    )

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


@pytest.mark.parametrize(
    "payload",
    [
        {"identifier": "a" * 256, "password": "correct-password"},
        {"identifier": "demo-user", "password": "a" * 129},
    ],
)
def test_login_rejects_fields_that_exceed_maximum_length(client, payload):
    response = client.post("/api/auth/login", json=payload)

    assert response.status_code == 422
    assert response.get_json()["error"]["code"] == "VALIDATION_ERROR"


def test_login_rejects_a_body_that_is_not_json(client):
    response = client.post("/api/auth/login", data="not-json", content_type="text/plain")

    assert response.status_code == 415
    assert response.get_json()["error"]["code"] == "UNSUPPORTED_MEDIA_TYPE"


def test_login_rejects_malformed_json(client):
    response = client.post(
        "/api/auth/login", data="{not valid json", content_type="application/json"
    )

    assert response.status_code == 400
    assert response.get_json()["error"]["code"] == "BAD_REQUEST"


def test_login_reports_the_field_that_failed_validation(client):
    response = client.post("/api/auth/login", json={"password": "correct-password"})

    assert response.get_json()["error"]["details"] == [
        {"field": "identifier", "message": "Field required"}
    ]


@pytest.mark.parametrize(
    "identifier,password",
    [
        ("demo@example.com", "wrong-password"),
        ("missing@example.com", "correct-password"),
    ],
)
def test_login_rejects_invalid_credentials(app, client, identifier, password):
    create_user(app)

    response = client.post(
        "/api/auth/login",
        json={"identifier": identifier, "password": password},
    )

    assert response.status_code == 401
    assert response.get_json() == {
        "error": {
            "code": "INVALID_CREDENTIALS",
            "message": "Invalid identifier or password.",
        }
    }


def test_register_creates_an_account_and_returns_a_usable_token(app, client):
    response = client.post("/api/auth/register", json=VALID_SIGNUP)

    response_data = response.get_json()["data"]

    assert response.status_code == 201
    assert response_data["user"]["username"] == "new-player"
    assert response_data["user"]["email"] == "new.player@example.com"

    # The starting balance comes from the column default, so signing up is all
    # it takes to be able to buy something.
    assert response_data["user"]["gem_balance"] == "500.00"

    with app.app_context():
        account = User.query.filter_by(username="new-player").one()

        assert decode_token(response_data["access_token"])["sub"] == str(account.id)
        assert response_data["user"]["id"] == account.id


def test_register_stores_a_hash_rather_than_the_password(app, client):
    client.post("/api/auth/register", json=VALID_SIGNUP)

    with app.app_context():
        stored_hash = User.query.filter_by(username="new-player").one().password_hash

    assert stored_hash != VALID_SIGNUP["password"]
    assert VALID_SIGNUP["password"] not in stored_hash


def test_a_registered_user_can_then_log_in(client):
    client.post("/api/auth/register", json=VALID_SIGNUP)

    response = client.post(
        "/api/auth/login",
        json={
            "identifier": VALID_SIGNUP["username"],
            "password": VALID_SIGNUP["password"],
        },
    )

    assert response.status_code == 200
    assert response.get_json()["data"]["access_token"]


def test_register_normalises_the_email_and_login_still_matches(app, client):
    """A mailbox is the same mailbox whatever the capitalisation."""
    response = client.post(
        "/api/auth/register",
        json={**VALID_SIGNUP, "email": "  New.Player@Example.COM  "},
    )

    assert response.get_json()["data"]["user"]["email"] == "new.player@example.com"
    assert stored_users(app) == [("new-player", "new.player@example.com")]

    # Logging in with the capitalisation originally typed must still work.
    login = client.post(
        "/api/auth/login",
        json={
            "identifier": "New.Player@Example.COM",
            "password": VALID_SIGNUP["password"],
        },
    )

    assert login.status_code == 200


def test_register_rejects_a_username_already_taken(app, client):
    client.post("/api/auth/register", json=VALID_SIGNUP)

    response = client.post(
        "/api/auth/register",
        json={**VALID_SIGNUP, "email": "someone.else@example.com"},
    )

    error = response.get_json()["error"]

    assert response.status_code == 409
    assert error["code"] == "USER_ALREADY_EXISTS"
    assert "username" in error["message"]
    assert len(stored_users(app)) == 1


def test_register_rejects_a_username_already_taken_in_another_case(app, client):
    """A name is the same name whatever the capitalisation."""
    client.post("/api/auth/register", json=VALID_SIGNUP)

    response = client.post(
        "/api/auth/register",
        json={
            **VALID_SIGNUP,
            "username": "New-Player",
            "email": "someone.else@example.com",
        },
    )

    error = response.get_json()["error"]

    assert response.status_code == 409
    assert error["code"] == "USER_ALREADY_EXISTS"
    assert "username" in error["message"]
    assert len(stored_users(app)) == 1


def test_register_names_the_clashing_field_for_a_taken_username(client):
    """The 409 carries the field so a client can show it under that input."""
    client.post("/api/auth/register", json=VALID_SIGNUP)

    response = client.post(
        "/api/auth/register",
        json={**VALID_SIGNUP, "email": "someone.else@example.com"},
    )

    error = response.get_json()["error"]

    assert error["details"] == [
        {"field": "username", "message": error["message"]}
    ]


def test_register_names_the_clashing_field_for_a_taken_email(client):
    client.post("/api/auth/register", json=VALID_SIGNUP)

    response = client.post(
        "/api/auth/register",
        json={**VALID_SIGNUP, "username": "someone-else"},
    )

    error = response.get_json()["error"]

    assert error["details"] == [{"field": "email", "message": error["message"]}]


def test_rejected_login_names_no_field(client):
    """Naming one would say which half of the pair was wrong."""
    create_user(client.application)

    response = client.post(
        "/api/auth/login",
        json={"identifier": "demo-user", "password": "wrong-password"},
    )

    assert "details" not in response.get_json()["error"]


def test_register_keeps_the_username_as_typed(app, client):
    """Only the comparison folds case: the name is stored as it was given."""
    response = client.post(
        "/api/auth/register", json={**VALID_SIGNUP, "username": "New-Player"}
    )

    assert response.get_json()["data"]["user"]["username"] == "New-Player"
    assert stored_users(app) == [("New-Player", "new.player@example.com")]


@pytest.mark.parametrize("identifier", ["DEMO-USER", "Demo-User"])
def test_login_matches_a_username_in_any_case(app, client, identifier):
    create_user(app)

    response = client.post(
        "/api/auth/login",
        json={"identifier": identifier, "password": "correct-password"},
    )

    assert response.status_code == 200


def test_register_rejects_an_email_already_taken_in_another_case(app, client):
    """Normalisation is what makes the duplicate detectable at all."""
    client.post("/api/auth/register", json=VALID_SIGNUP)

    response = client.post(
        "/api/auth/register",
        json={
            **VALID_SIGNUP,
            "username": "someone-else",
            "email": "New.Player@EXAMPLE.com",
        },
    )

    error = response.get_json()["error"]

    assert response.status_code == 409
    assert error["code"] == "USER_ALREADY_EXISTS"
    assert "email" in error["message"]
    assert len(stored_users(app)) == 1


def test_register_ignores_a_gem_balance_supplied_by_the_client(app, client):
    """The starting balance is not a field the request model parses."""
    response = client.post(
        "/api/auth/register", json={**VALID_SIGNUP, "gem_balance": "999999.00"}
    )

    assert response.status_code == 201
    assert response.get_json()["data"]["user"]["gem_balance"] == "500.00"

    with app.app_context():
        account = User.query.filter_by(username="new-player").one()

        assert account.gem_balance == Decimal("500.00")


@pytest.mark.parametrize(
    ("payload", "invalid_field"),
    [
        ({**VALID_SIGNUP, "username": None}, "username"),
        ({**VALID_SIGNUP, "username": "ab"}, "username"),
        ({**VALID_SIGNUP, "username": "a" * 81}, "username"),
        ({**VALID_SIGNUP, "username": "   "}, "username"),
        # An "@" in a username would be ambiguous with an email at login.
        ({**VALID_SIGNUP, "username": "looks@like.email"}, "username"),
        ({**VALID_SIGNUP, "username": "has a space"}, "username"),
        ({**VALID_SIGNUP, "username": 123}, "username"),
        ({**VALID_SIGNUP, "email": "not-an-email"}, "email"),
        ({**VALID_SIGNUP, "email": "missing-domain@"}, "email"),
        ({**VALID_SIGNUP, "email": None}, "email"),
        ({**VALID_SIGNUP, "password": "short12"}, "password"),
        ({**VALID_SIGNUP, "password": "a" * 129}, "password"),
        ({**VALID_SIGNUP, "password": 12345678}, "password"),
        ({**VALID_SIGNUP, "password": None}, "password"),
    ],
)
def test_register_rejects_invalid_input(app, client, payload, invalid_field):
    response = client.post("/api/auth/register", json=payload)

    error = response.get_json()["error"]

    assert response.status_code == 422
    assert error["code"] == "VALIDATION_ERROR"
    assert [detail["field"] for detail in error["details"]] == [invalid_field]
    assert stored_users(app) == []


def test_register_reports_every_missing_field_at_once(app, client):
    """One request should tell the signup form everything that is wrong."""
    response = client.post("/api/auth/register", json={})

    error = response.get_json()["error"]

    assert response.status_code == 422
    assert [detail["field"] for detail in error["details"]] == [
        "username",
        "email",
        "password",
    ]
    assert all(detail["message"] == "Field required" for detail in error["details"])
    assert stored_users(app) == []


def test_register_rejects_a_body_that_is_not_json(app, client):
    response = client.post(
        "/api/auth/register", data="not-json", content_type="text/plain"
    )

    assert response.status_code == 415
    assert stored_users(app) == []
