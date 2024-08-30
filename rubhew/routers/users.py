from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlmodel import select

from typing import Annotated, List

from .. import deps
from .. import models

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(current_user: models.User = Depends(deps.get_current_user)) -> models.User:
    return current_user


@router.get("/{user_id}", response_model=models.User)
async def get_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.User:
    user = await session.get(models.DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return user


@router.get("/", response_model=List[models.User])
async def list_users(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_active_superuser),  # Only admin can list users
) -> List[models.User]:
    users = await session.exec(select(models.DBUser))
    return users.all()


@router.post("/create", response_model=models.User)
async def create_user(
    user_info: models.RegisteredUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.User:
    existing_user = await session.exec(
        select(models.DBUser).where(models.DBUser.username == user_info.username)
    )
    if existing_user.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    user = models.DBUser.from_orm(user_info)
    await user.set_password(user_info.password)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    profile = models.DBProfile(user_id=user.id)
    session.add(profile)
    await session.commit()

    return user

@router.post("/createsuper", response_model=models.User)
async def create_user(
    user_info: models.RegisterSuperUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
) -> models.RegisterSuperUser:
    existing_user = await session.exec(
        select(models.DBUser).where(models.DBUser.username == user_info.username)
    )
    if existing_user.one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists.",
        )

    user = models.DBUser.from_orm(user_info)
    await user.set_password(user_info.password)
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return user

@router.put("/update")
async def update_user(
    user_update: models.UpdateUser,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) ->JSONResponse :
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    for key, value in user_update.dict(exclude_unset=True).items():
        setattr(current_user, key, value)

    session.add(current_user)
    await session.commit()
    await session.refresh(current_user)

    return {"message" : "Update is Successful"}


@router.put("/change_password")
async def change_password(
    password_update: models.ChangedPassword,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> dict:
    if not await current_user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect current password",
        )

    await current_user.set_password(password_update.new_password)
    session.add(current_user)
    await session.commit()

    return {"message": "Password updated successfully"}


@router.delete("/{user_id}", response_model=dict)
async def delete_user(
    user_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_active_superuser),  # Only admin can delete users
) -> dict:
    user = await session.get(models.DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    await session.delete(user)
    await session.commit()

    return {"message": "User deleted successfully"}


@router.put("/{user_id}/updaterole")
async def update_user_role(
    user_id: int,
    new_role: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_active_superuser),  # Only admin can update roles
) :
    user = await session.get(models.DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    user.role = new_role
    session.add(user)
    await session.commit()
    await session.refresh(user)

    return {"message" : "Update Role is Successful"}
