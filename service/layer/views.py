from ..models import Transfer, Address
from ..models import Block, Token
from fastapi import APIRouter
from ..errors import Abort
from fastapi import Query
from .. import utils

router = APIRouter(prefix="/layer", tags=["Layer"])

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
        holders = await token.balances.filter(value__gt=0).count()
        transfers = await token.transfers.filter().count()
        owner = await token.owner

        result.append({
            "reissuable": token.reissuable,
            "decimals": token.decimals,
            "transfers": transfers,
            "supply": token.supply,
            "ticker": token.ticker,
            "owner": owner.label,
            "holders": holders
        })

    return {
        "pagination": pagination,
        "list": result
    }

@router.get("/token/{ticker}")
async def token(ticker: str):
    if not (token := await Token.filter(ticker=ticker).first()):
        raise Abort("token", "not-found")
    
    holders = await token.balances.filter(value__gt=0).count()
    transfers = await token.transfers.filter().count()
    owner = await token.owner

    return {
        "reissuable": token.reissuable,
        "decimals": token.decimals,
        "transfers": transfers,
        "supply": token.supply,
        "ticker": token.ticker,
        "owner": owner.label,
        "holders": holders
    }

@router.get("/token/{ticker}/holders")
async def holders(ticker: str, page: int = Query(default=1, ge=1)):
    if not (token := await Token.filter(ticker=ticker).first()):
        raise Abort("token", "not-found")
    
    total = await token.balances.filter(value__gt=0).count()
    limit, offset, size = utils.pagination(page)
    pagination = utils.pagination_dict(total, page, size)
    result = []

    holders = await token.balances.filter(
        value__gt=0
    ).order_by("-value").limit(limit).offset(offset)

    for balance in holders:
        address = await balance.address

        result.append({
            "address": address.label,
            "received": balance.received,
            "value": balance.value,
            "sent": balance.sent,
            "decimals": token.decimals,
        })

    return {
        "pagination": pagination,
        "list": result
    }

@router.get("/token/{ticker}/transfers")
async def transfers(ticker: str, page: int = Query(default=1, ge=1)):
    if not (token := await Token.filter(ticker=ticker).first()):
        raise Abort("token", "not-found")
    
    total = await token.transfers.filter().count()
    limit, offset, size = utils.pagination(page)
    pagination = utils.pagination_dict(total, page, size)
    result = []

    transfers = await token.transfers.filter().order_by(
        "-created"
    ).limit(limit).offset(offset)

    for transfer in transfers:
        receiver = await transfer.receiver
        sender = await transfer.sender
        block = await transfer.block

        result.append({
            "receiver": receiver.label if receiver else None,
            "created": int(transfer.created.timestamp()),
            "sender": sender.label if sender else None,
            "category": transfer.category,
            "decimals": token.decimals,
            "value": transfer.value,
            "height": block.height,
            "token": token.ticker,
            "txid": transfer.txid,
        })

    return {
        "pagination": pagination,
        "list": result
    }

@router.get("/transfer/{txid}")
async def transfer(txid: str):
    if not (transfer := await Transfer.filter(txid=txid).first()):
        raise Abort("transfer", "not-found")

    receiver = await transfer.receiver
    sender = await transfer.sender
    block = await transfer.block
    token = await transfer.token

    return {
        "receiver": receiver.label if receiver else None,
        "created": int(transfer.created.timestamp()),
        "sender": sender.label if sender else None,
        "category": transfer.category,
        "decimals": token.decimals,
        "value": transfer.value,
        "height": block.height,
        "token": token.ticker,
        "txid": transfer.txid,
    }

@router.get("/address/{label}")
async def address(label: str):
    result = []

    if not (address := await Address.filter(label=label).first()):
        return {
            "stats": {
                "transfers": 0,
                "balances": 0
            },
            "balances": result
        }

    async for balance in address.balances:
        token = await balance.token

        transfers = await address.index.filter(token=token).count()

        result.append({
            "received": balance.received,
            "decimals": token.decimals,
            "address": address.label,
            "transfers": transfers,
            "value": balance.value,
            "sent": balance.sent,
        })

    transfers_count = await address.index.filter().count()
    balances_count = await address.balances.filter().count()

    return {
        "stats": {
            "transfers": transfers_count,
            "balances": balances_count
        },
        "balances": result
    }

@router.get("/address/{label}/transfers")
async def address(label: str, page: int = Query(default=1, ge=1)):
    result = []

    if not (address := await Address.filter(label=label).first()):
        return {
            "pagination": {"pages": 0, "total": 0, "page": 0},
            "list": result
        }

    total = await address.index.filter().count()
    limit, offset, size = utils.pagination(page)
    pagination = utils.pagination_dict(total, page, size)

    index_list = await address.index.filter().order_by(
        "-created"
    ).limit(limit).offset(offset)

    for index in index_list:
        transfer = await index.transfer

        receiver = await transfer.receiver
        sender = await transfer.sender
        block = await transfer.block
        token = await index.token

        result.append({
            "receiver": receiver.label if receiver else None,
            "created": int(transfer.created.timestamp()),
            "sender": sender.label if sender else None,
            "category": transfer.category,
            "decimals": token.decimals,
            "value": transfer.value,
            "height": block.height,
            "token": token.ticker,
            "txid": transfer.txid,
        })

    return {
        "pagination": pagination,
        "list": result
    }

@router.get("/address/{label}/transfers/{ticker}")
async def address(label: str, ticker: str, page: int = Query(default=1, ge=1)):
    result = []

    if not (address := await Address.filter(label=label).first()):
        return {
            "pagination": {"pages": 0, "total": 0, "page": 0},
            "list": result
        }

    if not (token := await Token.filter(ticker=ticker).first()):
        raise Abort("token", "not-found")

    total = await address.index.filter(token=token).count()
    limit, offset, size = utils.pagination(page)
    pagination = utils.pagination_dict(total, page, size)

    index_list = await address.index.filter(token=token).order_by(
        "-created"
    ).limit(limit).offset(offset)

    for index in index_list:
        transfer = await index.transfer

        receiver = await transfer.receiver
        sender = await transfer.sender
        block = await transfer.block

        result.append({
            "receiver": receiver.label if receiver else None,
            "created": int(transfer.created.timestamp()),
            "sender": sender.label if sender else None,
            "category": transfer.category,
            "decimals": token.decimals,
            "value": transfer.value,
            "height": block.height,
            "token": token.ticker,
            "txid": transfer.txid,
        })

    return {
        "pagination": pagination,
        "list": result
    }
