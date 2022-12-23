from fastapi import APIRouter, Depends
from ..models import Block

router = APIRouter(prefix="/layer")

@router.get("/latest")
async def latest():
    latest = await Block.filter().order_by("-height").limit(1).first()

    return {
        "created": int(latest.created.timestamp()),
        "height": latest.height,
        "hash": latest.hash,
    }
