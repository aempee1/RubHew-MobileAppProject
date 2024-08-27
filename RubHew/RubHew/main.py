# main.py
from contextlib import asynccontextmanager
from fastapi import FastAPI

from config import *
from models import *
from router import *

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    if engine is not None:
        # Close the DB connection
        await close_session()


def create_app(settings=None):
    if not settings:
        settings = get_settings()

    app = FastAPI(lifespan=lifespan)

    init_db(settings)

    init_router(app)

    return app


app = create_app()