from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from api import deps
import crud
import models
import schemas


discipline_router = APIRouter()

discipline_ownership_checker = deps.ResourceOwnershipChecker[models.Discipline](
    crud.discipline.get, lambda x: x.user_id, "discipline"
)


@discipline_router.get("/disciplines", response_model=list[schemas.DisciplineSchema])
def get_user_disciplines(
    auth_session: schemas.JWTAuthSchema = Depends(deps.get_auth_token),
    db_session: Session = Depends(deps.get_db),
    skip: int | None = 0,
    limit: int | None = 10,
) -> list[schemas.DisciplineSchema]:
    disciplines = crud.discipline.get_disciplines_by_user(
        db_session, auth_session.user_id, offset=skip, limit=limit
    )
    return disciplines


@discipline_router.post("/discipline", response_model=schemas.DisciplineSchema)
def create_discipline(
    auth_session: schemas.JWTAuthSchema = Depends(deps.get_auth_token),
    db_session: Session = Depends(deps.get_db),
    discipline: schemas.DisciplineCreateSchema = Body(...),
) -> schemas.DisciplineSchema:
    try:
        discipline_commit = schemas.DisciplineCommitSchema.model_validate(discipline)
        discipline_commit.user_id = auth_session.user_id
        db_discipline = crud.discipline.create(db_session, discipline_commit)
        return db_discipline
    except IntegrityError as e:
        raise HTTPException(
            status_code=409, detail="discipline with this name already exists"
        ) from e


@discipline_router.patch(
    "/discipline/{discipline_id}", response_model=schemas.DisciplineSchema
)
def update_discipline(
    db_discipline: models.Discipline = Depends(discipline_ownership_checker("discipline_id")),
    db_session: Session = Depends(deps.get_db),
    discipline: schemas.DisciplineUpdateSchema = Body(...),
) -> schemas.DisciplineSchema:
    try:
        return crud.discipline.update(db_session, db_obj=db_discipline, obj_in=discipline)
    except IntegrityError as e:
        raise HTTPException(
            status_code=409, detail="The name of the discipline is already in using"
        ) from e


@discipline_router.delete(
    "/discipline/{discipline_id}", response_model=schemas.DisciplineSchema
)
def delete_discipline(
    db_discipline: models.Card = Depends(discipline_ownership_checker("discipline_id")),
    db_session: Session = Depends(deps.get_db),
) -> schemas.DisciplineSchema:
    try:
        return crud.discipline.delete(db_session, db_discipline.id)
    except IntegrityError as e:
        raise HTTPException(
            status_code=409,
            detail="Cannot delete the disciplines because it had related cards",
        ) from e


@discipline_router.patch(
    "/discipline/{discipline_id}/random-card/view", response_model=schemas.CardSchema
)
def get_random(
    db_discipline: models.Discipline = Depends(discipline_ownership_checker("discipline_id")),
    db_session: Session = Depends(deps.get_db),
    auth_session: schemas.JWTAuthSchema = Depends(deps.get_auth_token),
) -> schemas.CardSchema:
    db_card = crud.card.get_random_by_priority(
        db_session, auth_session.user_id, discipline_id=db_discipline.id
    )
    if not db_card:
        raise HTTPException(
            status_code=404,
            detail="No cards associated with discipline given"
        )
    db_card = crud.card.update(
        db_session,
        db_card,
        schemas.CardCommitSchema(last_viewed_at=datetime.now(timezone.utc)),
    )
    return db_card
