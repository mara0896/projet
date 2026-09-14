from datetime import datetime, timezone

from sqlalchemy import ForeignKey, Index, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity


class PedantleArticle(BaseEntity):
    __tablename__ = "pedantle_articles"

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    published_on: Mapped[datetime | None] = mapped_column(nullable=True)

    word_scores: Mapped[list["PedantleWordScore"]] = relationship(
        back_populates="article",
        cascade="all, delete-orphan",
    )


class PedantleWordScore(BaseEntity):
    __tablename__ = "pedantle_word_scores"
    __table_args__ = (
        Index(
            "ix_pedantle_word_scores_article_word",
            "article_id",
            "word",
            unique=True,
        ),
    )

    article_id: Mapped[int] = mapped_column(
        ForeignKey("pedantle_articles.id", ondelete="CASCADE"),
        nullable=False,
    )
    word: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float] = mapped_column(nullable=False)
    rank: Mapped[int] = mapped_column(nullable=False)

    article: Mapped[PedantleArticle] = relationship(
        back_populates="word_scores"
    )


class PedantleGuess(BaseEntity):
    __tablename__ = "pedantle_guesses"

    game_session_id: Mapped[int] = mapped_column(
        ForeignKey("game_sessions.id", ondelete="CASCADE"),
        nullable=False,
    )
    word: Mapped[str] = mapped_column(String(255), nullable=False)
    score: Mapped[float | None] = mapped_column(nullable=True)
    rank: Mapped[int | None] = mapped_column(nullable=True)
    guessed_at: Mapped[datetime] = mapped_column(
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
