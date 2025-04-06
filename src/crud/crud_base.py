from typing import Generic, TypeVar

from sqlalchemy.orm import Session

from models import Base
from schemas import BaseCreateSchema, BaseUpdateSchema

ModelVar = TypeVar("ModelVar", bound=Base)
CreateSchemaVar = TypeVar("CreateSchemaVar", bound=BaseCreateSchema)
UpdateSchemaVar = TypeVar("UpdateSchemaVar", bound=BaseUpdateSchema)



class CRUDBase(Generic[ModelVar, CreateSchemaVar, UpdateSchemaVar]):

    def __init__(
        self,
        model: ModelVar
    ):
        self._model = model

    def create(self, db_session: Session, obj_in: CreateSchemaVar) -> ModelVar:
        db_obj = self._model(**obj_in.model_dump())
        db_session.add(db_obj)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj

    def update(self, db_session: Session, db_obj: ModelVar, obj_in: UpdateSchemaVar) -> ModelVar:
        for field, value in obj_in.model_dump(exclude_unset=True).items():
            setattr(db_obj, field, value)
        db_session.commit()
        db_session.refresh(db_obj)
        return db_obj

    def delete(self, db_session: Session, ident: int) -> ModelVar:
        db_obj = db_session.get(self._model, ident)
        if db_obj:
            db_session.delete(db_obj)
            db_session.commit()
        return db_obj

    def get(self, db_session: Session, ident: int) -> ModelVar:
        db_obj = db_session.get(self._model, ident)
        return db_obj
