from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Column, JSON  # Explicitly import Column and JSON from SQLAlchemy
from typing import Optional, List
import datetime

# Define CategoryBase for shared fields
class CategoryBase(SQLModel):
    name_category: str = Field(index=True)
    category_image: str = Field(index=True)

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

#----------------------------------------------------------------
class TagsBase(SQLModel):
    name_tags: str = Field(index=True)
    
class Tags(TagsBase, table=True):
    __tablename__ = "tags"  # Fixed table name for tags

    id_tags: Optional[int] = Field(default=None, primary_key=True)

    # Relationship to items
    items: List["ItemTagsLink"] = Relationship(back_populates="tag")  # type: ignore

class TagsCreate(TagsBase):
    pass

class TagsRead(TagsBase):
    id_tags: int

# Now we modify the ItemBase and Item to include a relationship with Category and Tags
class ItemBase(SQLModel):
    name_item: str = Field(index=True)
    description: str
    price: float
    images: List[str] = Field(sa_column=Column(JSON), default=[])  # Store multiple base64 images as a list of strings
    status: str = Field(default="Available")  # Boolean field to represent item status (active/inactive)
    category_id: Optional[int] = Field(default=None, foreign_key="categories.id_category")

    # Remove the tags relationship here
    # Use the association table instead

    # Use JSON field explicitly for detail
    detail: Optional[dict] = Field(default=None, sa_column=Column(JSON))

# models.py
class Item(ItemBase, table=True):
    __tablename__ = "items"  # Table name in the database

    id_item: Optional[int] = Field(default=None, primary_key=True)
    id_user: Optional[int] = Field(foreign_key="users.id", nullable=False)

    # Establish relationship to User model
    user: Optional["DBUser"] = Relationship(back_populates="items")  # type: ignore
    transactions: List["Transaction"] = Relationship(back_populates="item")  # type: ignore

    # Relationship to Category
    category: Optional["Category"] = Relationship(back_populates="items")  # type: ignore

    # Relationship to Tags through association table
    tags_link: List["ItemTagsLink"] = Relationship(back_populates="item")  # <--- Add this line

    created_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)


# ItemCreate no longer needs `id_user` in the request body
class ItemCreate(ItemBase):
    tags: List[int] = []  # Add this line

class UserProfile(SQLModel):
    username: str
    first_name: str
    last_name: str

class ItemRead(SQLModel):
    id_user:int
    id_item: int
    name_item: str
    description: str
    price: float
    images: List[str]  # Include the list of Base64-encoded images
    status: str      # Include the item's status
    detail: Optional[dict] = None
    category_id: int  # Only show category_id, not the full category
    tags: List[TagsRead] = []  # Include the tags associated with the item
    user_profile: Optional[UserProfile]

class ItemUpdate(SQLModel):
    name_item: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None
    images: Optional[List[str]] = None  # Allow updating the list of images
    status: Optional[str] = None       # Allow updating the status field
    detail: Optional[dict] = None       # Allow updating the detail field
    category_id: Optional[int] = None   # Allow updating category
    tags: Optional[List[int]] = None     # Allow updating tags

# Association table for the many-to-many relationship between Item and Tags
class ItemTagsLink(SQLModel, table=True):
    __tablename__ = "item_tags_link"  # Association table name

    item_id: Optional[int] = Field(foreign_key="items.id_item", primary_key=True)
    tag_id: Optional[int] = Field(foreign_key="tags.id_tags", primary_key=True)

    item: Optional[Item] = Relationship(back_populates="tags_link")  # <--- Ensure this is correct
    tag: Optional[Tags] = Relationship(back_populates="items")  # type: ignore

