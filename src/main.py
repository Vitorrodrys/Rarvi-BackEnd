from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api import api_router
from core import log, settings
from crud.db import create_all
from models import Base
from notification_handler.worker import create_worker

log.init_logging()
create_all(Base)

env_settings = settings.get()

app = FastAPI()

origins = [
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(api_router, prefix=env_settings.VERSION_PREFIX)
create_worker()
