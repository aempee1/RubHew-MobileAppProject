from fastapi import APIRouter, Depends, HTTPException, Request, status # type: ignore
from sqlmodel.ext.asyncio.session import AsyncSession # type: ignore
from sqlmodel import select # type: ignore

from typing import Annotated

from deps import *
from models import *

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/me")
def get_me(
    current_user: User = Depends(get_current_user)) -> User:
    return current_user


@router.get("/{user_id}")
async def get(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    current_user: User = Depends(get_current_user),
) -> User:

    user = await session.get(DBUser, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )
    return user


@router.post("/create")
async def create(
    user_info: RegisteredUser,
    session: Annotated[AsyncSession, Depends(get_session)],
) -> User:

    result = await session.exec(
        select(DBUser).where(DBUser.username == user_info.username)
    )

    user = result.one_or_none()

    if user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="This username is exists.",
        )

    #user = DBUser.from_orm(user_info)
    user = DBUser.model_validate(user_info)


    await user.set_password(user_info.password)
    session.add(user)
    await session.commit()

    return user


@router.put("/{user_id}/change_password")
async def change_password(
    user_id: int,
    session: Annotated[AsyncSession, Depends(get_session)],
    password_update: ChangedPassword,
    current_user: User = Depends(get_current_user),
) -> dict() :

    user = await session.get(DBUser, user_id)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    if not await user.verify_password(password_update.current_password):  # ใช้ await
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    await user.set_password(password_update.new_password)  # ใช้ await
    session.add(user)
    await session.commit()

    return {"message": "Password updated successfully"}



@router.put("/{user_id}/update")
async def update(
    request: Request,
    user_id: int,
    password_update: ChangedPassword,
    session: Annotated[AsyncSession, Depends(get_session)],
    user_update: UpdatedUser,
    current_user: User = Depends(get_current_user),
) -> User:

    db_user = await session.get(DBUser, user_id)

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found this user",
        )

    if not await db_user.verify_password(password_update.current_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
        )

    db_user.sqlmodel_update(user_update)
    await db_user.set_password(password_update.new_password)
    session.add(db_user)
    await session.commit()
    await session.refresh(db_user)

    return db_user