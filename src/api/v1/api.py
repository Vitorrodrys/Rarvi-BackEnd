from fastapi import APIRouter

from api.v1.endpoints.card import card_router
from api.v1.endpoints.discipline import discipline_router
from api.v1.endpoints.user import user_router

api_router = APIRouter()

api_router.include_router(card_router, prefix="/cards", tags=["cards"])
api_router.include_router(discipline_router, prefix="/disciplines", tags=["disciplines"])
api_router.include_router(user_router, prefix="/user", tags=["user"])
