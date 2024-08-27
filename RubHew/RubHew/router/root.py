from fastapi import APIRouter, HTTPException, Depends, Query


router = APIRouter()


@router.get("/")
async def index() -> dict:
    return dict(message="Digital Wallet API")