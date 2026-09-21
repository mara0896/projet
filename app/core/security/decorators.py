from functools import wraps

import jwt
from flask import current_app, g, redirect, request, url_for

from ...container import Container
from ...core.errors import (
    AuthenticationRequired,
    PermissionDenied,
)


def auth_required(roles: tuple[str, ...] = ()):
    def decorator(view):
        @wraps(view)
        def wrapped(*args, **kwargs):
            token = request.cookies.get("access_token")

            if not token:
                raise AuthenticationRequired()

            container: Container = (
                current_app.extensions["container"]
            )

            jwt_service = container.resolve("jwt_service")
            users = container.resolve("user_repository")

            try:
                payload = jwt_service.decode_token(token)
                user_id = int(payload["sub"])
            except (
                jwt.InvalidTokenError,
                KeyError,
                TypeError,
                ValueError,
            ) as error:
                raise AuthenticationRequired() from error

            user = users.find_by_id(user_id)

            if user is None:
                raise AuthenticationRequired()

            if roles:
                user_roles = {
                    role.code
                    for role in user.roles
                }

                if not user_roles.intersection(roles):
                    raise PermissionDenied()

            g.current_user = user

            return view(*args, **kwargs)

        return wrapped

    return decorator
