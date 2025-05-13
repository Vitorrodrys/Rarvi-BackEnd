from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .discipline import Discipline


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    email: Mapped[str] = mapped_column(String(100), unique=True)
    pass_checksum: Mapped[str] = mapped_column(String(512))

    disciplines: Mapped[list["Discipline"]] = relationship(back_populates="user")
