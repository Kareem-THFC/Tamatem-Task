"""Health-check endpoint used to verify that the API is running."""

from flask import Blueprint

from app.utils.responses import success_response

health_bp = Blueprint("health", __name__)


@health_bp.get("/health")
def health_check():
    """Return a lightweight readiness response without requiring authentication."""
    return success_response({"status": "ok"})
