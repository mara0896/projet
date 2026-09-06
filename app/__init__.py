# Creates Flask app instance and initializes extensions

from flask import Flask, g

from .config import get_config
from .container import create_container


# Flask app Factory function
# Create a new app every time this function is called (multiple instances authorized like test_app and dev_app simultaneously)
def create_app(config_name: str = "development") -> Flask:
    app = Flask(__name__)

    config = get_config(config_name)

    app.config.from_mapping(
        SECRET_KEY=config.secret_key,
        SQLALCHEMY_DATABASE_URI=config.database_url,
        DEBUG=config.debug,
        TESTING=config.testing,
    )

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

    return app