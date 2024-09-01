from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from sqlmodel.ext.asyncio.session import AsyncSession
from sqlalchemy.orm import Session as SQLAlchemySession
from typing import List, Annotated
from datetime import datetime

from .. import deps
from .. import models

router = APIRouter(prefix="/transactions", tags=["transactions"])

# Create a new transaction
@router.post("/", response_model=models.TransactionRead)
async def create_transaction(
    transaction_in: models.TransactionCreate,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.TransactionRead:
    # Create a new Transaction instance without including id_user_customer in dict expansion
    transaction = models.Transaction(
        **transaction_in.dict(exclude={"id_user_customer", "create_time", "update_time"}),  # Exclude conflicting fields
        id_user_customer=current_user.id,  # Set id_user_customer directly
        create_time=datetime.utcnow(),
        update_time=datetime.utcnow(),
    )
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


# Get my transactions as a customer
@router.get("/customer", response_model=List[models.TransactionRead])
async def get_my_transactions_customer(
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_active_superuser),
) -> List[models.TransactionRead]:
    statement = select(models.Transaction).where(models.Transaction.id_user_customer == current_user.id)
    results = await session.execute(statement)
    return results.scalars().all()


# Update transaction status (Admin only)
@router.put("/{transaction_id}/status", response_model=models.TransactionRead)
async def update_transaction_status(
    transaction_id: int,
    status: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.TransactionRead:
    transaction = await session.get(models.Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    transaction.status = status
    transaction.update_time = datetime.utcnow()
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


# Edit address if status is "Waiting" (Customer only)
@router.put("/{transaction_id}/address", response_model=models.TransactionRead)
async def update_transaction_address(
    transaction_id: int,
    address: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.TransactionRead:
    transaction = await session.get(models.Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.id_user_customer != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this transaction")

    if transaction.status != "Waiting":
        raise HTTPException(status_code=400, detail="Cannot update address at this stage")

    transaction.address = address
    transaction.update_time = datetime.utcnow()
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


# Send receipt slip (base64) (Customer only)
@router.put("/{transaction_id}/receipt", response_model=models.TransactionRead)
async def update_transaction_receipt(
    transaction_id: int,
    receipt: str,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.TransactionRead:
    transaction = await session.get(models.Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.id_user_customer != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this transaction")

    transaction.receipt = receipt
    transaction.update_time = datetime.utcnow()
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


# Cancel transaction (Customer only)
@router.put("/{transaction_id}/cancel", response_model=models.TransactionRead)
async def cancel_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: models.User = Depends(deps.get_current_user),
) -> models.TransactionRead:
    transaction = await session.get(models.Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    if transaction.id_user_customer != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to cancel this transaction")

    if transaction.status not in ["Waiting", "Confirm"]:
        raise HTTPException(status_code=400, detail="Cannot cancel transaction at this stage")

    transaction.status = "Cancel"
    transaction.update_time = datetime.utcnow()
    session.add(transaction)
    await session.commit()
    await session.refresh(transaction)
    return transaction


# Delete transaction (Admin only)
@router.delete("/{transaction_id}", response_model=dict)
async def delete_transaction(
    transaction_id: int,
    session: Annotated[AsyncSession, Depends(models.get_session)],
    current_user: Annotated[models.User, Depends(deps.get_current_active_superuser)],
) -> dict:
    transaction = await session.get(models.Transaction, transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    await session.delete(transaction)
    await session.commit()
    return {"message": "Transaction deleted successfully"}
