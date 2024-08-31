from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List, Annotated

from .. import models, deps

router = APIRouter(prefix="/transactions", tags=["transactions"])

# Get transaction by ID
@router.get("/{transaction_id}", response_model=models.TransactionRead)
async def get_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user),
) -> models.Transaction:
    transaction = await session.get(models.Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    return transaction

# Get transactions where the user is the seller
@router.get("/seller/me", response_model=List[models.TransactionRead])
async def get_my_seller_transactions(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user),
) -> List[models.Transaction]:
    result = await session.exec(select(models.Transaction).where(models.Transaction.id_user_seller == current_user.id))
    transactions = result.all()
    return transactions

# Get transactions where the user is the customer
@router.get("/customer/me", response_model=List[models.TransactionRead])
async def get_my_customer_transactions(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user),
) -> List[models.Transaction]:
    result = await session.exec(select(models.Transaction).where(models.Transaction.id_user_customer == current_user.id))
    transactions = result.all()
    return transactions

# Create a new transaction
@router.post("/", response_model=models.TransactionRead, status_code=status.HTTP_201_CREATED)
async def create_transaction(
    transaction: models.TransactionCreate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user),
) -> models.Transaction:
    new_transaction = models.Transaction.from_orm(transaction)
    session.add(new_transaction)
    await session.commit()
    await session.refresh(new_transaction)
    return new_transaction

# Update a transaction's status (Admin only)
@router.put("/{transaction_id}/status", response_model=models.TransactionRead)
async def update_transaction_status(
    transaction_id: int,
    status_update: models.TransactionUpdate,  # Changed to TransactionUpdate
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_active_superuser),
) -> models.Transaction:
    transaction = await session.get(models.Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    transaction.status = status_update.status
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction

# Update transaction address (Customer only and only if status is Waiting)
@router.put("/{transaction_id}/address", response_model=models.TransactionRead)
async def update_transaction_address(
    transaction_id: int,
    address_update: models.TransactionUpdate,  # Changed to TransactionUpdate
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_user),
) -> models.Transaction:
    transaction = await session.get(models.Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )

    # Check if the user is the customer and the status is Waiting
    if transaction.id_user_customer != current_user.id or transaction.status != "Waiting":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only update the address if you are the customer and the status is 'Waiting'.",
        )

    transaction.address = address_update.address
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction

# Delete a transaction
@router.delete("/{transaction_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.DBUser = Depends(deps.get_current_active_superuser),
) -> None:
    transaction = await session.get(models.Transaction, transaction_id)
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Transaction not found",
        )
    await session.delete(transaction)
    await session.commit()
