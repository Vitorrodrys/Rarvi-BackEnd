from typing import Optional

from sqlalchemy.orm import Query, Session

import models
import schemas

from .crud_base import CRUDBase


class CRUDDisciplines(
    CRUDBase[
        models.Discipline,
        schemas.DisciplineCommitSchema,
        schemas.DisciplineUpdateSchema,
    ]
):
    def __init__(self):
        super().__init__(models.Discipline)

    def __basic_stmt(self, db_session: Session, user_id: int) -> Query:
        return db_session.query(models.Discipline).filter(
            models.Discipline.user_id == user_id
        )

    def get_disciplines_by_user(
        self,
        db_session: Session,
        user_id: int,
        *,
        offset: Optional[int],
        limit: Optional[int],
    ) -> list[models.Discipline]:
        stmt = self.__basic_stmt(db_session, user_id)
        if offset:
            stmt.offset(offset)
        if limit:
            stmt.limit(limit)
        return stmt.all()
