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