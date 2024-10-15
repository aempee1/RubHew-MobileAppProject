import pytest
from sqlmodel import SQLModel
from httpx import AsyncClient
from rubhew.models import TagsCreate, TagsRead

@pytest.mark.asyncio
async def test_create_tag(client: AsyncClient, token_user1: dict):
    # Set the headers for authentication
    headers = {"Authorization": f"Bearer {token_user1['access_token']}"}
    
    # Define the tag data to be created
    tag_data = {
        "name_tags": "Test Tag"
    }
    
    # Make a POST request to create a tag
    response = await client.post(
        "/tags/",
        json=tag_data,
        headers=headers
    )
    
    # Assert the response status code and data
    assert response.status_code == 201
    assert response.json()["name_tags"] == tag_data["name_tags"]


@pytest.mark.asyncio
async def test_get_tag(client: AsyncClient, token_user1: dict):
    # Set the headers for authentication
    headers = {"Authorization": f"Bearer {token_user1['access_token']}"}

    # First, create a tag to retrieve later
    tag_data = {
        "name_tags": "Test Tag for Get"
    }
    create_response = await client.post(
        "/tags/",
        json=tag_data,
        headers=headers
    )
    
    tag_id = create_response.json()["id_tags"]

    # Now retrieve the created tag
    get_response = await client.get(
        f"/tags/{tag_id}",
        headers=headers
    )
    
    # Assert the response status code and data
    assert get_response.status_code == 200
    assert get_response.json()["id_tags"] == tag_id
    assert get_response.json()["name_tags"] == tag_data["name_tags"]
