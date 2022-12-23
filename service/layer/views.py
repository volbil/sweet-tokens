from ..models import Block, Token
from fastapi import APIRouter

router = APIRouter(prefix="/layer")

@router.get("/latest")
async def latest():
    latest = await Block.filter().order_by("-height").limit(1).first()

    return {
        "created": int(latest.created.timestamp()),
        "height": latest.height,
        "hash": latest.hash,
    }

@router.get("/tokens")
async def latest():
    tokens = await Token.filter()
    result = []

    for token in tokens:
        balances = await token.balances.filter(value__gt=0).count()
        transfers = await token.transfers.filter().count()
        owner = await token.owner

        result.append({
            "reissuable": token.reissuable,
            "decimals": token.decimals,
            "transfers": transfers,
            "supply": token.supply,
            "ticker": token.ticker,
            "owner": owner.label,
            "balances": balances
        })

    return result
