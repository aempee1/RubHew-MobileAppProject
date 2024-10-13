from fastapi import APIRouter , HTTPException , Depends , status

from typing import Optional , Annotated

from sqlmodel import Field , SQLModel , Session , select , func
from sqlmodel.ext.asyncio.session import AsyncSession

import math 

from .. import models
from .. import deps

router = APIRouter(prefix="/profiles", tags=["profiles"])

@router.get("/me", response_model=models.Profile)
async def get_user_profile(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.Profile:
    profile = await session.get(models.DBProfile, current_user.id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )
    return profile

@router.put("/updateMyprofile", response_model=models.UpdateProfileModel)
async def update_profile(
    profile_update: models.UpdateProfileModel,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.UpdateProfileModel:
    # Fetch the user's profile using their ID
    profile = await session.get(models.DBProfile, current_user.id)

    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    for key, value in profile_update.dict(exclude_unset=True).items():
        setattr(profile, key, value)

    session.add(profile)
    await session.commit()
    await session.refresh(profile)

    return profile

@router.put("/updateMyFollowing", response_model=models.UpdateFollowingModel)
async def update_profile(
    profile_update: models.UpdateFollowingModel,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user)
) -> models.UpdateFollowingModel:
    # Fetch the user's profile using their ID
    profile = await session.get(models.DBProfile, current_user.id)

    if not profile or profile.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User profile not found")

    for key, value in profile_update.dict(exclude_unset=True).items():
        setattr(profile, key, value)

    session.add(profile)
    await session.commit()
    await session.refresh(profile)

    return profile
