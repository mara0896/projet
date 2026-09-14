from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity


class Character(BaseEntity):
    __tablename__ = "characters"

    name: Mapped[str] = mapped_column(String(100), nullable=False)

    character_attributes: Mapped[list["CharacterAttribute"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan",
    )


class Attribute(BaseEntity):
    __tablename__ = "attributes"

    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    label: Mapped[str] = mapped_column(String(100), nullable=False)
    value_type: Mapped[str] = mapped_column(
        String(20), nullable=False, default="boolean"
    )

    character_attributes: Mapped[list["CharacterAttribute"]] = relationship(
        back_populates="attribute",
        cascade="all, delete-orphan",
    )


class CharacterAttribute(BaseEntity):
    __tablename__ = "character_attributes"
    __table_args__ = (
        UniqueConstraint(
            "character_id",
            "attribute_id",
            name="uq_character_attribute_pair",
        ),
    )

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id", ondelete="CASCADE"),
        nullable=False,
    )
    attribute_id: Mapped[int] = mapped_column(
        ForeignKey("attributes.id", ondelete="CASCADE"),
        nullable=False,
    )
    value: Mapped[str] = mapped_column(String(255), nullable=False)

    character: Mapped[Character] = relationship(
        back_populates="character_attributes"
    )
    attribute: Mapped[Attribute] = relationship(
        back_populates="character_attributes"
    )
