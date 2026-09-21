from sqlalchemy import select

from ...extensions import db
from ...models import GameSession


class TicTacToeRepository:
    def __init__(self) -> None:
        self.session = db.session

    def find_session(
        self,
        session_id: int,
    ) -> GameSession | None:
        statement = select(GameSession).where(
            GameSession.id == session_id,
            GameSession.deleted_at.is_(None),
        )

        return self.session.scalar(statement)

    def add(self, game_session: GameSession) -> GameSession:
        self.session.add(game_session)
        return game_session

    def commit(self) -> None:
        self.session.commit()
