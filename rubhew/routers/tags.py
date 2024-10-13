
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Annotated

from .. import models, deps

router = APIRouter(prefix="/tags", tags=["tags"])

# Dependency to ensure user is active super user
async def active_super_user(current_user: models.DBUser = Depends(deps.get_current_user)):
    if not current_user.is_active or not current_user.is_superuser:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions")

@router.post("/", response_model=models.TagsRead, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag: models.TagsCreate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.DBUser, Depends(deps.get_current_active_superuser)]
) -> models.TagsRead:
    new_tag = models.Tags(**tag.dict())
    session.add(new_tag)
    await session.commit()
    await session.refresh(new_tag)
    return new_tag

@router.get("/", response_model=List[models.TagsRead])
async def list_tags(session: Annotated[AsyncSession, Depends(models.get_session)]):
    statement = select(models.Tags)
    results = await session.exec(statement)
    return results.all()

@router.get("/{tag_id}", response_model=models.TagsRead)
async def get_tag(
    tag_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.DBUser, Depends(active_super_user)]
):
    tag = await session.get(models.Tags, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    return tag

@router.put("/{tag_id}", response_model=models.TagsRead)
async def update_tag(
    tag_id: int,
    tag_update: models.TagsCreate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.DBUser, Depends(deps.get_current_active_superuser)]
):
    tag = await session.get(models.Tags, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    
    tag.name_tags = tag_update.name_tags  # Update fields as necessary
    session.add(tag)
    await session.commit()
    await session.refresh(tag)
    return tag

@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.DBUser, Depends(deps.get_current_active_superuser)]
):
    tag = await session.get(models.Tags, tag_id)
    if not tag:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Tag not found")
    
    await session.delete(tag)
    await session.commit()
