
from datetime import date
from typing import List, Literal, Optional

from pydantic import BaseModel , ConfigDict
from sqlmodel import Field , SQLModel , create_engine , Session , select , Relationship
from sqlalchemy import Column, JSON

from . import users




class ProfileModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    gender: str | None = None
    address: str | None = None
    birthday: str | None = None
    phoneNumber: str | None = None
    profile_image: str | None = None
    user_id : int | None = 0
    tag_following: List[int] = Field(sa_column=Column(JSON), default_factory=list)

    # Field for storing followed categories as a list of integers
    category_following: List[int] = Field(sa_column=Column(JSON), default_factory=list)



class CreateProfileModel(BaseModel):

    gender: str | None = None
    address: str | None = None
    birthday: str | None = None
    phoneNumber: str | None = None
    profile_image: str | None = None

class UpdateProfileModel(BaseModel):
    gender: str | None = None
    address: str | None = None
    birthday: str | None = None
    phoneNumber: str | None = None
    profile_image: str | None = None

class UpdateFollowingModel(BaseModel):
   
    tag_following: List[int] = Field(sa_column=Column(JSON), default_factory=list)
    # Field for storing followed categories as a list of integers
    category_following: List[int] = Field(sa_column=Column(JSON), default_factory=list)

class Profile(ProfileModel):
    id : int

class DBProfile(ProfileModel , SQLModel , table = True) :
    __tablename__ = 'profile'
    id : Optional[int] = Field(default=None , primary_key= True)

    user_id: int = Field(default=None, foreign_key="users.id")
    user: users.DBUser | None = Relationship()
    
     # Field for storing followed tags as a list of integers
    tag_following: List[int] = Field(sa_column=Column(JSON), default_factory=list)

    # Field for storing followed categories as a list of integers
    category_following: List[int] = Field(sa_column=Column(JSON), default_factory=list)

class ProfileList(ProfileModel) :
    model_config = ConfigDict(from_attributes=True)
    profiles : List[Profile]
    page : int
    page_count : int
    size_per_page : int
