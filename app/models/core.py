from datetime import datetime

from sqlalchemy import ForeignKey, Index, String, Table, Column, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ..extensions import db
from .base import BaseEntity


user_roles = Table(
    "user_roles",
    db.metadata,
    Column(
        "user_id",
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class User(BaseEntity):
    __tablename__ = "users"
    __table_args__ = (
        Index(
            "uq_users_email_active",
            "email",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    email: Mapped[str] = mapped_column(String(320), nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    display_name: Mapped[str] = mapped_column(String(80), nullable=False)

    roles: Mapped[list["Role"]] = relationship(
        secondary=user_roles,
        back_populates="users",
    )
    sessions: Mapped[list["GameSession"]] = relationship(back_populates="user")
    scores: Mapped[list["Score"]] = relationship(back_populates="user")


class Role(BaseEntity):
    __tablename__ = "roles"

    code: Mapped[str] = mapped_column(String(40), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(80), nullable=False)

    users: Mapped[list[User]] = relationship(
        secondary=user_roles,
        back_populates="roles",
    )


class Game(BaseEntity):
    __tablename__ = "games"
    __table_args__ = (
        Index(
            "uq_games_slug_active",
            "slug",
            unique=True,
            postgresql_where=text("deleted_at IS NULL"),
        ),
    )

    slug: Mapped[str] = mapped_column(String(50), nullable=False)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    thumbnail: Mapped[str | None] = mapped_column(String(255), nullable=True)
    is_active: Mapped[bool] = mapped_column(default=True, nullable=False)

    sessions: Mapped[list["GameSession"]] = relationship(back_populates="game")
    scores: Mapped[list["Score"]] = relationship(back_populates="game")


class GameSession(BaseEntity):
    __tablename__ = "game_sessions"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="RESTRICT"),
        nullable=False,
    )
    status: Mapped[str] = mapped_column(
        String(20), nullable=False, default="active"
    )
    state: Mapped[dict] = mapped_column(db.JSON, nullable=False, default=dict)
    started_at: Mapped[datetime] = mapped_column(nullable=False)
    finished_at: Mapped[datetime | None] = mapped_column(nullable=True)

    user: Mapped[User] = relationship(back_populates="sessions")
    game: Mapped[Game] = relationship(back_populates="sessions")
    score: Mapped["Score | None"] = relationship(
        back_populates="session",
        uselist=False,
    )


class Score(BaseEntity):
    __tablename__ = "scores"

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
    )
    game_id: Mapped[int] = mapped_column(
        ForeignKey("games.id", ondelete="RESTRICT"),
        nullable=False,
    )
    game_session_id: Mapped[int] = mapped_column(
        ForeignKey("game_sessions.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    score_type: Mapped[str] = mapped_column(String(40), nullable=False)
    score_value: Mapped[float] = mapped_column(nullable=False)

    user: Mapped[User] = relationship(back_populates="scores")
    game: Mapped[Game] = relationship(back_populates="scores")
    session: Mapped[GameSession] = relationship(back_populates="score")
