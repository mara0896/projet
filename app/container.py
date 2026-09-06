# Manage all the dependencies and services for the app

from collections.abc import Callable
from enum import Enum
from typing import Any

from flask import g, has_request_context


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


def create_container() -> Container:
    container = Container()

    container.register(
        "greeting_service",
        GreetingService,
        Lifetime.SCOPED,
    )

    return container
