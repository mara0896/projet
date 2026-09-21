# The repo contains database access only 
# (how to query, filter deleted rows, save entities...)
from sqlalchemy import select

from ...extensions import db
from ...models import Game


class GameRepository:
    def __init__(self) -> None:
        self.session = db.session

    def find_public(self) -> list[Game]:
        statement = (
            select(Game)
            .where(
                Game.deleted_at.is_(None),  # Filter deleted/inactive
                Game.is_active.is_(True),
            )
            .order_by(Game.name.asc())
        )

        return list(self.session.scalars(statement))

    def find_all_active_or_inactive(self) -> list[Game]:
        statement = (
            select(Game)
            .where(Game.deleted_at.is_(None))
            .order_by(Game.name.asc())
        )

        return list(self.session.scalars(statement))

    def find_by_id(self, game_id: int) -> Game | None:
        statement = select(Game).where(
            Game.id == game_id,
            Game.deleted_at.is_(None),
        )

        return self.session.scalar(statement)

    def find_by_slug(self, slug: str) -> Game | None:
        statement = select(Game).where(
            Game.slug == slug,
            Game.deleted_at.is_(None),
        )

        return self.session.scalar(statement)

    def add(self, game: Game) -> Game:
        self.session.add(game)
        return game

    def save(self, game: Game) -> Game:
        self.session.add(game)
        return game
