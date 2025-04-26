from datetime import datetime, timedelta
import hashlib
from typing import Optional

from pydantic import model_validator, BaseModel, ConfigDict, Field

from core import settings

from .base import BaseSchema


def _compute_password_checksum(password: str) -> str:
    salt = settings.get().CHECKSUM_SALT
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()


class UserCreateSchema(BaseModel):
    name: str
    email: str
    password: str


class UserUpdateSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None


class UserCommitSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: Optional[str] = None
    email: Optional[str] = None
    # The password is excluded from serialization because we don't have this field in the database.
    password: Optional[str] = Field(default=None, exclude=True)
    pass_checksum: Optional[str] = None

    @model_validator(mode="after")
    @classmethod
    def _compute_checksum(cls, values: "UserCommitSchema"):
        """
        Computes automatically the checksum of the password to be stored in the database.
        """
        password = values.password
        if password and not values.pass_checksum:
            values.pass_checksum = _compute_password_checksum(password)
        return values


class UserSchema(BaseSchema):
    id: int
    name: str
    email: str


class UserAuthSchema(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    password: str = Field(default=None, exclude=True)

    @property
    def pass_checksum(self) -> str:
        return _compute_password_checksum(self.password)


class JWTAuthSchema(BaseModel):
    issued_at: datetime = Field(default_factory=datetime.now)
    expires_at: datetime = Field(
        default_factory=lambda: datetime.now()
        + timedelta(hours=settings.get().JWT_VALID_PERIOD)
    )
    user_id: int
    signature: Optional[str] = None
