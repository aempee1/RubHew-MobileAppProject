from httpx import AsyncClient
from rubhew import models
import pytest


@pytest.mark.asyncio
async def test_no_permission_create_merchants(
    client: AsyncClient, user1: models.DBUser
):
    payload = {"name": "merchants", "user_id": user1.id}
    response = await client.post("/merchants", json=payload)

    assert response.status_code == 401