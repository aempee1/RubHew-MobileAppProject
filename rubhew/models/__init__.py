from typing import Optional, AsyncIterator

from sqlmodel import Field, SQLModel, create_engine, Session, select
from sqlmodel.ext.asyncio.session import AsyncSession

from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from sqlalchemy.orm import sessionmaker

from . import users
from . import profiles
from . import items
from . import transactions

from .users import *
from .profiles import *
from .items import *
from .transactions import *

connect_args = {}

engine: Optional[AsyncEngine] = None

def init_db(settings):
    global engine

    # Select the database URL based on whether we are testing
    db_url = settings.TEST_SQLDB_URL if settings.TESTING else settings.SQLDB_URL

    engine = create_async_engine(
        db_url,
        echo=True,
        future=True,
        connect_args=connect_args,
    )
    print(f"Database engine initialized with URL: {db_url}")

async def recreate_table():
    try:
        async with engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.drop_all)
            await conn.run_sync(SQLModel.metadata.create_all)
    except Exception as e:
        print(f"Error creating tables: {e}")

async def get_session() -> AsyncIterator[AsyncSession]:
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

async def close_session():
    global engine
    if engine is None:
        raise Exception("DatabaseSessionManager is not initialized")
    await engine.dispose()
