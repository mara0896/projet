import pytest

from app.core.errors import GameSlugAlreadyExists, GameNotFound
from app.modules.game.service import GameService


class FakeSession:
    def __init__(self):
        self.commit_count = 0

    def commit(self):
        self.commit_count += 1


class FakeGameRepository:
    def __init__(self):
        self.games = []
        self.session = FakeSession()

    def find_public(self):
        return [
            game
            for game in self.games
            if game.deleted_at is None and game.is_active
        ]

    def find_all_active_or_inactive(self):
        return [
            game
            for game in self.games
            if game.deleted_at is None
        ]

    def find_by_id(self, game_id):
        for game in self.games:
            if game.id == game_id and game.deleted_at is None:
                return game

        return None

    def find_by_slug(self, slug):
        for game in self.games:
            if game.slug == slug and game.deleted_at is None:
                return game

        return None

    def add(self, game):
        game.id = len(self.games) + 1
        self.games.append(game)
        return game

    def save(self, game):
        return game


# Test game format ex : "  tic-tac-toe " became "tic-tac-toe"
# Proves the service applies the rule : slug  = data["slug"].strip().lower()
def test_create_normalizes_slug():
    repository = FakeGameRepository()
    service = GameService(repository)

    game = service.create({
        "slug": "  tic-tac-toe  ",
        "name": "Tic-Tac-Toe",
        "description": "Play against the server.",
        "thumbnail": None,
        "is_active": True,
    })

    assert game.slug == "tic-tac-toe"
    assert game.name == "Tic-Tac-Toe"
    assert repository.session.commit_count == 1


# Test soft-delete. When deleted we:
# don't remove the game from the list
# we set game.deleted_at
# The game remains in memory but the repo no longer returns it through queries
def test_delete_sets_deleted_at():
    repository = FakeGameRepository()
    service = GameService(repository)

    game = service.create({
        "slug": "tic-tac-toe",
        "name": "Tic-Tac-Toe",
        "description": "Play against the server.",
        "thumbnail": None,
        "is_active": True,
    })

    service.delete(game.id)

    assert game.deleted_at is not None
    assert repository.session.commit_count == 2


# Proves the service checks for duplicates before creating a new game
def test_duplicate_slug_is_rejected():
    repository = FakeGameRepository()
    service = GameService(repository)

    data = {
        "slug": "tic-tac-toe",
        "name": "Tic-Tac-Toe",
        "description": "First game.",
        "thumbnail": None,
        "is_active": True,
    }

    service.create(data)

    with pytest.raises(GameSlugAlreadyExists):
        service.create(data)


# Checks interactions between soft-deletion service and repository filtering
# after deletion, repository.find_by_id(game.id) returns nothing
def test_deleted_game_is_not_returned_by_fake_repository():
    repository = FakeGameRepository()
    service = GameService(repository)

    game = service.create({
        "slug": "tic-tac-toe",
        "name": "Tic-Tac-Toe",
        "description": "Play against the server.",
        "thumbnail": None,
        "is_active": True,
    })

    service.delete(game.id)

    assert repository.find_by_id(game.id) is None


def test_missing_game_is_rejected():
    repository = FakeGameRepository()
    service = GameService(repository)

    with pytest.raises(GameNotFound):
        service.find_one(999)
