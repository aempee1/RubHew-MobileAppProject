from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import datetime


# Define CategoryBase for shared fields
class CategoryBase(SQLModel):
    name_category: str = Field(index=True)
 


# Category table for storing categories
class Category(CategoryBase, table=True):
    __tablename__ = "categories"  # Table name in the database

    id_category: Optional[int] = Field(default=None, primary_key=True)
    
    # Relationship to items
    items: List["Item"] = Relationship(back_populates="category")  # type: ignore


# CategoryCreate schema for creating a new category
class CategoryCreate(CategoryBase):
    pass


# CategoryRead schema for reading category data
class CategoryRead(CategoryBase):
    id_category: int


# Now we modify the ItemBase and Item to include a relationship with Category
class ItemBase(SQLModel):
    name_item: str = Field(index=True)
    description: str
    price: float
    image: str
    status_thing: bool
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id_category")


class Item(ItemBase, table=True):
    __tablename__ = "items"  # Table name in the database

    id_item: Optional[int] = Field(default=None, primary_key=True)
    id_user: Optional[int] = Field(foreign_key="users.id", nullable=False)

    # Establish relationship to User model
    user: Optional["DBUser"] = Relationship(back_populates="items")  # type: ignore
    transactions: List["Transaction"] = Relationship(back_populates="item")  # type: ignore
    
    # Relationship to Category
    category: Optional["Category"] = Relationship(back_populates="items")  # type: ignore

    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


class ItemCreate(ItemBase):
    id_user: int


class ItemRead(ItemBase):
    id_item: int
    id_user: int
    created_at: datetime.datetime
    updated_at: datetime.datetime
    category: Optional[CategoryRead] = None  # Include category information in read response


class ItemUpdate(SQLModel):
    name_item: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    image: Optional[str] = None
    status_thing: Optional[bool] = False
    category_id: Optional[int] = None  # Allow updating category
