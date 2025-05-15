from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from api import deps
import crud
import models
import schemas


card_router = APIRouter()

card_ownership_checker = deps.ResourceOwnershipChecker[models.Card](
    crud.card.get, lambda x: x.discipline.user_id, "card"
)


@card_router.patch("/card/{card_id}/view", response_model=schemas.CardSchema)
def get_card(
    db_card: models.Card = Depends(card_ownership_checker("card_id")),
    db_session: Session = Depends(deps.get_db),
) -> schemas.CardSchema:
    db_card = crud.card.update(
        db_session,
        db_card,
        schemas.CardCommitSchema(last_viewed_at=datetime.now(timezone.utc)),
    )
    return db_card


@card_router.post("/card", response_model=schemas.CardSchema)
def create_card(
    db_session: Session = Depends(deps.get_db),
    auth_session: schemas.JWTAuthSchema = Depends(deps.get_auth_token),
    card: schemas.CardCreateSchema = Body(...),
) -> schemas.CardSchema:
    db_discipline = crud.discipline.get(db_session, card.discipline_id)
    if not db_discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    if db_discipline.user_id != auth_session.user_id:
        raise HTTPException(status_code=403, detail="Unauthorized acess to discipline")
    card_commit = schemas.CardCommitSchema.model_validate(card)
    return crud.card.create(db_session, card_commit)


@card_router.patch("/card/{card_id}", response_model=schemas.CardSchema)
def update(
    db_card: models.Card = Depends(card_ownership_checker("card_id")),
    db_session: Session = Depends(deps.get_db),
    card: schemas.CardUpdateSchema = Body(...),
) -> schemas.CardSchema:
    card_commit = schemas.CardCommitSchema(**card.model_dump(exclude_unset=True))
    db_card = crud.card.update(db_session, db_card, card_commit)
    return db_card


@card_router.delete("/card/{card_id}", response_model=schemas.CardSchema)
def delete_card(
    db_card: models.Card = Depends(card_ownership_checker("card_id")),
    db_session: Session = Depends(deps.get_db),
) -> schemas.CardSchema:
    return crud.card.delete(db_session, db_card.id)


@card_router.get("/cards", response_model=list[schemas.SummarizedCardSchema])
def get_cards(
    auth_session: schemas.JWTAuthSchema = Depends(deps.get_auth_token),
    db_session: Session = Depends(deps.get_db),
    skip: int = 0,
    limit: int = 10,
    discipline_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> list[schemas.SummarizedCardSchema]:
    """
    Get the cards belonging to a user, optionally filtered by discipline and data range

    Args:
        skip (int, Optional): skip the results, making a paging of it
        limit (int, Optional): The max of objects must return case exceed
        discipline_id (int, Optional): An optional discipline to filter the cards
        from_date: (datetime, Optional): Start of the last_viewed_at interval. Defaults to 1970-01-01 if None
        to_date: (datetime, Optional): End of the last_viewed_at interval. Defaults to far future if None.

    Returns:
        The list of cards found by query.

    """
    return crud.card.get_cards_by_period(
        db_session,
        auth_session.user_id,
        from_date,
        to_date,
        discipline_id=discipline_id,
        limit=limit,
        offset=skip,
    )

@card_router.get("/count")
def count_cards(
    auth_session: schemas.JWTAuthSchema = Depends(deps.get_auth_token),
    db_session: Session = Depends(deps.get_db),
    discipline_id: int | None = None,
    from_date: datetime | None = None,
    to_date: datetime | None = None,
) -> int:
    """
    Count the number of cards belonging to a user, optionally filtered by discipline and date range.

    Args:
        discipline_id (int, optional): Discipline ID to filter cards.
        from_date (datetime, optional): Start of the last_viewed_at interval. Defaults to 1970-01-01 if None.
        to_date (datetime, optional): End of the last_viewed_at interval. Defaults to far future if None.

    Returns:
        int: Number of matching cards.
    """
    return crud.card.count(
        db_session,
        auth_session.user_id,
        discipline_id=discipline_id,
        from_time=from_date,
        to_time=to_date,
    )


@card_router.patch("/card/{card_id}/{card_feedback}", response_model=schemas.CardSchema)
def receive_card_feedback(
    card_feedback: schemas.CardDifficultyEnum,
    db_session: Session = Depends(deps.get_db),
    db_card: models.Card = Depends(card_ownership_checker("card_id")),
) -> schemas.CardSchema:
    db_card = crud.card.update_priority_weight(db_session, db_card, card_feedback)
    return db_card
