from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import datetime
from sqlalchemy.orm import relationship


class ItemBase(SQLModel):
    name_item: str = Field(index=True)
    description: str
    type: str
    price: float
    image: str
    status_thing : bool


class Item(ItemBase, table=True):
    __tablename__ = "items"  # Table name in the database

    id_item: Optional[int] = Field(default=None, primary_key=True)
    id_user: Optional[int] = Field(foreign_key="users.id", nullable=False)

    # Establish relationship to User model
    user: Optional["DBUser"] = Relationship(back_populates="items") # type: ignore
    transactions: List["Transaction"] = Relationship(back_populates="item") # type: ignore

    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class ItemCreate(ItemBase):
    id_user: int


class ItemRead(ItemBase):
    id_item: int
    id_user: int
    created_at: datetime.datetime
    updated_at: datetime.datetime


class ItemUpdate(SQLModel):
    name_item: Optional[str] = None
    description: Optional[str] = None
    type: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    status_thing : Optional[bool] =  False
