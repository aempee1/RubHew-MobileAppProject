import pytest
from httpx import AsyncClient
from rubhew import config, models, main

@pytest.fixture(scope="session")
def settings():
    # Return settings configured for testing
    return config.get_settings(testing=True)

@pytest.fixture(scope="session")
async def app(settings):
    # Create and configure the FastAPI app
    app = main.create_app(settings=settings)
    # Ensure the test database schema is created
    async with models.get_session() as session:
        await models.recreate_table()
        yield app
    await models.close_session()

@pytest.fixture(scope="session")
async def client(app):
    # Create an AsyncClient to make requests to the FastAPI app
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture(scope="function", autouse=True)
async def clean_test_db():
    # Clean the test database before each test
    await models.recreate_table()
