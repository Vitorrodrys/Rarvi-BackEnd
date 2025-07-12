from typing import Callable, Generic, TypeVar

from fastapi import Depends, HTTPException, Path, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import crud
import models
import schemas
from services import jwt_handler


def get_db():
    with crud.db.SessionLocal() as session:
        yield session


def _handle_jwt_error(jwt_exception: jwt_handler.JWTInvalidTokenException) -> None:
    match jwt_exception.cause:
        case jwt_handler.JWTErrorEnum.EXPIRED:
            raise HTTPException(status_code=401, detail="Token expired")
        case jwt_handler.JWTErrorEnum.UNRECOGNIZED:
            raise HTTPException(status_code=401, detail="Invalid token")
        case jwt_handler.JWTErrorEnum.BROKEN:
            raise HTTPException(status_code=401, detail="Broken token")
        case _:
            raise HTTPException(status_code=500, detail="Internal server error")


def get_auth_token(
    request: Request,
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer()),
    db_session: Session = Depends(get_db),
) -> schemas.JWTAuthSchema:
    client_ip = request.client.host
    token = credentials.credentials
    try:
        jwt = jwt_handler.JWTHandler.from_jwt(token)
        if crud.user.get(db_session, jwt.user_id) is None:
            raise HTTPException(
                status_code=401, detail="User associated with token not found"
            )
        checker = jwt_handler.JWTHandler(jwt=jwt)
        checker.check()
        if client_ip != jwt.requested_from:
            raise HTTPException(status_code=401, detail="IP address mismatch")
        return jwt
    except jwt_handler.JWTInvalidTokenException as e:
        _handle_jwt_error(e)


ResourceType = TypeVar("ResourceType", bound=models.Base)


class ResourceOwnershipChecker(Generic[ResourceType]):
    def __init__(
        self,
        resource_getter: Callable[[Session, int], ResourceType],
        owner_id_getter: Callable[[ResourceType], int],
        resource_name: str,
    ):
        self.__resource_getter = resource_getter
        self.__owner_id_getter = owner_id_getter
        self.__resource_name = resource_name

    def __call__(
        self,
        resource_id_alias: str,
    ) -> Callable[[int, schemas.JWTAuthSchema, Session], ResourceType]:
        def checker(
            resource_id: int = Path(..., alias=resource_id_alias),
            auth_session: schemas.JWTAuthSchema = Depends(get_auth_token),
            db_session: Session = Depends(get_db),
        ) -> ResourceType:
            resource = self.__resource_getter(db_session, resource_id)
            if not resource:
                raise HTTPException(
                    status_code=404, detail=f"{self.__resource_name} not found"
                )
            if self.__owner_id_getter(resource) != auth_session.user_id:
                raise HTTPException(
                    status_code=403, detail=f"Unauthorized access to {self.__resource_name}"
                )
            return resource
        return checker
