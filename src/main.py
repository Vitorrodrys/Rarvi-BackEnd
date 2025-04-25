from fastapi import FastAPI

from api import api_router
from core import log, settings
from crud.db import create_all
from models import Base

log.init_logging()
create_all(Base)

env_settings = settings.get()

app = FastAPI()
app.include_router(api_router, prefix=env_settings.VERSION_PREFIX)
