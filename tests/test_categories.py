import pytest
from sqlmodel import SQLModel
from httpx import AsyncClient
from rubhew.models import CategoryCreate, CategoryRead

@pytest.mark.asyncio
async def test_create_category(client: AsyncClient, token_user1: dict):
    # Set the headers for authentication
    headers = {"Authorization": f"Bearer {token_user1['access_token']}"}
    
    # Define the category data to be created
    category_data = {
        "name_category": "Test Category",
        "category_image": "http://example.com/image.jpg"
    }
    
    # Make a POST request to create a category
    response = await client.post(
        "/categories/",
        json=category_data,
        headers=headers
    )
    
    # Assert the response status code and data
    assert response.status_code == 201
    assert response.json()["name_category"] == category_data["name_category"]
    assert response.json()["category_image"] == category_data["category_image"]


@pytest.mark.asyncio
async def test_get_category(client: AsyncClient, token_user1: dict):
    # Set the headers for authentication
    headers = {"Authorization": f"Bearer {token_user1['access_token']}"}

    # First, create a category to retrieve later
    category_data = {
        "name_category": "Test Category for Get",
        "category_image": "http://example.com/image.jpg"
    }
    create_response = await client.post(
        "/categories/",
        json=category_data,
        headers=headers
    )
    
    category_id = create_response.json()["id_category"]

    # Now retrieve the created category
    get_response = await client.get(
        f"/categories/{category_id}",
        headers=headers
    )
    
    # Assert the response status code and data
    assert get_response.status_code == 200
    assert get_response.json()["id_category"] == category_id
    assert get_response.json()["name_category"] == category_data["name_category"]
    assert get_response.json()["category_image"] == category_data["category_image"]
