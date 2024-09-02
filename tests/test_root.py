from httpx import AsyncClient
import pytest

@pytest.mark.asyncio
async def test_root_endpoint(client: AsyncClient):
    # Make a GET request to the root endpoint
    response = await client.get("/")

    # Assert the response status code and content
    assert response.status_code == 200
    assert response.json() == {"message": "RubHew API"}
