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


@router.get("/{item_id}", response_model=models.ItemRead)
async def get_item(
    item_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.Item:
    item = await session.get(models.Item, item_id)
    if not item or item.id_user != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    return item


@router.get("/", response_model=List[models.ItemRead])
async def list_items(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> List[models.Item]:
    statement = select(models.Item).where(models.Item.id_user == current_user.id)
    results = await session.exec(statement)
    return results.all()


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
