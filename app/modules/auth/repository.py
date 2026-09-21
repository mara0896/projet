from sqlalchemy import select

from ...extensions import db
from ...models import User, Role


class UserRepository:
    def __init__(self) -> None:
        self.session = db.session

    def find_by_email(self, email: str) -> User | None:
        statement = select(User).where(
            User.email == email,
            User.deleted_at.is_(None),
        )

        return self.session.scalar(statement)

    def find_by_id(self, user_id: int) -> User | None:
        statement = select(User).where(
            User.id == user_id,
            User.deleted_at.is_(None),
        )

        return self.session.scalar(statement)

    def find_role_by_code(self, code: str) -> Role | None:
        statement = select(Role).where(
            Role.code == code,
            Role.deleted_at.is_(None),
        )

        return self.session.scalar(statement)

    def add(self, user: User) -> User:
        self.session.add(user)
        return user

    def commit(self) -> None:
        self.session.commit()
