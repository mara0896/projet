from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PublicGameDTO:
    slug: str
    name: str
    description: str
    thumbnail: str | None


@dataclass(frozen=True)
class AdminGameDTO:
    id: int
    slug: str
    name: str
    description: str
    thumbnail: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime
