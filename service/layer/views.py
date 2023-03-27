from ..models import Block, Token, Balance
from ..models import FeeAddress, TokenCost
from ..models import Transfer, Address
from fastapi import APIRouter
from ..chain import get_chain
from ..errors import Abort
from fastapi import Query
from .. import constants
from .. import utils
import config

router = APIRouter(prefix="/layer", tags=["Layer"])

@router.get(
    "/latest", summary="Latest synced block"
)
async def latest():
    latest = await Block.filter().order_by("-height").limit(1).first()
    holders = await Balance.filter(value__gt=0).count()
    transfers = await Transfer.filter().count()
    tokens = await Token.filter().count()

    return {
        "created": int(latest.created.timestamp()),
        "height": latest.height,
        "hash": latest.hash,
        "stats": {
            "transfers": transfers,
            "holders": holders,
            "tokens": tokens
        }
    }

@router.get(
    "/tokens", summary="Tokens list"
)
async def tokens_list(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    type: str = Query(default=None)
):
    query = Token.filter()

    if type:
        query = query.filter(type=type)

    total = await query.count()
    limit, offset, size = utils.pagination(page, size)
    pagination = utils.pagination_dict(total, page, size)
    result = []

    tokens = await query.order_by(
        "-created"
    ).limit(limit).offset(offset)

    for token in tokens:
        holders = await token.balances.filter(value__gt=0).count()
        transfers = await token.transfers.filter().count()

        result.append({
            "supply": utils.satoshis(token.supply, token.decimals),
            "reissuable": token.reissuable,
            "decimals": token.decimals,
            "transfers": transfers,
            "ticker": token.ticker,
            "type": token.type,
            "holders": holders
        })

    return {
        "pagination": pagination,
        "list": result
    }

@router.get(
    "/token/{ticker}", summary="Token info"
)
async def token_info(
    ticker: str
):
    if not (token := await Token.filter(ticker=ticker).first()):
        raise Abort("token", "not-found")
    
    holders = await token.balances.filter(value__gt=0).count()
    transfers = await token.transfers.filter().count()

    return {
        "supply": utils.satoshis(token.supply, token.decimals),
        "reissuable": token.reissuable,
        "decimals": token.decimals,
        "transfers": transfers,
        "ticker": token.ticker,
        "type": token.type,
        "holders": holders
    }

@router.get(
    "/token/{ticker}/holders", summary="Token holders"
)
async def token_holders(
    ticker: str, page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100)
):
    if not (token := await Token.filter(ticker=ticker).first()):
        raise Abort("token", "not-found")
    
    total = await token.balances.filter(value__gt=0).count()
    limit, offset, size = utils.pagination(page, size)
    pagination = utils.pagination_dict(total, page, size)
    result = []

    holders = await token.balances.filter(
        value__gt=0
    ).order_by("-value").limit(limit).offset(offset)

    for balance in holders:
        address = await balance.address

        result.append({
            "received": utils.satoshis(balance.received, token.decimals),
            "value": utils.satoshis(balance.value, token.decimals),
            "sent": utils.satoshis(balance.sent, token.decimals),
            "decimals": token.decimals,
            "address": address.label,
            "ticker": token.ticker
        })

    return {
        "pagination": pagination,
        "list": result
    }

@router.get(
    "/token/{ticker}/transfers", summary="Token transfers"
)
async def token_transfers(
    ticker: str, page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100)
):
    if not (token := await Token.filter(ticker=ticker).first()):
        raise Abort("token", "not-found")
    
    total = await token.transfers.filter().count()
    limit, offset, size = utils.pagination(page, size)
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
            "value": utils.satoshis(transfer.value, token.decimals),
            "receiver": receiver.label if receiver else None,
            "created": int(transfer.created.timestamp()),
            "sender": sender.label if sender else None,
            "category": transfer.category,
            "version": transfer.version,
            "decimals": token.decimals,
            "height": block.height,
            "token": token.ticker,
            "txid": transfer.txid,
        })

    return {
        "pagination": pagination,
        "list": result
    }

@router.get(
    "/transfers", summary="Transfers list"
)
async def transfers_list(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100)
):
    total = await Transfer.filter().count()
    limit, offset, size = utils.pagination(page, size)
    pagination = utils.pagination_dict(total, page, size)
    result = []

    transfers = await Transfer.filter().order_by(
        "-created"
    ).limit(limit).offset(offset)

    for transfer in transfers:
        receiver = await transfer.receiver
        sender = await transfer.sender
        token = await transfer.token
        block = await transfer.block

        result.append({
            "value": utils.satoshis(transfer.value, token.decimals),
            "receiver": receiver.label if receiver else None,
            "created": int(transfer.created.timestamp()),
            "sender": sender.label if sender else None,
            "category": transfer.category,
            "version": transfer.version,
            "decimals": token.decimals,
            "height": block.height,
            "token": token.ticker,
            "txid": transfer.txid
        })

    return {
        "pagination": pagination,
        "list": result
    }

