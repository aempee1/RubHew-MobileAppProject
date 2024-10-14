from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Annotated
from sqlalchemy import delete  # เพิ่มการนำเข้าคำสั่ง delete

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
) -> models.ItemRead:
    # Fetch the item to be updated
    item = await session.get(models.Item, item_id)

    # Check if the item exists and belongs to the current user
    if not item or item.id_user != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # If category_id is provided, validate that it exists
    if item_update.category_id is not None:
        category = await session.get(models.Category, item_update.category_id)
        if not category:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category")

    # Update the item with the provided fields, excluding unset fields
    for key, value in item_update.dict(exclude_unset=True).items():
        if key != "tags":  # Skip 'tags' update here
            setattr(item, key, value)

    # Update the tags if provided
    if item_update.tags is not None:
        # Clear existing tags
        await session.execute(
            delete(models.ItemTagsLink).where(models.ItemTagsLink.item_id == item_id)
        )
        # Add updated tags
        for tag_id in item_update.tags:
            new_link = models.ItemTagsLink(item_id=item_id, tag_id=tag_id)
            session.add(new_link)

    # Add the updated item to the session
    session.add(item)
    
    # Commit the transaction
    await session.commit()
    
    # Refresh the item to get the updated data
    await session.refresh(item)

    # Fetch the updated tags for the item
    tags_links = await session.execute(
        select(models.Tags).join(models.ItemTagsLink).where(models.ItemTagsLink.item_id == item_id)
    )
    tags = tags_links.scalars().all()

    # Construct the ItemRead object with the updated tags
    item_read = models.ItemRead(
        id_user=item.id_user,
        id_item=item.id_item,
        name_item=item.name_item,
        description=item.description,
        price=item.price,
        images=item.images,
        status=item.status,
        detail=item.detail,
        category_id=item.category_id,
        tags=[models.TagsRead.from_orm(tag) for tag in tags],  # Map tags to TagsRead schema
        user_profile=models.UserProfile(  # Assume user data is available
            username=current_user.username,
            first_name=current_user.first_name,
            last_name=current_user.last_name
        )
    )

    # Return the updated item
    return item_read




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
