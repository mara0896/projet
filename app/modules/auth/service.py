from ...core.errors import (
    EmailAlreadyRegistered,
    InvalidCredentials,
)
from ...models import User


class AuthService:
    def __init__(self, users, hasher):
        self.users = users
        self.hasher = hasher

    def register(
        self,
        email: str,
        password: str,
        display_name: str,
    ) -> User:
        normalized_email = email.strip().lower()

        if self.users.find_by_email(normalized_email) is not None:
            raise EmailAlreadyRegistered()

        player_role = self.users.find_role_by_code("player")

        if player_role is None:
            raise RuntimeError(
                "The player role has not been seeded."
            )

        user = User(
            email=normalized_email,
            password_hash=self.hasher.hash(password),
            display_name=display_name.strip(),
        )

        user.roles.append(player_role)

        self.users.add(user)
        self.users.commit()

        return user

    def authenticate(
        self,
        email: str,
        password: str,
    ) -> User:
        normalized_email = email.strip().lower()
        user = self.users.find_by_email(normalized_email)

        if user is None:
            raise InvalidCredentials()

        if not self.hasher.verify(
            user.password_hash,
            password,
        ):
            raise InvalidCredentials()

        return user
