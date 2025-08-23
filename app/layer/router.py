from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query
from . import service, dependencies as deps
from app.database import get_session
from app.chain import get_chain
from app.errors import Abort
from app import constants
from app import utils

from app.models import (
    FeeAddress,
    TokenCost,
    Address,
    Block,
    Token,
)


router = APIRouter(prefix="/layer", tags=["Layer"])


@router.get("/latest", summary="Latest synced block")
async def latest(session: AsyncSession = Depends(get_session)):
    return await service.get_latest_block(session)


@router.get("/tokens", summary="Tokens list")
async def tokens_list(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    type: str = Query(default=None),
    session: AsyncSession = Depends(get_session),
):
    limit, offset, size = utils.pagination(page, size)

    total = await service.count_tokens(session, type)
    items = await service.list_tokens(session, type, limit, offset)

    return {"pagination": utils.pagination_dict(total, page, size), "list": items}


@router.get("/token/{ticker}", summary="Token info")
async def token_info(
    token: Token = Depends(deps.require_token),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_token_info(session, token)


@router.get("/token/{ticker}/holders", summary="Token holders")
async def token_holders(
    token: Token = Depends(deps.require_token),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    limit, offset, size = utils.pagination(page, size)

    total = await service.count_token_holders(session, token)
    items = await service.list_token_holders(session, token, limit, offset)

    return {"pagination": utils.pagination_dict(total, page, size), "list": items}


@router.get("/token/{ticker}/transfers", summary="Token transfers")
async def token_transfers(
    token: Token = Depends(deps.require_token),
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    limit, offset, size = utils.pagination(page, size)

    total = await service.count_token_transfers(session, token)
    items = await service.list_token_transfers(session, token, limit, offset)

    return {"pagination": utils.pagination_dict(total, page, size), "list": items}


@router.get("/transfers", summary="Transfers list")
async def transfers_list(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    limit, offset, size = utils.pagination(page, size)

    total = await service.count_transfers(session)
    items = await service.list_transfers(session, limit, offset)

    return {"pagination": utils.pagination_dict(total, page, size), "list": items}


@router.get("/tx/{txid}", summary="Transaction transfers")
async def transaction_transfers(
    txid: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    limit, offset, size = utils.pagination(page, size)

    total = await service.count_transaction_transfers(session, txid)
    items = await service.list_transaction_transfers(session, txid, limit, offset)

    return {"pagination": utils.pagination_dict(total, page, size), "list": items}


@router.get("/address/{label}", summary="Address stats and balances")
async def address_info(label: str):
    result = []

    if not (address := await Address.filter(label=label).first()):
        return {"stats": {"transfers": 0, "balances": 0}, "balances": result}

    async for balance in address.balances:
        token = await balance.token

        transfers = await address.index.filter(token=token).count()

        result.append(
            {
                "received": utils.satoshis(balance.received, token.decimals),
                "value": utils.satoshis(balance.value, token.decimals),
                "sent": utils.satoshis(balance.sent, token.decimals),
                "decimals": token.decimals,
                "address": address.label,
                "transfers": transfers,
                "ticker": token.ticker,
            }
        )

    transfers_count = await address.index.filter().count()
    balances_count = await address.balances.filter().count()

    return {
        "stats": {"transfers": transfers_count, "balances": balances_count},
        "balances": result,
    }


@router.get("/address/{label}/transfers", summary="Address transfers")
async def address_transfers(
    label: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
):
    result = []

    if not (address := await Address.filter(label=label).first()):
        return {
            "pagination": {"pages": 0, "total": 0, "page": 0},
            "list": result,
        }

    total = await address.index.filter().count()
    limit, offset, size = utils.pagination(page, size)
    pagination = utils.pagination_dict(total, page, size)

    index_list = (
        await address.index.filter().order_by("-created").limit(limit).offset(offset)
    )

    for index in index_list:
        transfer = await index.transfer

        receiver = await transfer.receiver
        sender = await transfer.sender
        block = await transfer.block
        token = await index.token

        result.append(
            {
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
            }
        )

    return {"pagination": pagination, "list": result}


@router.get("/address/{label}/transfers/{ticker}", summary="Address token transfers")
async def address_token_transfers(
    label: str,
    ticker: str,
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
):
    result = []

    if not (address := await Address.filter(label=label).first()):
        return {
            "pagination": {"pages": 0, "total": 0, "page": 0},
            "list": result,
        }

    if not (token := await Token.filter(ticker=ticker).first()):
        raise Abort("token", "not-found")

    total = await address.index.filter(token=token).count()
    limit, offset, size = utils.pagination(page, size)
    pagination = utils.pagination_dict(total, page, size)

    index_list = (
        await address.index.filter(token=token)
        .order_by("-created")
        .limit(limit)
        .offset(offset)
    )

    for index in index_list:
        transfer = await index.transfer

        receiver = await transfer.receiver
        sender = await transfer.sender
        block = await transfer.block

        result.append(
            {
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
            }
        )

    return {"pagination": pagination, "list": result}


@router.get("/params", summary="Layer params")
async def params():
    settings = get_settings()
    chain = get_chain(settings.general.chain)

    latest = await Block.filter().order_by("-height").limit(1).first()

    fee_address = await FeeAddress.filter().order_by("-height").first()

    create_root = (
        await TokenCost.filter(
            action=constants.ACTION_CREATE, type=constants.TOKEN_ROOT
        )
        .order_by("-height")
        .first()
    )

    create_sub = (
        await TokenCost.filter(action=constants.ACTION_CREATE, type=constants.TOKEN_SUB)
        .order_by("-height")
        .first()
    )

    create_unique = (
        await TokenCost.filter(
            action=constants.ACTION_CREATE, type=constants.TOKEN_UNIQUE
        )
        .order_by("-height")
        .first()
    )

    issue_root = (
        await TokenCost.filter(action=constants.ACTION_ISSUE, type=constants.TOKEN_ROOT)
        .order_by("-height")
        .first()
    )

    issue_sub = (
        await TokenCost.filter(action=constants.ACTION_ISSUE, type=constants.TOKEN_SUB)
        .order_by("-height")
        .first()
    )

    admin = []

    for address in chain["admin"]:
        if chain["admin"][address][0] > latest.height:
            continue

        if chain["admin"][address][1] and chain["admin"][address][1] < latest.height:
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
                "sub": utils.satoshis(issue_sub.value, chain["decimals"]),
            },
        },
        "admin": admin,
    }
