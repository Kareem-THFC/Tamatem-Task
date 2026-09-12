import os

from flask import Flask

from app.cli import register_cli_commands
from app.config import Config
from app.errors.handlers import register_error_handlers, register_jwt_error_handlers
from app.extensions import cors, db, jwt, migrate
from app.routes.auth import auth_bp
from app.routes.docs import docs_bp
from app.routes.health import health_bp
from app.routes.orders import orders_bp
from app.routes.products import products_bp

# Secrets have no safe default: a missing value must stop startup rather than
# surface later as a confusing failure when the first token is signed.
REQUIRED_CONFIG_KEYS = ("SECRET_KEY", "JWT_SECRET_KEY")


def _validate_required_config(app: Flask) -> None:
    """Raise immediately when configuration required to run is missing."""
    missing = [key for key in REQUIRED_CONFIG_KEYS if not app.config.get(key)]

    if missing:
        raise RuntimeError(
            f"Missing required configuration: {', '.join(missing)}. "
            "Copy backend/.env.example to backend/.env and set real values."
        )


def create_app(test_config: dict | None = None) -> Flask:
    """Create and configure an application instance.
    """
    app = Flask(__name__, instance_relative_config=True)
    app.config.from_object(Config)

    if test_config is not None:
        app.config.update(test_config)

    _validate_required_config(app)

    # The instance directory is intentionally outside source packages so local
    # SQLite databases and runtime files are not committed with application code.
    os.makedirs(app.instance_path, exist_ok=True)

    db.init_app(app)

    # Importing models registers their tables with SQLAlchemy's metadata before
    # Flask-Migrate reads it to generate migrations.
    from app.models import Order, Product, User  # noqa: F401

    migrate.init_app(app, db)
    jwt.init_app(app)

    # The browser blocks a cross-origin response unless the server opts in, so
    # the API has to name the origins allowed to read it. Flask-Cors adds the
    # Access-Control-* headers to each response and answers the OPTIONS
    # preflight the browser sends before anything other than a simple request.
    #
    # Only /api/* is covered, so nothing else is inadvertently opened up.
    #
    # supports_credentials is deliberately left off: the access token travels
    # in the Authorization header, which the allowlisted headers below permit,
    # rather than in a cookie. Turning it on would be required only if the
    # token moved to a cookie.
    cors.init_app(
        app,
        resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}},
        allow_headers=["Authorization", "Content-Type"],
        methods=["GET", "POST", "OPTIONS"],
    )
    register_cli_commands(app)
    register_error_handlers(app)
    register_jwt_error_handlers(jwt)

    app.register_blueprint(auth_bp, url_prefix="/api/auth")
    app.register_blueprint(docs_bp, url_prefix="/api")
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(products_bp, url_prefix="/api")
    app.register_blueprint(orders_bp, url_prefix="/api")

    return app
