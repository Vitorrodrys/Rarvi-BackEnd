from datetime import datetime, timezone

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from api.deps import get_db, get_auth_token
import crud
import schemas


card_router = APIRouter()


@card_router.get("/card/{card_id}", response_model=schemas.CardSchema)
def get_card(
    card_id: int,
    auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
) -> schemas.CardSchema:
    db_card = crud.card.get(db_session, card_id)
    if db_card.discipline.user_id != auth_session.user_id:
        raise HTTPException(status_code=403, detail="Only can read your own cards")
    db_card = crud.card.update(
        db_session,
        db_card,
        schemas.CardCommitSchema(last_viewed_at=datetime.now(timezone.utc)),
    )
    return db_card


@card_router.post("/card", response_model=schemas.CardSchema)
def create_card(
    auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
    card: schemas.CardCreateSchema = Body(...),
) -> schemas.CardSchema:
    linked_discipline = crud.discipline.get(db_session, card.discipline_id)
    if not linked_discipline:
        raise HTTPException(status_code=404, detail="Discipline not found")
    if linked_discipline.user_id != auth_session.user_id:
        raise HTTPException(
            status_code=403,
            detail="You cannot associate the card with a discipline you do not own",
        )
    card_commit = schemas.CardCommitSchema.model_validate(card)
    card_commit.last_viewed_at = datetime.now(timezone.utc)
    return crud.card.create(db_session, card_commit)


@card_router.patch("/card/{card_id}", response_model=schemas.CardSchema)
def update(
    card_id: int,
    auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
    card: schemas.CardUpdateSchema = Body(...),
) -> schemas.CardSchema:
    db_card = crud.card.get(db_session, card_id)
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    if db_card.discipline.user_id != auth_session.user_id:
        raise HTTPException(
            status_code=403, detail="You cannot update a card that you do not own"
        )
    card_commit = schemas.CardCommitSchema(**card.model_dump(exclude_unset=True))
    card_commit.last_viewed_at = datetime.now(timezone.utc)
    db_card = crud.card.update(db_session, db_card, card_commit)
    return db_card


@card_router.delete("/card/{card_id}", response_model=schemas.CardSchema)
def delete_card(
    card_id: int,
    auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
) -> schemas.CardSchema:
    db_card = crud.card.get(db_session, card_id)
    if not db_card:
        raise HTTPException(status_code=404, detail="Card not found")
    if db_card.discipline.user_id != auth_session.user_id:
        raise HTTPException(
            status_code=403, detail="You cannot delete a card that you do not own"
        )
    return crud.card.delete(db_session, card_id)


@card_router.get("/cards", response_model=list[schemas.CardSchema])
def get_cards(
    auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
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
    if from_date and not to_date:
        raise HTTPException(
            status_code=400,
            detail="You must specify an end date for the time interval.",
        )
    if not from_date and to_date:
        raise HTTPException(
            status_code=400,
            detail="You must specify a start date for the time interval.",
        )

    if from_date and to_date:
        return crud.card.get_cards_by_period(
            db_session,
            auth_session.user_id,
            from_date,
            to_date,
            discipline_id=discipline_id,
            limit=limit,
            offset=skip,
        )
    return crud.card.get_cards(
        db_session,
        auth_session.user_id,
        discipline_id=discipline_id,
        limit=limit,
        offset=skip,
    )

@card_router.get("/count")
def count_cards(
    auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
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
