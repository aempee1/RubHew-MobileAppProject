import pytest
from httpx import AsyncClient
from rubhew import models

@pytest.mark.asyncio
async def test_create_user(client: AsyncClient, user1: models.DBUser):
    payload = {
        "username": "new_user",
        "email": "new_user@example.com",
        "first_name": "New First",
        "last_name": "New Last",
        "password": "password123"
    }
    response = await client.post("/users/create", json=payload)
    
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["first_name"] == payload["first_name"]
    assert data["last_name"] == payload["last_name"]

