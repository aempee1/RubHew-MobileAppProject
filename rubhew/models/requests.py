from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
import datetime

class RequestBase(SQLModel):
    id_sent: int = Field(foreign_key="users.id")  # Foreign key to the user who sent the request
    id_receive: int = Field(foreign_key="users.id")  # Foreign key to the user who owns the item
    id_item: int = Field(foreign_key="items.id_item")  # Foreign key to the requested item
    message: Optional[str] = Field(default=None)  # Message from the requester
    res_message: Optional[str] = Field(default=None)  # Response message from the owner

    create_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)  # Request creation time
    update_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)  # Request update time

class Request(RequestBase, table=True):
    __tablename__ = "requests"

    id: Optional[int] = Field(default=None, primary_key=True)

    # Establish the relationship to the Item model
    item: "Item" = Relationship(back_populates="requests")  # This creates a relationship to the Item

# For schemas
class RequestCreate(SQLModel):
    id_item: int  # ID of the item
    message: Optional[str] = None  # Initial message

class RequestRead(SQLModel):
    id: int
    id_sent: int
    id_receive: int
    id_item: int
    message: Optional[str]
    res_message: Optional[str]
    create_time: datetime.datetime
    update_time: datetime.datetime

# New schema to handle updates
class RequestUpdate(SQLModel):
    message: Optional[str] = None  # Allows updating the requester's message
    res_message: Optional[str] = None  # Allows updating the owner's response message


class UserDetail(SQLModel):
    username: str
    email: str
    first_name: str
    last_name: str

class ItemDetail(SQLModel):
    id_item: int
    name_item: str
    images: List[str]  # Assuming images is a list of strings (base64 or URLs)
    status: str

class RequestDetailRead(SQLModel):
    id: int
    id_sent: int
    id_receive: int
    id_item: int
    message: Optional[str]
    res_message: Optional[str]
    create_time: datetime.datetime
    update_time: datetime.datetime
    sender: UserDetail
    receiver: UserDetail
    item: ItemDetail

class RequestUpdate(SQLModel):
    res_message: Optional[str] = None
    item_status: Optional[str] = None  # This will hold the new status for the item


