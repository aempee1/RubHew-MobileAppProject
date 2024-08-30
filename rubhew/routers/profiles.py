from fastapi import APIRouter , HTTPException , Depends , Query

from typing import Optional , Annotated

from sqlmodel import Field , SQLModel , Session , select , func
from sqlmodel.ext.asyncio.session import AsyncSession

import math 

from .. import models
from .. import deps
