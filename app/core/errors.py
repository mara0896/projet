# raise application errors if missing game or duplicate slug
# avoid to give away too much information to the user. just "not found" or "already exists"

class DomainError(Exception):
    """Base class for expected business errors."""


class GameNotFound(DomainError):
    pass


class GameSlugAlreadyExists(DomainError):
    pass