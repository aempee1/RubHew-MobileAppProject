from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Annotated

from .. import models, deps

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=models.ItemRead, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: models.ItemCreate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.Item:
    new_item = models.Item.from_orm(item)
    new_item.id_user = current_user.id

    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)

    return new_item


@router.get("/{item_id}")
async def get_item(
    item_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
):
    # Fetch the item first
    item = await session.get(models.Item, item_id)
    
    if not item or item.id_user != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # Fetch the category using the category_id from the item
    category_details = None
    if item.category_id:
        category = await session.get(models.Category, item.category_id)
        if category:
            category_details = {
                "name_category": category.name_category,
                "category_image": category.category_image
            }

    # Return the item with manually added category details
    return {
        "id_item": item.id_item,
        "name_item": item.name_item,
        "description": item.description,
        "price": item.price,
        "image": item.image,
        "detail": item.detail,
        "category_id": item.category_id,
        "category_details": category_details  # Adding the category details manually
    }




@router.get("/")
async def list_items(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
):
    # Fetch all items for the current user
    statement = select(models.Item).where(models.Item.id_user == current_user.id)
    results = await session.exec(statement)
    items = results.all()

    item_reads = []
    for item in items:
        # Fetch the category using the category_id from the item
        category_details = None
        if item.category_id:
            category = await session.get(models.Category, item.category_id)
            if category:
                category_details = {
                    "name_category": category.name_category,
                    "category_image": category.category_image
                }
        
        # Add the item with manually added category details to the response list
        item_reads.append({
            "id_item": item.id_item,
            "name_item": item.name_item,
            "description": item.description,
            "price": item.price,
            "image": item.image,
            "detail": item.detail,
            "category_id": item.category_id,
            "category_details": category_details  # Adding category details manually
        })
    
    return item_reads


@router.put("/{item_id}", response_model=models.ItemRead)
async def update_item(
    item_id: int,
    item_update: models.ItemUpdate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.Item:
    item = await session.get(models.Item, item_id)
    if not item or item.id_user != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    for key, value in item_update.dict(exclude_unset=True).items():
        setattr(item, key, value)

    session.add(item)
    await session.commit()
    await session.refresh(item)

    return item


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_item(
    item_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
):
    item = await session.get(models.Item, item_id)
    if not item or item.id_user != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    await session.delete(item)
    await session.commit()
