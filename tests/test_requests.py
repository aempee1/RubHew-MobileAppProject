import pytest
from sqlmodel import SQLModel
from httpx import AsyncClient
from rubhew.models import CategoryCreate, CategoryRead

@pytest.mark.asyncio
@pytest.fixture
async def db_session():
    engine = create_engine("sqlite+aiosqlite:///:memory:")  # Use in-memory SQLite for testing
    async with AsyncSession(engine) as session:
        async with session.begin():
            # Create the tables (if you haven't already)
            await SQLModel.metadata.create_all(engine)
        yield session
        await session.rollback()  # Rollback after test

@pytest.fixture
async def client(db_session):
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_user(db_session):
    # Create a test user in the database and return the user object
    user = DBUser(username="testuser", email="test@example.com", password="hashed_password")
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.mark.asyncio
async def test_create_request(client, db_session, test_user):
    # Create a test item (assuming you have an Item model)
    item = models.Item(name_item="Test Item", id_user=test_user.id, status="Available")
    db_session.add(item)
    await db_session.commit()
    await db_session.refresh(item)

    # Define the request data
    request_data = RequestCreate(id_item=item.id_item, message="Test request")

    # Send the create request
    response = await client.post(
        "/requests/",
        json=request_data.dict(),
        headers={"Authorization": f"Bearer {test_user.token}"},  # Add auth header if needed
    )

    # Assertions
    assert response.status_code == 201
    request_response = response.json()
    assert request_response["message"] == "Test request"
    assert request_response["id_sent"] == test_user.id
    assert request_response["id_item"] == item.id_item

@pytest.mark.asyncio
async def test_get_requests(client, db_session, test_user):
    # Assuming test_create_request has already created a request
    response = await client.get(
        "/requests/my-requests/",
        headers={"Authorization": f"Bearer {test_user.token}"},  # Add auth header if needed
    )

    # Assertions
    assert response.status_code == 200
    requests = response.json()
    assert len(requests) > 0  # Ensure there's at least one request
    assert requests[0]["id_sent"] == test_user.id
