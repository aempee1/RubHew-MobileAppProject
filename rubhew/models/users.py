import datetime
import pydantic
from pydantic import BaseModel, EmailStr, ConfigDict
from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, String , Boolean
from typing import Optional, List


from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class BaseUser(BaseModel):

    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    email: str = pydantic.Field(example="admin@email.local")
    username: str = pydantic.Field(example="admin")
    first_name: str = pydantic.Field(example="Firstname")
    last_name: str = pydantic.Field(example="Lastname")
    


class UpdateUser(BaseModel):

    email: str = pydantic.Field(example="admin@email.local")
    first_name: str = pydantic.Field(example="Firstname")
    last_name: str = pydantic.Field(example="Lastname")
    # profile_image: str = pydantic.Field(example="base64")

class User(BaseUser):
    id: int
    last_login_date: datetime.datetime | None = pydantic.Field(
        example="2023-01-01T00:00:00.000000", default=None
    )
    register_date: datetime.datetime | None = pydantic.Field(
        example="2023-01-01T00:00:00.000000", default=None
    )


class ReferenceUser(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    username: str = pydantic.Field(example="admin")
    first_name: str = pydantic.Field(example="Firstname")
    last_name: str = pydantic.Field(example="Lastname")


class UserList(BaseModel):
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    users: list[User]


class Login(BaseModel):
    email: EmailStr
    password: str


class ChangedPassword(BaseModel):
    current_password: str
    new_password: str


class ResetedPassword(BaseModel):
    email: EmailStr
    citizen_id: str


class RegisteredUser(BaseUser):
    password: str = pydantic.Field(example="password")

class RegisterSuperUser(RegisteredUser):
    role: str = pydantic.Field(example="admin")

class SuperUserUpdateStatus(RegisterSuperUser) :
    status : bool = pydantic.Field(example= True )
# class UpdatedUser(BaseUser):
#     pass
#     # role: str = pydantic.Field(example="admin")  


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    expires_at: datetime.datetime
    scope: str
    issued_at: datetime.datetime


class TokenData(BaseModel):
    user_id: str | None = None


class ChangedPasswordUser(BaseModel):
    current_password: str
    new_password: str


class DBUser(BaseUser, SQLModel, table=True):
    __tablename__ = "users"
    id: int | None = Field(default=None, primary_key=True)

    password: str
    role: str = Field(default="user", sa_column=Column(String))  # Change roles to a single string
    status : bool = Field(default=False ,sa_column=Column(Boolean))
    items: List["Item"] = Relationship(back_populates="user") # type: ignore
    transactions: List["Transaction"] = Relationship(back_populates="user_customer") # type: ignore


    register_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    updated_date: datetime.datetime = Field(default_factory=datetime.datetime.now)
    last_login_date: datetime.datetime | None = Field(default=None)

    async def has_role(self, role: str) -> bool:
        return self.role == role

    async def set_password(self, plain_password: str):
        self.password = pwd_context.hash(plain_password)

    async def verify_password(self, plain_password: str) -> bool:
        return pwd_context.verify(plain_password, self.password)

    async def is_use_citizen_id_as_password(self):
        return pwd_context.verify(self.citizen_id, self.password)
