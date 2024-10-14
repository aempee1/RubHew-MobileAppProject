from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Annotated
from datetime import datetime

from .. import models, deps  # Assuming models.py contains the Request model and deps has the get_current_user function

router = APIRouter(prefix="/requests", tags=["requests"])

# Create a new request
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
        id_sent=current_user.id,
        id_receive=item.id_user,
        id_item=request_data.id_item,
        message=request_data.message,
        create_time=datetime.utcnow(),
        update_time=datetime.utcnow()
    )

    session.add(new_request)
    await session.commit()
    await session.refresh(new_request)

    return new_request


# Get all requests (admin route or for debugging)
@router.get("/", response_model=List[models.RequestRead])
async def get_all_requests(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> List[models.RequestRead]:
    # Fetch all requests from the database (consider admin authorization here)
    statement = select(models.Request)
    results = await session.exec(statement)
    requests = results.all()

    return requests


# Get requests related to the current user (both sent and received)
@router.get("/my-requests", response_model=List[models.RequestRead])
async def get_my_requests(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> List[models.RequestRead]:
    # Fetch requests where the current user is either the sender or receiver
    statement = select(models.Request).where(
        (models.Request.id_sent == current_user.id) | (models.Request.id_receive == current_user.id)
    )
    results = await session.exec(statement)
    requests = results.all()

    return requests


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

    await session.delete(request)
    await session.commit()

    return
