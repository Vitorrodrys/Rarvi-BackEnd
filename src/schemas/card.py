from datetime import datetime, timezone
from enum import IntEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseSchema


class CardDifficultyEnum(IntEnum):
    AGAIN = 2
    HARD = 1
    MEDIUM = 0
    EASY = -1


class CardCreateSchema(BaseModel):
    question: str = Field(min_length=0, max_length=1024)
    answer: str
    discipline_id: int


class CardUpdateSchema(BaseModel):
    question: Optional[str] = Field(None, min_length=0, max_length=1024)
    answer: Optional[str]
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
