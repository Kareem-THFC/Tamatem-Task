"""Serves the built React bundle from the same origin as the API.

Only the deployed image has a bundle to serve: the Docker build copies Vite's
output into ``app/frontend_dist``. Locally the directory does not exist and
none of these routes are registered, so the Vite dev server keeps its usual
job and this module stays invisible during development.
"""

from pathlib import Path

from flask import Flask, Response, abort, send_from_directory

BUNDLE_DIR = Path(__file__).resolve().parents[1] / "frontend_dist"

INDEX_FILE = "index.html"

# Vite fingerprints everything under assets/, so a given URL's contents can
# never change and the browser can keep it for a year.
ASSET_CACHE_CONTROL = "public, max-age=31536000, immutable"

# index.html is the one file whose URL is stable while its contents change on
# every deploy. Caching it would pin a reviewer to a stale bundle referencing
# asset filenames that no longer exist.
INDEX_CACHE_CONTROL = "no-cache"


def bundle_is_present() -> bool:
    """Report whether a built frontend was baked into the image."""
    return (BUNDLE_DIR / INDEX_FILE).is_file()


def _send_index() -> Response:
    response = send_from_directory(BUNDLE_DIR, INDEX_FILE)
    response.headers["Cache-Control"] = INDEX_CACHE_CONTROL
    return response


def register_spa(app: Flask) -> None:
    """Attach the routes that serve the bundle, if there is one to serve."""
    if not bundle_is_present():
        app.logger.info("No frontend bundle found; serving the API only.")
        return

    @app.get("/")
    def spa_index() -> Response:
        return _send_index()

    @app.get("/<path:requested>")
    def spa_catch_all(requested: str) -> Response:
        # Werkzeug prefers static rules over this converter, so a registered
        # endpoint is never shadowed. An *unregistered* /api path would fall
        # through to here though, and answering it with the HTML shell would
        # turn a typo into a confusing 200 for an API client expecting JSON.
        if requested == "api" or requested.startswith("api/"):
            abort(404)

        candidate = BUNDLE_DIR / requested

        if candidate.is_file():
            response = send_from_directory(BUNDLE_DIR, requested)

            if requested.startswith("assets/"):
                response.headers["Cache-Control"] = ASSET_CACHE_CONTROL

            return response

        # Anything else is a client-side route such as /products/12. The router
        # in the browser reads the path once the shell has loaded, so a deep
        # link pasted into the address bar has to return the shell rather than
        # a 404 the way a plain static host would.
        return _send_index()
