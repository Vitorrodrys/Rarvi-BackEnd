from datetime import datetime
from enum import StrEnum
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseSchema


class CardDifficultyEnum(StrEnum):
    EASY = "easy"
    MEDIUM = "medium"
    HARD = "hard"


class CardCreateSchema(BaseModel):
    title: str = Field(min_length=5, max_length=100)
    question: str = Field(min_length=10, max_length=1024)
    answer: str = Field(min_length=10, max_length=1024)
    difficulty: CardDifficultyEnum
    discipline_id: int


class CardUpdateSchema(BaseModel):
    title: Optional[str] = Field(min_length=5, max_digits=100)
    question: Optional[str] = Field(min_length=10, max_length=1024)
    answer: Optional[str] = Field(min_length=10, max_length=1024)
    difficulty: Optional[CardDifficultyEnum]
    discipline_id: Optional[int]


class CardCommitSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    title: Optional[str]
    question: Optional[str]
    answer: Optional[str]
    difficulty: Optional[str]
    last_viewed_at: Optional[datetime]
    discipline_id: Optional[int]


class CardSchema(BaseSchema):
    title: str
    question: str
    answer: str
    difficulty: CardDifficultyEnum
    last_viewed_at: datetime
    discipline_id: int
