from flask import (
    Blueprint,
    current_app,
    g,
    jsonify,
    request,
)

from ...container import Container
from ...core.errors import (
    PermissionDenied,
    TicTacToeGameFinished,
    TicTacToeInvalidMove,
    TicTacToeSessionNotFound,
)
from ...core.security.decorators import auth_required


tictactoe_bp = Blueprint(
    "tictactoe",
    __name__,
    url_prefix="/api/tictactoe",
)


def _service():
    container: Container = (
        current_app.extensions["container"]
    )

    return container.resolve("tictactoe_service")


def _state_response(game_session):
    return {
        "session_id": game_session.id,
        "status": game_session.status,
        "board": game_session.state["board"],
        "turn": game_session.state["turn"],
        "winner": game_session.state["winner"],
    }


@tictactoe_bp.post("/sessions")
@auth_required()
def create_session():
    container: Container = (
        current_app.extensions["container"]
    )

    game_repository = container.resolve(
        "game_repository"
    )

    game = game_repository.find_by_slug("tic-tac-toe")

    if game is None:
        return jsonify(error="Game is not configured"), 500

    game_session = _service().create_session(
        g.current_user,
        game,
    )

    return jsonify(
        _state_response(game_session)
    ), 201


@tictactoe_bp.get("/sessions/<int:session_id>")
@auth_required()
def get_session(session_id: int):
    game_session = _service().get_owned_session(
        session_id,
        g.current_user,
    )

    return jsonify(
        _state_response(game_session)
    )


@tictactoe_bp.post(
    "/sessions/<int:session_id>/moves"
)
@auth_required()
def play_move(session_id: int):
    body = request.get_json(silent=True) or {}
    cell = body.get("cell")

    if not isinstance(cell, int):
        return jsonify(
            error="cell must be an integer"
        ), 400

    try:
        game_session = _service().play_move(
            session_id,
            g.current_user,
            cell,
        )
    except TicTacToeSessionNotFound:
        return jsonify(error="Session not found"), 404
    except PermissionDenied:
        return jsonify(error="Not your session"), 403
    except (
        TicTacToeInvalidMove,
        TicTacToeGameFinished,
    ):
        return jsonify(error="Invalid move"), 400

    return jsonify(
        _state_response(game_session)
    )