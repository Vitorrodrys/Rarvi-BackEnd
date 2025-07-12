from datetime import datetime, timedelta, timezone
import numpy as np
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
        stmt = stmt.join(models.Discipline)
        if discipline_id:
            stmt = stmt.filter(models.Card.discipline_id == discipline_id)
        stmt = stmt.filter(models.Discipline.user_id == user_id)
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
        *,
        from_time: Optional[datetime] = None,
        to_time: Optional[datetime] = None,
        discipline_id: Optional[int] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> list[models.Card]:
        from_time = from_time or datetime(1970, 1, 1)
        to_time = to_time or (datetime.now(timezone.utc) + timedelta(days=365 * 1000))
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

    def get_randoms_by_priority(
        self, db_session: Session, user_id: int, quantity:int, *, discipline_id: Optional[int] = None
    ) -> list[models.Card]:
        stmt = db_session.query(models.Card.id, models.Card.priority_weight)
        stmt = self.__basic_stmt(stmt, user_id, discipline_id=discipline_id)
        cards = stmt.all()
        if not cards:
            return []

        ids, weights = zip(*cards)
        total = sum((w+1 for w in weights))
        probabilities = [(w+1) / total for w in weights]

        # choice the Q cards from weighted probabilities
        quantity = min(quantity, len(cards))
        selected_cards = np.random.choice(ids, size=quantity, replace=False, p=probabilities)
        return [self.get(db_session, card_id) for card_id in selected_cards]
