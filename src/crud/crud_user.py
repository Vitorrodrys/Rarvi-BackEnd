from typing import Optional

from sqlalchemy.orm import Session

import models
import schemas

from .crud_base import CRUDBase


class CRUDUser(
    CRUDBase[models.User, schemas.UserCommitSchema, schemas.UserCommitSchema]
):
    def __init__(self):
        super().__init__(models.User)

    def get_by_email(self, db_session: Session, email: str) -> Optional[models.User]:
        """
        Retrieve a user from the database by their email. If no user is found, return None.
        Args:
            db_session: A pre-established SQLAlchemy ORM session.
            email: The email of the user to retrieve.
        """
        return db_session.query(models.User).filter(models.User.email == email).first()

    def get_by_name(self, db_session: Session, name: str) -> Optional[models.User]:
        """
        Retrieve a user from the database by their name. If no user is found, return None.
        Args:
            db_session: A pre-established SQLAlchemy ORM session.
            name: The name of the user you want to retrieve.
        """
        return db_session.query(models.User).filter(models.User.name == name).first()
