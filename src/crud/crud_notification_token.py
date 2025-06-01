from typing import Optional

from sqlalchemy.orm import Session

import models
import schemas

from .crud_base import CRUDBase


class CRUDNotificationToken(
    CRUDBase[
        models.NotificationToken,
        schemas.NotificationTokenCommitSchema,
        schemas.NotificationTokenCommitSchema,
    ]
):
    def __init__(self):
        super().__init__(models.NotificationToken)

    def get_by_token(
        self, db_session: Session, token: str, user_id: int
    ) -> Optional[models.NotificationToken]:
        return (
            db_session.query(models.NotificationToken)
            .filter(
                models.NotificationToken.token == token
                and models.NotificationToken.user_id == user_id
            )
            .first()
        )
