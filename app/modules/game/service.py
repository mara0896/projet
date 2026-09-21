# Business logic : normalize slug or reject duplicate, reject missing games, soft delete, etc.
# it does not implement any rules about the game itself, just the management of the game entity in the database

from datetime import datetime, timezone

from ...core.errors import GameNotFound, GameSlugAlreadyExists
from ...models import Game
from .repository import GameRepository


class GameService:
    def __init__(self, repository: GameRepository) -> None:
        self.repository = repository

    def find_public_games(self) -> list[Game]:
        return self.repository.find_public()

    def find_all_games(self) -> list[Game]:
        return self.repository.find_all_active_or_inactive()

    def find_one(self, game_id: int) -> Game:
        game = self.repository.find_by_id(game_id)

        if game is None:
            raise GameNotFound()

        return game

    def create(self, data: dict) -> Game:
        slug = data["slug"].strip().lower()

        if self.repository.find_by_slug(slug) is not None:
            raise GameSlugAlreadyExists()

        game = Game(
            slug=slug,
            name=data["name"].strip(),
            description=data["description"].strip(),
            thumbnail=data.get("thumbnail") or None,
            is_active=data.get("is_active", True),
        )

        self.repository.add(game)
        self.repository.session.commit()

        return game

    def update(self, game_id: int, data: dict) -> Game:
        game = self.find_one(game_id)
        slug = data["slug"].strip().lower()

        existing = self.repository.find_by_slug(slug)

        if existing is not None and existing.id != game.id:
            raise GameSlugAlreadyExists()

        game.slug = slug
        game.name = data["name"].strip()
        game.description = data["description"].strip()
        game.thumbnail = data.get("thumbnail") or None
        game.is_active = data.get("is_active", True)

        self.repository.save(game)
        self.repository.session.commit()

        return game

    def delete(self, game_id: int) -> None:
        game = self.find_one(game_id)
        game.deleted_at = datetime.now(timezone.utc)

        self.repository.save(game)
        self.repository.session.commit()
