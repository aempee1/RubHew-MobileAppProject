from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Annotated

from .. import models, deps

router = APIRouter(prefix="/categories", tags=["categories"])

# Create a new category
@router.post("/", response_model=models.CategoryRead, status_code=status.HTTP_201_CREATED)
async def create_category(
    category: models.CategoryCreate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.Category:
    statement = select(models.Category).where(models.Category.name_category == category.name_category)
    result = await session.exec(statement)
    existing_category = result.first()

    if existing_category:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Category name already exists")

    new_category = models.Category.from_orm(category)

    session.add(new_category)
    await session.commit()
    await session.refresh(new_category)

    return new_category


# Get a category by ID
@router.get("/{category_id}", response_model=models.CategoryRead)
async def get_category(
    category_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.Category:
    category = await session.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    return category


# List all categories
@router.get("/", response_model=List[models.CategoryRead])
async def list_categories(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> List[models.Category]:
    statement = select(models.Category)
    results = await session.exec(statement)
    return results.all()


# Update a category by ID
@router.put("/{category_id}", response_model=models.CategoryRead)
async def update_category(
    category_id: int,
    category_update: models.CategoryCreate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.Category:
    category = await session.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    for key, value in category_update.dict(exclude_unset=True).items():
        setattr(category, key, value)

    session.add(category)
    await session.commit()
    await session.refresh(category)

    return category


# Delete a category by ID
@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
):
    category = await session.get(models.Category, category_id)
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    await session.delete(category)
    await session.commit()
