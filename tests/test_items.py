import pytest
from sqlmodel import SQLModel
from httpx import AsyncClient
from rubhew.models import CategoryCreate, CategoryRead

@pytest.mark.asyncio
async def test_create_item(client, create_category, create_tag, user_token):
    item_data = {
        "name_item": "Smartphone",
        "description": "Latest model smartphone.",
        "price": 699.99,
        "images": ["image1_url", "image2_url"],
        "status": "Available",
        "detail": {"color": "black", "memory": "128GB"},
        "category_id": create_category.id_category,
        "tags": [create_tag.id_tags]
    }

    response = await client.post("/items/", json=item_data, headers={"Authorization": f"Bearer {user_token}"})

    assert response.status_code == 201
    assert response.json()["name_item"] == item_data["name_item"]
    assert response.json()["category_id"] == create_category.id_category

@pytest.mark.asyncio
async def test_list_items(client, user_token):
    response = await client.get("/items/", headers={"Authorization": f"Bearer {user_token}"})
    
    assert response.status_code == 200
    assert isinstance(response.json(), list)  # Check that the response is a list