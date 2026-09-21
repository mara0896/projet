from ...models import Game
from .dto import AdminGameDTO, PublicGameDTO


class GameMapper:
    @staticmethod
    def to_public(game: Game) -> PublicGameDTO:
        return PublicGameDTO(
            slug=game.slug,
            name=game.name,
            description=game.description,
            thumbnail=game.thumbnail,
        )

    @staticmethod
    def to_admin(game: Game) -> AdminGameDTO:
        return AdminGameDTO(
            id=game.id,
            slug=game.slug,
            name=game.name,
            description=game.description,
            thumbnail=game.thumbnail,
            is_active=game.is_active,
            created_at=game.created_at,
            updated_at=game.updated_at,
        )
