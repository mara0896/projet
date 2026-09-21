# Creates Flask app instance and initializes extensions

from flask import Flask, g

from .config import get_config
from .container import create_container
from .extensions import db, migrate, csrf
from .modules.game.controller import game_bp
from .modules.game.admin_controller import admin_game_bp


# Flask app Factory function
# Create a new app every time this function is called.
# This allows separate development and test app instances.
def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    config = get_config(config_name)

    app.config.from_mapping(
        SECRET_KEY=config.secret_key,
        SQLALCHEMY_DATABASE_URI=config.database_url,
        DEBUG=config.debug,
        TESTING=config.testing,
    )

    db.init_app(app)
    migrate.init_app(app, db)
    csrf.init_app(app)

    # Import models so Flask-Migrate can discover their metadata.
    from . import models  # noqa: F401

    app.extensions["container"] = create_container()

    # Flask runs cleanup after each request
    @app.teardown_request
    def cleanup_scoped_dependencies(exception: BaseException | None) -> None:
        scoped_objects = getattr(g, "_scoped_dependencies", {})

        for obj in scoped_objects.values():
            close = getattr(obj, "close", None)

            if close is not None:
                close()

        g.pop("_scoped_dependencies", None)

    from .routes import main_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(game_bp)
    app.register_blueprint(admin_game_bp)

    return app
