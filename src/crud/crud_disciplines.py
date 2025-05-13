from sqlalchemy.orm import Session

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
        super().__init__(models.User)

    def get_disciplines_by_user(
        self, db_session: Session, *, user_id: int
    ) -> list[models.Discipline]:
        return (
            db_session.query(models.Discipline)
            .filter(models.Discipline.user_id == user_id)
            .all()
        )
