from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Annotated

from .. import models, deps

router = APIRouter(prefix="/items", tags=["items"])

@router.post("/", response_model=models.ItemPost, status_code=status.HTTP_201_CREATED)
async def create_item(
    item: models.ItemCreate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.Item:
    # Manually create an Item instance
    new_item = models.Item(
        name_item=item.name_item,
        description=item.description,
        price=item.price,
        images=item.images,
        status=item.status,
        detail=item.detail,
        category_id=item.category_id,
        id_user=current_user.id  # Assign the user ID here
    )

    # Save the item to the database
    session.add(new_item)
    await session.commit()
    await session.refresh(new_item)

    # Handle tags
    if item.tags:  # Check if there are tags to associate with the item
        for tag_id in item.tags:
            item_tag_link = models.ItemTagsLink(item_id=new_item.id_item, tag_id=tag_id)
            session.add(item_tag_link)

        await session.commit()  # Commit after adding tags

    return new_item


@router.get("/my-items/", response_model=List[models.ItemRead_Only])
async def get_user_items(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> List[models.ItemRead_Only]:
    # Fetch items for the current user
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

        # Fetch the tags linked to the item
        tags = []
        item_tags = await session.exec(
            select(models.ItemTagsLink).where(models.ItemTagsLink.item_id == item.id_item)
        )
        for item_tag in item_tags:
            tag = await session.get(models.Tags, item_tag.tag_id)
            if tag:
                tags.append(models.TagsRead(
                    id_tags=tag.id_tags,
                    name_tags=tag.name_tags
                ))

        # Add the item with category details and tags to the response
        item_reads.append(models.ItemRead_Only(
           
            id_item=item.id_item,
            name_item=item.name_item,
            description=item.description,
            price=item.price,
            images=item.images,
            status=item.status,
            detail=item.detail,
            category_id=item.category_id,
            tags=tags,
        ))

    return item_reads



@router.get("/", response_model=List[models.ItemRead])
async def list_items(
    session: Annotated[AsyncSession, Depends(models.get_session)]
):
    # Fetch all items from the database
    statement = select(models.Item)
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

        # Fetch the tags linked to the item
        tags = []
        item_tags = await session.exec(
            select(models.ItemTagsLink).where(models.ItemTagsLink.item_id == item.id_item)
        )
        for item_tag in item_tags:
            tag = await session.get(models.Tags, item_tag.tag_id)
            if tag:
                tags.append(models.TagsRead(
                    id_tags=tag.id_tags,
                    name_tags=tag.name_tags
                ))
        # Fetch user profile details using id_user from the item
        user_profile = None
        if item.id_user:
            user = await session.get(models.DBUser, item.id_user) 
            if user:
                user_profile = {
                    "username": user.username,  # Adjust according to your user model fields
                    "first_name" : user.first_name,
                    "last_name" : user.last_name

                }
        # Add the item with category details and tags to the response list
        item_reads.append(models.ItemRead(
            id_user=item.id_user,
            id_item=item.id_item,
            name_item=item.name_item,
            description=item.description,
            price=item.price,
            images=item.images,
            status=item.status,
            detail=item.detail,
            category_id=item.category_id,
            tags=tags,  # Include tags in the response
            user_profile=user_profile 
        ))

    return item_reads



@router.get("/{item_id}", response_model=models.ItemRead_Only)
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

    # Fetch the tags linked to the item
    tags = []
    item_tags = await session.exec(
        select(models.ItemTagsLink).where(models.ItemTagsLink.item_id == item.id_item)
    )
    for item_tag in item_tags:
        tag = await session.get(models.Tags, item_tag.tag_id)
        if tag:
            tags.append(models.TagsRead(
                id_tags=tag.id_tags,
                name_tags=tag.name_tags  # Assuming your Tags model has a name_tags field
            ))

    # Return the item with category and tags
    return models.ItemRead_Only(
        id_item=item.id_item,
        name_item=item.name_item,
        description=item.description,
        price=item.price,
        images=item.images,
        status=item.status,
        detail=item.detail,
        category_id=item.category_id,
        tags=tags  # Include tags in the response
    )



@router.put("/{item_id}", response_model=models.ItemRead)
async def update_item(
    item_id: int,
    item_update: models.ItemUpdate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.ItemRead:  # Changed return type to ItemRead
    item = await session.get(models.Item, item_id)
    if not item or item.id_user != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")

    # Update the item with the provided fields
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
