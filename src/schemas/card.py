from datetime import datetime, timezone
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseSchema


class CardDifficultyEnum(IntEnum):
    AGAIN = -1
    HARD = 0
    MEDIUM = 1
    EASY = 2


class CardCreateSchema(BaseModel):
    question: str = Field(min_length=10, max_length=1024)
    answer: str = Field(min_length=10, max_length=1024)
    discipline_id: int


class CardUpdateSchema(BaseModel):
    question: Optional[str] = Field(None, min_length=10, max_length=1024)
    answer: Optional[str] = Field(None, min_length=10, max_length=1024)
    discipline_id: Optional[int] = None


class CardCommitSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    question: Optional[str] = None
    answer: Optional[str] = None
    last_viewed_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    discipline_id: Optional[int] = None


class CardSchema(BaseSchema):
    id: int
    question: str
    answer: str
    last_viewed_at: datetime
    discipline_id: int

class SummarizedCardSchema(BaseSchema):
    id: int
    question: str
    discipline_id: int
