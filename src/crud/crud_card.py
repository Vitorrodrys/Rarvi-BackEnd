from datetime import datetime, timedelta, timezone
import random
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

    def update_priority_weight(
        self,
        db_session: Session,
        db_card: models.Card,
        difficulty: schemas.CardDifficultyEnum,
    ) -> models.Card:
        if db_card.priority_weight == 0 and difficulty < 0:
            return db_card
        db_card.priority_weight += difficulty
        db_session.add(db_card)
        db_session.commit()
        db_session.refresh(db_card)
        return db_card

    def get_random_by_priority(
        self, db_session: Session, user_id: int, *, discipline_id: Optional[int] = None
    ) -> Optional[models.Card]:
        stmt = db_session.query(models.Card.id, models.Card.priority_weight)
        stmt = self.__basic_stmt(stmt, user_id, discipline_id=discipline_id)
        card_weights = stmt.all()
        if not card_weights:
            return None
        weight_sum = sum(w[1] + 1 for w in card_weights)
        weights = ((weight_sum  -  w[1]) / weight_sum for w in card_weights)
        card_choiced = random.choices(card_weights, weights, k=1)[0]
        return self.get(db_session, card_choiced[0])
