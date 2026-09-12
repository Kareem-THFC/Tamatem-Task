"""Tests for the cross-origin headers the browser-based frontend depends on.

These assert on response headers rather than bodies. A missing CORS header does
not fail the request server-side -- the endpoint runs and answers 200 -- it
makes the browser throw the response away, which is why it is worth a test
rather than being left to be noticed in a browser console.
"""

# The allowlist the conftest app fixture is configured with. It has to be set
# when the app is created, because Flask-Cors reads it once at init_app time --
# reassigning app.config["CORS_ORIGINS"] afterwards has no effect.
ALLOWED_ORIGIN = "http://localhost:3000"
DISALLOWED_ORIGIN = "http://evil.example.com"


def test_a_preflight_from_the_frontend_is_answered(client):
    """The browser sends OPTIONS before a JSON POST and needs a 2xx with headers."""
    response = client.options(
        "/api/auth/login",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type",
        },
    )

    assert response.status_code < 400
    assert response.headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN
    assert "POST" in response.headers["Access-Control-Allow-Methods"]


def test_a_preflight_allows_the_authorization_header(client):
    """Without this the frontend could not send the token on protected routes."""
    response = client.options(
        "/api/orders",
        headers={
            "Origin": ALLOWED_ORIGIN,
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "authorization,content-type",
        },
    )

    allowed = response.headers["Access-Control-Allow-Headers"].lower()

    assert "authorization" in allowed
    assert "content-type" in allowed


def test_a_successful_response_carries_the_allow_origin_header(client):
    response = client.get("/api/products", headers={"Origin": ALLOWED_ORIGIN})

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN


def test_an_error_response_also_carries_the_allow_origin_header(client):
    """A 401 the browser cannot read is an error the frontend cannot display."""
    response = client.post(
        "/api/orders", json={"product_id": 1}, headers={"Origin": ALLOWED_ORIGIN}
    )

    assert response.status_code == 401
    assert response.headers["Access-Control-Allow-Origin"] == ALLOWED_ORIGIN


def test_an_origin_outside_the_allowlist_is_not_granted_access(client):
    response = client.get("/api/products", headers={"Origin": DISALLOWED_ORIGIN})

    # The request still succeeds server-side; it is the absent header that
    # makes the browser refuse to hand the response to the calling script.
    assert response.status_code == 200
    assert "Access-Control-Allow-Origin" not in response.headers


def test_a_request_without_an_origin_still_succeeds(client):
    """CORS is a browser mechanism, so curl and server-to-server callers are
    unaffected. Flask-Cors still stamps a header on the response; nothing
    enforces it when no browser is involved."""
    response = client.get("/api/products")

    assert response.status_code == 200
    assert response.get_json()["data"] == []
