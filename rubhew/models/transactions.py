from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy.orm import relationship
from typing import Optional, List
from datetime import datetime


class TransactionBase(SQLModel):
    price: float
    address: str
    receipt: str  # Base64 encoded image
    create_time: datetime = Field(default_factory=datetime.utcnow)
    update_time: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="Waiting")  # Default status


class Transaction(TransactionBase, table=True):
    __tablename__ = "transactions"

    id_transaction: int = Field(default=None, primary_key=True)
    id_item: int = Field(foreign_key="items.id_item")
    id_user_customer: int = Field(foreign_key="users.id")

    # Correctly annotated relationships
    item: Optional["Item"] = Relationship(back_populates="transactions")
    user_customer: Optional["DBUser"] = Relationship(back_populates="transactions")


class TransactionCreate(TransactionBase):
    id_item: int
    id_user_customer: int


class TransactionRead(TransactionBase):
    id_transaction: int
    id_item: int
    id_user_customer: int


class TransactionUpdate(SQLModel):
    price: Optional[float] = None
    address: Optional[str] = None
    receipt: Optional[str] = None  # Base64 encoded image
    status: Optional[str] = None
