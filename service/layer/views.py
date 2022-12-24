from ..models import Block, Token
from fastapi import APIRouter
from fastapi import Query
from .. import utils

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
async def tokens(page: int = Query(default=1, ge=1)):
    total = await Token.filter().count()
    limit, offset, size = utils.pagination(page)
    pagination = utils.pagination_dict(total, page, size)
    result = []

    tokens = await Token.filter().order_by(
        "created"
    ).limit(limit).offset(offset)

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

    return {
        "pagination": pagination,
        "list": result
    }
