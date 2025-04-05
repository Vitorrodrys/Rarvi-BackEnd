from fastapi import FastAPI

from api import api_router
from core import settings

env_settings = settings.get()

app = FastAPI()
app.include_router(api_router, prefix=env_settings.VERSION_PREFIX)

