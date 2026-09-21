# raise application errors if missing game or duplicate slug
# avoid to give away too much information to the user.

class DomainError(Exception):
    """Base class for expected business errors."""


class GameNotFound(DomainError):
    pass


class GameSlugAlreadyExists(DomainError):
    pass


# During registration if email already used for an user
class EmailAlreadyRegistered(DomainError):
    pass


# Unknown email or if password is incorrect
# same exception for both so attackers cannot discover registered emails
class InvalidCredentials(DomainError):
    pass


# When user tries to go through a route without a valid token
# Normally correspond to HTTP 401
class AuthenticationRequired(DomainError):
    pass


# User is authenticated but lacks the required role.
# ex : a regular player visiting an admin route
class PermissionDenied(DomainError):
    pass
