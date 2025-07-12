from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from .base import BaseSchema


class DisciplineCreateSchema(BaseModel):
    name: str
    red: int = Field(ge=0, le=255)
    blue: int = Field(ge=0, le=255)
    green: int = Field(ge=0, le=255)


class DisciplineUpdateSchema(BaseModel):
    name: Optional[str] = None
    red: Optional[int] = Field(default=None, ge=0, le=255)
    blue: Optional[int] = Field(default=None, ge=0, le=255)
    green: Optional[int] = Field(default=None, ge=0, le=255)


class DisciplineCommitSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    red: Optional[int] = None
    blue: Optional[int] = None
    green: Optional[int] = None
    user_id: Optional[int] = None


class DisciplineSchema(BaseSchema):
    id: int
    name: str
    red: int
    blue: int
    green: int
    user_id: int
