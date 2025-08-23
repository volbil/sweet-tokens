from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Select, func, select
from sqlalchemy.orm import joinedload
from typing import Any

from app.models import Balance, Block, Token, Transfer
from app import utils

from sqlalchemy.orm.strategy_options import (
    _AbstractLoad,  # pyright: ignore[reportPrivateUsage]
)


async def get_token(session: AsyncSession, ticker: str):
    return await session.scalar(select(Token).filter(Token.ticker == ticker))


async def get_latest_block(session: AsyncSession):
    latest = await session.scalar(select(Block).order_by(Block.height.desc()).limit(1))
    assert latest is not None

    holders = (
        await session.scalar(select(func.count(Balance.id)).filter(Balance.value > 0))
        or 0
    )
    transfers = await session.scalar(select(func.count(Transfer.id))) or 0
    tokens = await session.scalar(select(func.count(Token.id))) or 0

    return {
        "created": int(latest.created.timestamp()),
        "height": latest.height,
        "hash": latest.hash,
        "stats": {"transfers": transfers, "holders": holders, "tokens": tokens},
    }


async def count_tokens(session: AsyncSession, type: str | None):
    query = select(func.count(Token.id))
    if type:
        query = query.filter(Token.type == type)

    return await session.scalar(query) or 0


async def list_tokens(
    session: AsyncSession,
    type: str | None,
    limit: int,
    offset: int,
):
    query: Select[tuple[Token, int, int]] = select(
        Token,
        select(func.count(Balance.id)).filter(Token.id == Balance.token_id).subquery(),
        select(func.count(Transfer.id))
        .filter(Token.id == Transfer.token_id)
        .subquery(),
    )

    if type:
        query = query.filter(Token.type == type)

    tokens = await session.execute(
        query.order_by(Token.created.desc()).limit(limit).offset(offset)
    )

    return [
        {
            "supply": utils.satoshis(token.supply, token.decimals),
            "reissuable": token.reissuable,
            "decimals": token.decimals,
            "transfers": transfers,
            "ticker": token.ticker,
            "type": token.type,
            "holders": holders,
        }
        for token, holders, transfers in tokens.tuples()
    ]


async def get_token_info(session: AsyncSession, token: Token):
    query: Select[tuple[int, int]] = select(
        select(func.count(Balance.id)).filter(Balance.token_id == token.id).subquery(),
        select(func.count(Transfer.id))
        .filter(Transfer.token_id == token.id)
        .subquery(),
    )

    row = (await session.execute(query)).tuples().first()

    assert row is not None

    holders, transfers = row

    return {
        "supply": utils.satoshis(token.supply, token.decimals),
        "reissuable": token.reissuable,
        "decimals": token.decimals,
        "transfers": transfers,
        "ticker": token.ticker,
        "type": token.type,
        "holders": holders,
    }


async def count_token_holders(session: AsyncSession, token: Token):
    return (
        await session.scalar(
            select(
                func.count(Balance.id).filter(
                    Balance.value > 0, Balance.token_id == token.id
                )
            )
        )
        or 0
    )


async def list_token_holders(
    session: AsyncSession, token: Token, limit: int, offset: int
):

    holders = await session.scalars(
        select(Balance)
        .filter(Balance.value > 0, Balance.token_id == token.id)
        .options(joinedload(Balance.address))
        .limit(limit)
        .offset(offset)
    )

    return [
        {
            "received": utils.satoshis(balance.received, token.decimals),
            "value": utils.satoshis(balance.value, token.decimals),
            "sent": utils.satoshis(balance.sent, token.decimals),
            "decimals": token.decimals,
            "address": balance.address.label,
            "ticker": token.ticker,
        }
        for balance in holders
    ]


def _transfers_fmt(
    *transfers: Transfer,
) -> list[dict[str, Any]]:  # pyright: ignore[reportExplicitAny]
    return [
        {
            "value": utils.satoshis(transfer.value, transfer.token.decimals),
            "receiver": transfer.receiver.label if transfer.receiver else None,
            "created": int(transfer.created.timestamp()),
            "sender": transfer.sender.label if transfer.sender else None,
            "category": transfer.category,
            "version": transfer.version,
            "decimals": transfer.token.decimals,
            "height": transfer.block.height,
            "token": transfer.token.ticker,
            "txid": transfer.txid,
        }
        for transfer in transfers
    ]


def _transfers_options() -> tuple[_AbstractLoad, ...]:
    return (
        joinedload(Transfer.sender),
        joinedload(Transfer.receiver),
        joinedload(Transfer.block),
        joinedload(Transfer.token),
    )


async def count_token_transfers(session: AsyncSession, token: Token):
    return (
        await session.scalar(
            select(func.count(Transfer.id)).filter(Transfer.token_id == token.id)
        )
        or 0
    )


async def list_token_transfers(
    session: AsyncSession, token: Token, limit: int, offset: int
):
    transfers = await session.scalars(
        select(Transfer)
        .filter(Transfer.token_id == token.id)
        .options(*_transfers_options())
        .limit(limit)
        .offset(offset)
    )

    return _transfers_fmt(*transfers)


async def count_transfers(session: AsyncSession):
    return await session.scalar(select(func.count(Transfer.id))) or 0


async def list_transfers(session: AsyncSession, limit: int, offset: int):
    transfers = await session.scalars(
        select(Transfer)
        .order_by(Transfer.created.desc().limit(limit).offset(offset))
        .options(*_transfers_options())
    )

    return _transfers_fmt(*transfers)


async def count_transaction_transfers(session: AsyncSession, txid: str):
    return (
        await session.scalar(
            select(func.count(Transfer.id)).filter(Transfer.txid == txid)
        )
        or 0
    )


async def list_transaction_transfers(
    session: AsyncSession, txid: str, limit: int, offset: int
):

    transfers = await session.scalars(
        select(Transfer)
        .filter(Transfer.txid == txid)
        .limit(limit)
        .offset(offset)
        .order_by(Transfer.created.desc())
        .options(*_transfers_options())
    )

    return _transfers_fmt(*transfers)