@router.get(
    "/tx/{txid}", summary="Transaction transfers"
)
async def transfer_info(
    txid: str, page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100)
):
    total = await Transfer.filter(txid=txid).count()
    limit, offset, size = utils.pagination(page, size)
    pagination = utils.pagination_dict(total, page, size)
    result = []

    transfers = await Transfer.filter(txid=txid).order_by(
        "-created"
    ).limit(limit).offset(offset)

    for transfer in transfers:
        receiver = await transfer.receiver
        sender = await transfer.sender
        token = await transfer.token
        block = await transfer.block

        result.append({
            "value": utils.satoshis(transfer.value, token.decimals),
            "receiver": receiver.label if receiver else None,
            "created": int(transfer.created.timestamp()),
            "sender": sender.label if sender else None,
            "category": transfer.category,
            "version": transfer.version,
            "decimals": token.decimals,
            "height": block.height,
            "token": token.ticker,
            "txid": transfer.txid,
        })

    return {
        "pagination": pagination,
        "list": result
    }

@router.get(
    "/address/{label}", summary="Address stats and balances"
)
async def address_info(
    label: str
):
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
            "received": utils.satoshis(balance.received, token.decimals),
            "value": utils.satoshis(balance.value, token.decimals),
            "sent": utils.satoshis(balance.sent, token.decimals),
            "decimals": token.decimals,
            "address": address.label,
            "transfers": transfers,
            "ticker": token.ticker
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

@router.get(
    "/address/{label}/transfers", summary="Address transfers"
)
async def address_transfers(
    label: str, page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100)
):
    result = []

    if not (address := await Address.filter(label=label).first()):
        return {
            "pagination": {"pages": 0, "total": 0, "page": 0},
            "list": result
        }

    total = await address.index.filter().count()
    limit, offset, size = utils.pagination(page, size)
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
            "value": utils.satoshis(transfer.value, token.decimals),
            "receiver": receiver.label if receiver else None,
            "created": int(transfer.created.timestamp()),
            "sender": sender.label if sender else None,
            "category": transfer.category,
            "version": transfer.version,
            "decimals": token.decimals,
            "height": block.height,
            "token": token.ticker,
            "txid": transfer.txid,
        })

    return {
        "pagination": pagination,
        "list": result
    }

@router.get(
    "/address/{label}/transfers/{ticker}", summary="Address token transfers"
)
async def address_token_transfers(
    label: str, ticker: str, page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100)
):
    result = []

    if not (address := await Address.filter(label=label).first()):
        return {
            "pagination": {"pages": 0, "total": 0, "page": 0},
            "list": result
        }

    if not (token := await Token.filter(ticker=ticker).first()):
        raise Abort("token", "not-found")

    total = await address.index.filter(token=token).count()
    limit, offset, size = utils.pagination(page, size)
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
            "value": utils.satoshis(transfer.value, token.decimals),
            "receiver": receiver.label if receiver else None,
            "created": int(transfer.created.timestamp()),
            "sender": sender.label if sender else None,
            "category": transfer.category,
            "version": transfer.version,
            "decimals": token.decimals,
            "height": block.height,
            "token": token.ticker,
            "txid": transfer.txid,
        })

    return {
        "pagination": pagination,
        "list": result
    }


@router.get(
    "/params", summary="Layer params"
)
async def params():
    chain = get_chain(config.chain)

    latest = await Block.filter().order_by("-height").limit(1).first()

    fee_address = await FeeAddress.filter().order_by("-height").first()

    create_root = await TokenCost.filter(
        action=constants.ACTION_CREATE, type=constants.TOKEN_ROOT
    ).order_by("-height").first()

    create_sub = await TokenCost.filter(
        action=constants.ACTION_CREATE, type=constants.TOKEN_SUB
    ).order_by("-height").first()

    create_unique = await TokenCost.filter(
        action=constants.ACTION_CREATE, type=constants.TOKEN_UNIQUE
    ).order_by("-height").first()

    issue_root = await TokenCost.filter(
        action=constants.ACTION_ISSUE, type=constants.TOKEN_ROOT
    ).order_by("-height").first()

    issue_sub = await TokenCost.filter(
        action=constants.ACTION_ISSUE, type=constants.TOKEN_SUB
    ).order_by("-height").first()

    admin = []

    for address in chain["admin"]:
        if chain["admin"][address][0] > latest.height:
            continue

        if chain["admin"][
            address
        ][1] and chain["admin"][
            address
        ][1] < latest.height:
            continue

        admin.append(address)

    return {
        "chain": config.chain,
        "fee_address": fee_address.label,
        "cost": {
            "create": {
                "root": utils.satoshis(create_root.value, chain["decimals"]),
                "sub": utils.satoshis(create_sub.value, chain["decimals"]),
                "unique": utils.satoshis(create_unique.value, chain["decimals"]),
            },
            "issue": {
                "root": utils.satoshis(issue_root.value, chain["decimals"]),
                "sub": utils.satoshis(issue_sub.value, chain["decimals"])
            }
        },
        "admin": admin
    }
