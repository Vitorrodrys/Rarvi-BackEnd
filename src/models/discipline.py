from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, SmallInteger, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .user import User
    from .card import Card


class Discipline(Base):
    __tablename__ = "disciplines"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    red: Mapped[int] = mapped_column(SmallInteger)
    blue: Mapped[int] = mapped_column(SmallInteger)
    green: Mapped[int] = mapped_column(SmallInteger)

    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user: Mapped["User"] = relationship(back_populates="disciplines")

    cards: Mapped[list["Card"]] = relationship(
        back_populates="discipline", cascade="all, delete-orphan", passive_deletes=True
    )
