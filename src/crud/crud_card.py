from datetime import datetime, timedelta, timezone
from typing import Optional

from sqlalchemy.orm import Query, Session

import models
import schemas

from .crud_base import CRUDBase


class CRUDCard(
    CRUDBase[models.Card, schemas.CardCommitSchema, schemas.CardCommitSchema]
):
    def __init__(self):
        super().__init__(models.Card)

    def __basic_stmt(
        self, stmt: Query, user_id: int, *, discipline_id: Optional[int] = None
    ) -> Query:
        stmt = stmt.join(models.Discipline).where(
            models.Card.discipline_id == models.Discipline.id
        )
        if discipline_id:
            stmt = stmt.filter(models.Card.discipline_id == discipline_id)
        return stmt

    def get_cards(
        self,
        db_session: Session,
        user_id: int,
        *,
        discipline_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[models.Card]:
        stmt = db_session.query(models.Card)
        stmt = self.__basic_stmt(stmt, user_id, discipline_id=discipline_id)
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return stmt.all()

    def count(
        self,
        db_session: Session,
        user_id: int,
        *,
        discipline_id: Optional[int] = None,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
    ) -> int:
        stmt = db_session.query(models.Card)
        stmt = self.__basic_stmt(stmt, user_id, discipline_id=discipline_id)
        if from_time or to_time:
            from_time = from_time or datetime(1970, 1, 1)
            to_time = to_time or (
                datetime.now(timezone.utc) + timedelta(days=365 * 1000)
            )
            stmt = stmt.filter(models.Card.last_viewed_at.between(from_time, to_time))
        return stmt.count()

    def get_cards_by_period(
        self,
        db_session: Session,
        user_id: int,
        from_time: datetime,
        to_time: datetime,
        *,
        discipline_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[models.Card]:
        stmt = db_session.query(models.Card)
        stmt = self.__basic_stmt(stmt, user_id, discipline_id=discipline_id)
        stmt = stmt.filter(models.Card.last_viewed_at.between(from_time, to_time))
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)
        return stmt.all()
