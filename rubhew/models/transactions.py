from sqlmodel import SQLModel, Field, Relationship
from typing import Optional
import datetime

class TransactionBase(SQLModel):
    price: float
    address: str
    receipt: str  # Base64 encoded image
    date_time: datetime.datetime = Field(default_factory=datetime.datetime.utcnow)
    status: str = Field(default="ยืนยันการโอน")  # Default status

class Transaction(TransactionBase, table=True):
    __tablename__ = "transactions"

    id_transaction: Optional[int] = Field(default=None, primary_key=True)
    
    # Seller relationship
    id_user_seller: Optional[int] = Field(foreign_key="users.id", nullable=False)
    seller: Optional["DBUser"] = Relationship(back_populates="seller_transactions", sa_relationship_kwargs={"lazy": "selectin"})

    # Customer relationship
    id_user_customer: Optional[int] = Field(foreign_key="users.id", nullable=False)
    customer: Optional["DBUser"] = Relationship(back_populates="customer_transactions", sa_relationship_kwargs={"lazy": "selectin"})


class TransactionCreate(TransactionBase):
    id_user_seller: int
    id_user_customer: int


class TransactionRead(TransactionBase):
    id_transaction: int
    id_user_seller: int
    id_user_customer: int
    date_time: datetime.datetime


class TransactionUpdate(SQLModel):
    price: Optional[float] = None
    address: Optional[str] = None
    receipt: Optional[str] = None  # Base64 encoded image
    status: Optional[str] = None
