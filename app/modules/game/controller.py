from flask import (
    Blueprint,
    current_app,
    render_template,
)

from ...container import Container
from .mapper import GameMapper


game_bp = Blueprint("games", __name__, url_prefix="/games")


@game_bp.get("")
def list_games():
    container: Container = current_app.extensions["container"]
    service = container.resolve("game_service")

    games = service.find_public_games()
    game_dtos = [GameMapper.to_public(game) for game in games]

    return render_template(
        "games/list.html",
        games=game_dtos,
    )
