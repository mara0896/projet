# Manage all the dependencies and services for the app

from collections.abc import Callable
from enum import Enum
from typing import Any

from flask import g, has_request_context

from .modules.game.repository import GameRepository
from .modules.game.service import GameService
from .modules.auth.repository import UserRepository
from .modules.auth.service import AuthService
from .modules.tictactoe.repository import TicTacToeRepository
from .modules.tictactoe.service import TicTacToeService

from .core.security.hashing import PasswordHashing
from .core.security.jwt import JWTService

class Lifetime(Enum):
    SINGLETON = "singleton"
    SCOPED = "scoped"
    TRANSIENT = "transient"


class Container:
    def __init__(self) -> None:
        self._registrations: dict[str, tuple[Callable[[], Any], Lifetime]] = {}
        self._singletons: dict[str, Any] = {}

    # tells container how to create an object and how often it's created
    # singleton = once per process
    # scoped = once per request
    # transient = every time it's requested
    def register(
        self,
        name: str,
        factory: Callable[[], Any],
        lifetime: Lifetime,
    ) -> None:
        self._registrations[name] = (factory, lifetime)

    # Ask the container for an object
    def resolve(self, name: str) -> Any:
        if name not in self._registrations:
            raise KeyError(f"No dependency registered for: {name}")

        factory, lifetime = self._registrations[name]

        if lifetime is Lifetime.SINGLETON:
            if name not in self._singletons:
                self._singletons[name] = factory()

            return self._singletons[name]

        if lifetime is Lifetime.SCOPED:
            if not has_request_context():
                raise RuntimeError(
                    "Scoped dependencies require an active request"
                )

            scoped_objects = getattr(g, "_scoped_dependencies", {})

            if name not in scoped_objects:
                scoped_objects[name] = factory()
                g._scoped_dependencies = scoped_objects

            return scoped_objects[name]

        return factory()


# Dummy service to prove that dependency injection works
class GreetingService:
    def message(self) -> str:
        return "Dependency injection is working."


def create_container(config=None) -> Container:
    container = Container()

    container.register(
        "greeting_service",
        GreetingService,
        Lifetime.SCOPED,
    )

    container.register(
        "game_repository",
        GameRepository,
        Lifetime.SCOPED,
    )

    container.register(
        "game_service",
        lambda: GameService(
            container.resolve("game_repository")
        ),
        Lifetime.SCOPED,
    )

    container.register(
        "password_hasher",
        PasswordHashing,
        Lifetime.SINGLETON,
    )

    container.register(
        "jwt_service",
        lambda: JWTService(
            secret_key=config.jwt_secret_key,
            expires_minutes=config.jwt_expires_minutes,
        ),
        Lifetime.SINGLETON,
    )

    container.register(
        "user_repository",
        UserRepository,
        Lifetime.SCOPED,
    )

    container.register(
        "auth_service",
        lambda: AuthService(
            users=container.resolve("user_repository"),
            hasher=container.resolve("password_hasher"),
        ),
        Lifetime.SCOPED,
    )

    container.register(
        "tictactoe_repository",
        TicTacToeRepository,
        Lifetime.SCOPED,
    )

    container.register(
        "tictactoe_service",
        lambda: TicTacToeService(
            container.resolve("tictactoe_repository")
        ),
        Lifetime.SCOPED,
    )

    return container
