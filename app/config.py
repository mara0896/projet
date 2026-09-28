# Load all settings and initialize Flask app instance

import os
from dataclasses import dataclass

# load environment
from dotenv import load_dotenv
load_dotenv(".env.local")


@dataclass(frozen=True)
class Config:               # Typed container for app configuration
    secret_key: str
    database_url: str
    jwt_secret_key: str
    jwt_expires_minutes: int
    debug: bool = False
    testing: bool = False


# Force required environment variables to be present, otherwise raise an error
# Don't allow the app to start if not present
def _required_env(name: str) -> str:
    value = os.getenv(name)

    if not value:
        raise RuntimeError(f"Missing required environment variable: {name}")

    return value


# Select configuration based on the environment name.
def get_config(config_name: str = "development") -> Config:
    if config_name == "testing":
        return Config(
            secret_key="testing-secret",
            database_url="sqlite:///:memory:",
            debug=False,
            testing=True,
            jwt_secret_key="testing-jwt-secret-key-at-least-32-bytes",
            jwt_expires_minutes=30,
        )

    return Config(
        secret_key=_required_env("FLASK_SECRET_KEY"),
        database_url=os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg://postgres:secret@localhost:5432/mydb",
        ),
        jwt_secret_key=_required_env("JWT_SECRET_KEY"),
        jwt_expires_minutes=int(os.getenv("JWT_EXPIRES_MINUTES", "30")),
        debug=config_name == "development",
        testing=False,
    )
