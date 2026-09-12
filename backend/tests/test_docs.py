"""Tests for the OpenAPI specification and the documentation page.

The specification is written by hand, which means it can drift away from the
code. The most valuable test here is therefore not that the page renders, but
that the spec and the application's real URL map still describe the same API.
"""

import json
import re
from pathlib import Path

import pytest

SPEC_PATH = Path(__file__).resolve().parents[1] / "app" / "static" / "openapi.json"

# Documented per-endpoint rather than as a path: /api/docs serves HTML and the
# static file is Flask's own route, so neither belongs in the API description.
UNDOCUMENTED_ENDPOINTS = {"docs.api_docs", "static"}


@pytest.fixture(scope="module")
def spec() -> dict:
    """Load the specification once for the whole module."""
    return json.loads(SPEC_PATH.read_text(encoding="utf-8"))


def documented_operations(spec: dict) -> set[tuple[str, str]]:
    """Return every (METHOD, path) pair the specification describes."""
    return {
        (method.upper(), path)
        for path, operations in spec["paths"].items()
        for method in operations
    }


def implemented_operations(app) -> set[tuple[str, str]]:
    """Return every (METHOD, path) pair the application actually serves.

    Flask's url_map holds rules such as ``/api/orders/<int:order_id>``, which
    are rewritten to the OpenAPI form ``/api/orders/{order_id}`` so the two
    sets are directly comparable. HEAD and OPTIONS are added automatically by
    Flask rather than being part of the API's design, so they are dropped.
    """
    operations = set()

    for rule in app.url_map.iter_rules():
        if rule.endpoint in UNDOCUMENTED_ENDPOINTS:
            continue

        # "<int:order_id>" -> "{order_id}"
        path = re.sub(r"<(?:[^:<>]+:)?([^<>]+)>", r"{\1}", rule.rule)

        for method in rule.methods - {"HEAD", "OPTIONS"}:
            operations.add((method, path))

    return operations


def test_the_specification_is_valid_json(spec):
    assert spec["openapi"].startswith("3.")
    assert spec["info"]["title"]
    assert spec["paths"]


def test_every_endpoint_is_documented(app, spec):
    """A route added without a spec entry should fail here, not in review."""
    missing = implemented_operations(app) - documented_operations(spec)

    assert missing == set(), f"Endpoints missing from openapi.json: {sorted(missing)}"


def test_the_specification_documents_nothing_that_does_not_exist(app, spec):
    """Guards the other direction: a renamed route leaving a stale entry."""
    stale = documented_operations(spec) - implemented_operations(app)

    assert stale == set(), f"openapi.json describes unknown endpoints: {sorted(stale)}"


def test_every_reference_in_the_specification_resolves(spec):
    """A typo in a $ref renders as a broken schema in Swagger UI, not an error."""
    serialised = json.dumps(spec)

    for pointer in set(re.findall(r'"\$ref": "([^"]+)"', serialised)):
        assert pointer.startswith("#/"), f"Unexpected external reference: {pointer}"

        target = spec

        # "#/components/schemas/Order" -> spec["components"]["schemas"]["Order"]
        for segment in pointer.removeprefix("#/").split("/"):
            assert segment in target, f"Unresolved reference: {pointer}"
            target = target[segment]


def test_protected_endpoints_are_marked_as_requiring_a_token(spec):
    """The padlock in Swagger UI has to match what @jwt_required() enforces."""
    for path in ["/api/orders", "/api/orders/{order_id}"]:
        for method, operation in spec["paths"][path].items():
            # A global `security` applies unless an operation overrides it, so
            # a protected operation is one that has not opted out.
            assert "security" not in operation, (
                f"{method.upper()} {path} opts out of authentication"
            )


def test_public_endpoints_are_marked_as_not_requiring_a_token(spec):
    """Requiring a token to log in would be an obvious documentation bug."""
    public = [
        ("/api/auth/login", "post"),
        ("/api/auth/register", "post"),
        ("/api/health", "get"),
    ]

    for path, method in public:
        assert spec["paths"][path][method]["security"] == []


def test_product_endpoints_accept_a_token_without_requiring_one(spec):
    """The product endpoints read the token optionally, and say so.

    `security: []` would be wrong here: it tells Swagger UI never to send the
    token, so "Try it out" could never demonstrate the `owned` flag. Listing
    an empty requirement alongside `bearerAuth` is how OpenAPI expresses
    "either anonymous or authenticated" -- the `{}` alternative is what keeps
    browsing public.
    """
    for path in ["/api/products", "/api/products/{product_id}"]:
        security = spec["paths"][path]["get"]["security"]

        assert {} in security, f"GET {path} no longer allows anonymous access"
        assert {"bearerAuth": []} in security, f"GET {path} ignores the token"


def test_the_docs_page_renders_and_points_at_the_specification(client):
    response = client.get("/api/docs")

    page = response.get_data(as_text=True)

    assert response.status_code == 200
    assert "text/html" in response.headers["Content-Type"]
    assert "/static/openapi.json" in page
    assert "swagger-ui" in page


def test_the_specification_is_served_as_json(client):
    response = client.get("/static/openapi.json")

    assert response.status_code == 200
    assert response.get_json()["info"]["title"] == "Tamatem Commerce API"
