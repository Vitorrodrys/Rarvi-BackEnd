from typing import TYPE_CHECKING
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .discipline import Discipline


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(100))
    question: Mapped[str] = mapped_column(String(1024))
    answer: Mapped[str] = mapped_column(String(1024))
    last_viewed_at: Mapped[datetime] = mapped_column(
        DateTime, default=lambda: datetime.now(timezone.utc)
    )
    priority_weight: Mapped[int] = mapped_column(default=0)

    discipline_id: Mapped[int] = mapped_column(ForeignKey("disciplines.id"))
    discipline: Mapped["Discipline"] = relationship(back_populates="cards")
