from datetime import datetime, timezone

from ...core.errors import (
    PermissionDenied,
    TicTacToeGameFinished,
    TicTacToeInvalidMove,
    TicTacToeSessionNotFound,
)
from ...models import Game, GameSession, User
from . import engine
from .repository import TicTacToeRepository


class TicTacToeService:
    def __init__(self, repository: TicTacToeRepository) -> None:
        self.repository = repository

    def create_session(
        self,
        user: User,
        game: Game,
    ) -> GameSession:
        game_session = GameSession(
            user_id=user.id,
            game_id=game.id,
            status="active",
            state={
                "board": engine.new_board(),
                "turn": "X",
                "winner": None,
            },
            started_at=datetime.now(timezone.utc),
        )

        self.repository.add(game_session)
        self.repository.commit()

        return game_session

    def get_owned_session(
        self,
        session_id: int,
        user: User,
    ) -> GameSession:
        game_session = self.repository.find_session(session_id)

        if game_session is None:
            raise TicTacToeSessionNotFound()

        if game_session.user_id != user.id:
            raise PermissionDenied()

        return game_session

    def play_move(
        self,
        session_id: int,
        user: User,
        cell: int,
    ) -> GameSession:
        game_session = self.get_owned_session(
            session_id,
            user,
        )

        if game_session.status != "active":
            raise TicTacToeGameFinished()

        state = game_session.state
        board = state["board"]
        turn = state["turn"]

        if turn != "X":
            raise TicTacToeInvalidMove()

        try:
            board = engine.apply_move(board, cell, "X")
        except ValueError as error:
            raise TicTacToeInvalidMove() from error

        game_winner = engine.winner(board)

        if game_winner is not None:
            state["board"] = board
            state["winner"] = game_winner
            state["turn"] = None
            game_session.status = "finished"
            game_session.finished_at = datetime.now(timezone.utc)

        elif engine.is_draw(board):
            state["board"] = board
            state["winner"] = None
            state["turn"] = None
            game_session.status = "finished"
            game_session.finished_at = datetime.now(timezone.utc)

        else:
            server_cell = engine.best_move(board, "O")

            if server_cell is not None:
                board = engine.apply_move(
                    board,
                    server_cell,
                    "O",
                )

            game_winner = engine.winner(board)

            state["board"] = board
            state["winner"] = game_winner
            state["turn"] = (
                None if game_winner or engine.is_draw(board)
                else "X"
            )

            if game_winner or engine.is_draw(board):
                game_session.status = "finished"
                game_session.finished_at = datetime.now(
                    timezone.utc
                )

        game_session.state = state
        self.repository.commit()

        return game_session
