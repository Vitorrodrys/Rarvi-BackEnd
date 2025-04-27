from fastapi import APIRouter, Body, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from api.deps import get_db, get_auth_token
import crud
import schemas
from services.jwt_handler import JWTHandler


user_router = APIRouter()


@user_router.get("/user/{user_id}", response_model=schemas.UserSchema)
def get_user(
    user_id: int,
    _: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
) -> schemas.UserSchema:
    """
    Get a user by ID.
    """
    user = crud.crud_user.get(db_session, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@user_router.get("/users", response_model=list[schemas.UserSchema])
def get_users(
    _: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
) -> list[schemas.UserSchema]:
    """
    Get a list of users with a Optional skip and limit range.
    """
    users = crud.crud_user.get_multi(db_session, skip=skip, limit=limit)
    return users


@user_router.post("/user", response_model=schemas.UserSchema)
def create_user(
    db_session: Session = Depends(get_db),
    user: schemas.UserCreateSchema = Body(...),
) -> schemas.UserSchema:
    """
    Create a new user.
    """
    user_commit = schemas.UserCommitSchema.model_validate(user)
    try:
        db_user = crud.crud_user.create(db_session, obj_in=user_commit)
    except IntegrityError as e:
        raise HTTPException(
            status_code=400, detail="User with this name or email already exists"
        ) from e
    return db_user


@user_router.patch("/user/{user_id}", response_model=schemas.UserSchema)
def update_user(
    user_id: int,
    auth_token: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
    user: schemas.UserUpdateSchema = Body(...),
) -> schemas.UserSchema:
    """
    Update a user fields by ID.
    """
    if user_id != auth_token.user_id:
        raise HTTPException(
            status_code=403, detail="A user can only update his own data"
        )
    db_user = crud.crud_user.get(db_session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_commit = schemas.UserCommitSchema.model_validate(
        user.model_dump(exclude_unset=True)
    )
    db_user = crud.crud_user.update(db_session, db_obj=db_user, obj_in=user_commit)
    return db_user


@user_router.delete("/user/{user_id}", response_model=schemas.UserSchema)
def delete_user(
    user_id: int,
    auth_token: schemas.JWTAuthSchema = Depends(get_auth_token),
    db_session: Session = Depends(get_db),
) -> schemas.UserSchema:
    """
    Delete a user by ID.
    """
    if user_id != auth_token.user_id:
        raise HTTPException(status_code=403, detail="A user can only delete themselves")
    db_user = crud.crud_user.get(db_session, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user = crud.crud_user.delete(db_session, user_id)
    return db_user


@user_router.post("/auth")
def auth_user(
    request: Request,
    db_session: Session = Depends(get_db),
    auth_creds: schemas.UserAuthSchema = Body(...),
) -> str:
    """
    Authenticate an user and return your corresponding JWT session if the credentials are correct.
    """
    db_user = None
    if auth_creds.email:
        db_user = crud.crud_user.get_by_email(db_session, auth_creds.email)
    elif auth_creds.name:
        db_user = crud.crud_user.get_by_name(db_session, auth_creds.name)
    else:
        raise HTTPException(status_code=400, detail="No email or name provided")
    if not db_user:
        raise HTTPException(status_code=401, detail="Unauthorized")
    if db_user.pass_checksum != auth_creds.pass_checksum:
        raise HTTPException(status_code=401, detail="Unauthorized")

    jwt_handler = JWTHandler(
        jwt=JWTHandler.from_model_user(db_user, requested_from=request.client.host)
    )
    return jwt_handler.to_jwt()
