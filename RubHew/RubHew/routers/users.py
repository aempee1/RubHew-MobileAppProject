from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from typing import Annotated

from .. import deps
from .. import models

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(current_user: models.User = Depends(deps.get_current_user)) -> models.User:
    return current_user


@router.get("/{user_id}")
async def get(
    user_id: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:

    user = await session.get(models.DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )
    return user


@router.post("/create")
async def create(
    user_info: models.RegisteredUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.User:

    result = await session.exec(
        select(models.DBUser).where(models.DBUser.username == user_info.username)
    )

    user = result.one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is exists.",
        )

    user = models.DBUser.from_orm(user_info)
    await user.set_password(user_info.password)
    session.add(user)
    await session.commit()

    return user

@router.put("/change_password")
async def change_password(
    password_update: models.ChangedPassword,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:

    # Verify the current password
    if not await current_user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password",
        )

    # Set the new password
    await current_user.set_password(password_update.new_password)

    # Update the user in the database
    session.add(current_user)
    await session.commit()

    return {"message": "Password updated successfully"}


@router.put("/update")
async def update_user(
    user_update: models.UpdatedUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:

    # Ensure that the user exists (current_user should already be validated)
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Update the user's information
    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, key, value)

    # Save the changes to the database
    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return current_user