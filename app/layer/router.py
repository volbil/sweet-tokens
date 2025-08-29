from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, Query

from . import service, dependencies as deps
from app.database import get_session
from app.schemas import Paginated
from app import utils

from .schemas import (
    TokenTransferInfo,
    TokenHolderInfo,
    AddressInfo,
    LayerParams,
    TokenInfo,
    BlockInfo,
)

from app.models import (
    Address,
    Token,
)


router = APIRouter(prefix="/layer", tags=["Layer"])


@router.get("/latest", summary="Latest synced block", response_model=BlockInfo)
async def latest(session: AsyncSession = Depends(get_session)):
    return await service.get_latest_block(session)


@router.get("/tokens", summary="Tokens list", response_model=Paginated[TokenInfo])
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


@router.get("/token/{ticker}", summary="Token info", response_model=TokenInfo)
async def token_info(
    token: Token = Depends(deps.require_token),
    session: AsyncSession = Depends(get_session),
):
    return await service.get_token_info(session, token)


@router.get(
    "/token/{ticker}/holders",
    summary="Token holders",
    response_model=Paginated[TokenHolderInfo],
)
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


@router.get(
    "/token/{ticker}/transfers",
    summary="Token transfers",
    response_model=Paginated[TokenTransferInfo],
)
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


@router.get(
    "/transfers", summary="Transfers list", response_model=Paginated[TokenTransferInfo]
)
async def transfers_list(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    session: AsyncSession = Depends(get_session),
):
    limit, offset, size = utils.pagination(page, size)

    total = await service.count_transfers(session)
    items = await service.list_transfers(session, limit, offset)

    return {"pagination": utils.pagination_dict(total, page, size), "list": items}


@router.get(
    "/tx/{txid}",
    summary="Transaction transfers",
    response_model=Paginated[TokenTransferInfo],
)
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


@router.get(
    "/address/{label}", summary="Address stats and balances", response_model=AddressInfo
)
async def address_info(
    address: Address | None = Depends(deps.optional_address),
    session: AsyncSession = Depends(get_session),
):
    if address is None:
        return {"stats": {"transfers": 0, "balances": 0}, "balances": ()}

    return await service.get_address_info(session, address)


@router.get(
    "/address/{label}/transfers",
    summary="Address transfers",
    response_model=Paginated[TokenTransferInfo],
)
async def address_transfers(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    address: Address | None = Depends(deps.optional_address),
    session: AsyncSession = Depends(get_session),
):
    if address is None:
        return {"pagination": {"pages": 0, "total": 0, "page": 0}, "list": ()}

    limit, offset, size = utils.pagination(page, size)

    total = await service.count_address_transfers(session, address)
    items = await service.list_address_transfers(session, address, limit, offset)

    return {"pagination": utils.pagination_dict(total, page, size), "list": items}


@router.get(
    "/address/{label}/transfers/{ticker}",
    summary="Address token transfers",
    response_model=Paginated[TokenTransferInfo],
)
async def address_token_transfers(
    page: int = Query(default=1, ge=1),
    size: int = Query(default=20, ge=1, le=100),
    address: Address | None = Depends(deps.optional_address),
    token: Token = Depends(deps.require_token),
    session: AsyncSession = Depends(get_session),
):
    if address is None:
        return {"pagination": {"pages": 0, "total": 0, "page": 0}, "list": ()}

    limit, offset, size = utils.pagination(page, size)

    total = await service.count_address_token_transfers(session, address, token)
    items = await service.list_address_token_transfers(
        session, address, token, limit, offset
    )

    return {"pagination": utils.pagination_dict(total, page, size), "list": items}


@router.get("/params", summary="Layer params", response_model=LayerParams)
async def params(session: AsyncSession = Depends(get_session)):
    return await service.get_params(session)
