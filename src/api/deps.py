from fastapi import Depends, Header, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

import crud
from schemas import JWTAuthSchema
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

def get_auth_token(credentials: HTTPAuthorizationCredentials = Header(HTTPBearer()), db_session:Session = Depends(get_db)) -> JWTAuthSchema:
    token = credentials.credentials
    try:
        jwt = jwt_handler.JWTHandler.from_jwt(token)
        if crud.crud_user.get(db_session, jwt.user_id) is None:
            raise HTTPException(status_code=401, detail="User associated with token not found")
        checker = jwt_handler.JWTHandler(jwt=jwt)
        checker.check()
        return jwt
    except jwt_handler.JWTInvalidTokenException as e:
        _handle_jwt_error(e)
