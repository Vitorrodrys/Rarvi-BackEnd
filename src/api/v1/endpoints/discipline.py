from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api.deps import get_db, get_auth_token
import crud
import schemas


discipline_router = APIRouter()


@discipline_router.get("/disciplines")
def get_user_disciplines(
    auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
) -> list[schemas.DisciplineSchema]:
    disciplines = crud.discipline.get_disciplines_by_user(
        db_session, user_id=auth_session.user_id
    )
    return disciplines


@discipline_router.post("/discipline")
def create_discipline(
    auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
    discipline: schemas.DisciplineCreateSchema = Body(...),
) -> schemas.DisciplineSchema:
    try:
        discipline_commit = schemas.DisciplineCommitSchema.model_validate(discipline)
        discipline_commit.user_id = auth_session.user_id
        db_discipline = crud.discipline.create(db_session, discipline_commit)
        return db_discipline
    except IntegrityError as e:
        raise HTTPException(
            status_code=400, detail="discipline with this name already exists"
        ) from e


@discipline_router.patch("/discipline/{discipline_id}")
def update_discipline(
    discipline_id: int,
    auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
    discipline: schemas.DisciplineUpdateSchema = Body(...),
) -> schemas.DisciplineSchema:
    db_discipline = crud.discipline.get(db_session, discipline_id)
    if db_discipline.user_id != auth_session.user_id:
        raise HTTPException(
            status_code=403,
            detail="The user cannot update this discipline because they aren't the owner of it",
        )
    try:
        crud.discipline.update(db_session, db_obj=db_discipline, obj_in=discipline)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400, detail="The name of the discipline is already in using"
        ) from e


@discipline_router.delete("/discipline/{discipline_id}")
def delete_discipline(
    discipline_id: int,
    auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
) -> schemas.DisciplineSchema:
    db_discipline = crud.discipline.get(db_session, discipline_id)
    if not db_discipline:
        raise HTTPException(status_code=400, detail="Discipline not found")
    if db_discipline.user_id != auth_session.user_id:
        raise HTTPException(
            status_code=403,
            detail="Not allowed to deleted a discipline that  you do not own",
        )
    try:
        return crud.discipline.delete(db_session, discipline_id)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400,
            detail="Cannot delete the disciplines because it had related cards",
        ) from e
