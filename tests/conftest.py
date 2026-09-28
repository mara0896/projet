# Creates real SQLAlchemy records in a disposable test database.
# The test client uses a JWT cookie and an isolated database,
# not local PostgreSQL.

import pytest

from app import create_app
from app.extensions import db
from app.models import Game, User
from app.core.security.jwt import JWTService


@pytest.fixture
def app():
    application = create_app("testing")

    with application.app_context():
        db.create_all()

    yield application

    with application.app_context():
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def game_data(app):
    with app.app_context():
        owner = User(
            email="owner@example.test",
            password_hash="unused-test-hash",
            display_name="Owner",
        )
        other_user = User(
            email="other@example.test",
            password_hash="unused-test-hash",
            display_name="Other Player",
        )
        game = Game(
            slug="tic-tac-toe",
            name="Tic-Tac-Toe",
            description="Test game",
            is_active=True,
        )

        db.session.add_all([owner, other_user, game])
        db.session.commit()

        jwt_service = JWTService(
            secret_key=app.config["JWT_SECRET_KEY"],
            expires_minutes=app.config["JWT_EXPIRES_MINUTES"],
        )

        return {
            "owner_id": owner.id,
            "other_user_id": other_user.id,
            "owner_token": jwt_service.create_token(owner.id),
            "other_token": jwt_service.create_token(other_user.id),
        }


@pytest.fixture
def logged_in_client(client, game_data):
    client.set_cookie("access_token", game_data["owner_token"])
    return client
