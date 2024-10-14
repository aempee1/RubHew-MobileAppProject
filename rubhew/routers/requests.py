from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Annotated
from datetime import datetime

from .. import models, deps  # Assuming models.py contains the Request model and deps has the get_current_user function

router = APIRouter(prefix="/requests", tags=["requests"])

@router.post("/", response_model=models.RequestRead, status_code=status.HTTP_201_CREATED)
async def create_request(
    request_data: models.RequestCreate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.Request:
    # Check if the item exists
    item = await session.get(models.Item, request_data.id_item)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Item not found")
    
    # Ensure the requester is not the owner of the item
    if item.id_user == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot request your own item")

    # Create the request
    new_request = models.Request(
        id_sent=current_user.id,  # Automatically use the current user's ID
        id_receive=item.id_user,   # Derive the receiver's ID from the item's owner
        id_item=request_data.id_item,
        message=request_data.message,
        create_time=datetime.utcnow(),
        update_time=datetime.utcnow()
    )

    # Add the new request to the session
    session.add(new_request)

    # Update the status of the item to "Progress"
    item.status = "Progress"
    session.add(item)  # Mark the item for commit

    # Commit the session
    await session.commit()
    
    # Refresh the new request to get the updated data
    await session.refresh(new_request)

    return new_request





@router.get("/my-requests", response_model=List[models.RequestDetailRead])
async def get_my_requests(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> List[models.RequestDetailRead]:
    # Fetch requests where the current user is either the sender or receiver
    statement = select(models.Request).where(
        (models.Request.id_sent == current_user.id) | (models.Request.id_receive == current_user.id)
    )
    results = await session.exec(statement)
    requests = results.all()

    # Fetch user and item details
    request_details = []
    for request in requests:
        sender = await session.get(models.DBUser, request.id_sent)
        receiver = await session.get(models.DBUser, request.id_receive)
        item = await session.get(models.Item, request.id_item)

        if sender and receiver and item:
            request_detail = models.RequestDetailRead(
                id=request.id,
                id_sent=request.id_sent,
                id_receive=request.id_receive,
                id_item=request.id_item,
                message=request.message,
                res_message=request.res_message,
                create_time=request.create_time,
                update_time=request.update_time,
                sender=models.UserDetail(
                    username=sender.username,
                    email=sender.email,
                    first_name=sender.first_name,
                    last_name=sender.last_name
                ),
                receiver=models.UserDetail(
                    username=receiver.username,
                    email=receiver.email,
                    first_name=receiver.first_name,
                    last_name=receiver.last_name
                ),
                item=models.ItemDetail(
                    id_item=item.id_item,
                    name_item=item.name_item,
                    images=item.images  # Assuming images is a list of strings
                )
            )
            request_details.append(request_detail)

    return request_details


@router.get("/", response_model=List[models.RequestDetailRead])
async def get_all_requests(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> List[models.RequestDetailRead]:
    # Fetch all requests from the database (consider admin authorization here)
    statement = select(models.Request)
    results = await session.exec(statement)
    requests = results.all()

    # Fetch user and item details
    request_details = []
    for request in requests:
        sender = await session.get(models.DBUser, request.id_sent)
        receiver = await session.get(models.DBUser, request.id_receive)
        item = await session.get(models.Item, request.id_item)

        if sender and receiver and item:
            request_detail = models.RequestDetailRead(
                id=request.id,
                id_sent=request.id_sent,
                id_receive=request.id_receive,
                id_item=request.id_item,
                message=request.message,
                res_message=request.res_message,
                create_time=request.create_time,
                update_time=request.update_time,
                sender=models.UserDetail(
                    username=sender.username,
                    email=sender.email,
                    first_name=sender.first_name,
                    last_name=sender.last_name
                ),
                receiver=models.UserDetail(
                    username=receiver.username,
                    email=receiver.email,
                    first_name=receiver.first_name,
                    last_name=receiver.last_name
                ),
                item=models.ItemDetail(
                    id_item=item.id_item,
                    name_item=item.name_item,
                    images=item.images  # Assuming images is a list of strings
                )
            )
            request_details.append(request_detail)

    return request_details



# Update a request's message or response message
@router.put("/{request_id}", response_model=models.RequestRead)
async def update_request_message(
    request_id: int,
    updated_data: models.RequestUpdate,  # Contains the new message or res_message
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.Request:
    # Fetch the request
    request = await session.get(models.Request, request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")
    
    # Ensure the current user is either the sender or receiver of the request
    if request.id_sent != current_user.id and request.id_receive != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this request")

    # Update the message or response message
    if updated_data.message:
        if request.id_sent == current_user.id:
            request.message = updated_data.message  # Only the sender can update the message
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the sender can update the message")
    
    if updated_data.res_message:
        if request.id_receive == current_user.id:
            request.res_message = updated_data.res_message  # Only the receiver can update the response message
        else:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the receiver can update the response message")

    request.update_time = datetime.utcnow()  # Update the timestamp
    session.add(request)
    await session.commit()
    await session.refresh(request)

    return request


# Delete a request (only if the request belongs to the user)
@router.delete("/{request_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_request(
    request_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
):
    # Fetch the request
    request = await session.get(models.Request, request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    # Ensure the current user is either the sender or receiver of the request
    if request.id_sent != current_user.id and request.id_receive != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this request")

    # Fetch the associated item
    item = await session.get(models.Item, request.id_item)
    if not item:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Associated item not found")

    # Change item status back to "Available"
    item.status = "Available"
    session.add(item)  # Mark the updated item for commit

    # Delete the request
    await session.delete(request)

    # Commit the session
    await session.commit()

    return

@router.put("/{request_id}/respond", response_model=models.RequestRead)
async def respond_to_request(
    request_id: int,
    response_data: models.RequestUpdate,  # This should include `res_message` and the new `item_status`
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.Request:
    # Fetch the request
    request = await session.get(models.Request, request_id)
    if not request:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Request not found")

    # Ensure the current user is the receiver of the request
    if request.id_receive != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to respond to this request")

    # Update the response message
    if response_data.res_message:
        request.res_message = response_data.res_message  # Update the response message

    # Update the status of the item if provided
    if response_data.item_status:
        item = await session.get(models.Item, request.id_item)
        if item:
            item.status = response_data.item_status  # Update item status
            session.add(item)  # Mark the item for commit

    request.update_time = datetime.utcnow()  # Update the timestamp
    session.add(request)  # Mark the request for commit
    await session.commit()
    await session.refresh(request)

    return request
