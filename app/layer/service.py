from sqlalchemy import Select, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from typing import Any
import typing

from app.models import Balance, Block, Token, Transfer
from app import constants, utils
from app.chain import get_chain

from sqlalchemy.orm.strategy_options import (
    _AbstractLoad,  # pyright: ignore[reportPrivateUsage]
)

from app.models.address import Address
from app.models.cost import FeeAddress, TokenCost


async def get_token(session: AsyncSession, ticker: str):
    return await session.scalar(select(Token).filter(Token.ticker == ticker))


async def get_address(session: AsyncSession, label: str):
    return await session.scalar(select(Address).filter(Address.label == label))


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
        .order_by(Transfer.created.desc())
        .limit(limit)
        .offset(offset)
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


async def get_address_info(session: AsyncSession, address: Address):
    balances = await session.stream_scalars(
        select(Balance)
        .filter(Balance.address_id == address.id)
        .options(joinedload(Balance.token))
    )

    query_transfers_count = select(func.count(Transfer.id)).filter(
        or_(Transfer.receiver_id == address.id, Transfer.sender_id == address.id)
    )

    total_transfers = await session.scalar(query_transfers_count) or 0
    total_balances = (
        await session.scalar(
            select(func.count(Balance.id)).filter(Balance.address_id == address.id)
        )
        or 0
    )
    stats = {"transfers": total_transfers, "balances": total_balances}

    return {
        "stats": stats,
        "balances": [
            {
                "received": utils.satoshis(balance.received, balance.token.decimals),
                "value": utils.satoshis(balance.value, balance.token.decimals),
                "sent": utils.satoshis(balance.sent, balance.token.decimals),
                "decimals": balance.token.decimals,
                "address": address.label,
                "transfers": await session.scalar(
                    query_transfers_count.filter(Transfer.token_id == balance.token_id)
                ),
                "ticker": balance.token.ticker,
            }
            async for balance in balances
        ],
    }


async def count_address_transfers(session: AsyncSession, address: Address):
    return (
        await session.scalar(
            select(func.count(Transfer.id)).filter(
                or_(
                    Transfer.sender_id == address.id, Transfer.receiver_id == address.id
                )
            )
        )
        or 0
    )


async def list_address_transfers(
    session: AsyncSession,
    address: Address,
    limit: int,
    offset: int,
):
    transfers = await session.scalars(
        select(Transfer)
        .filter(
            or_(Transfer.sender_id == address.id, Transfer.receiver_id == address.id)
        )
        .options(*_transfers_options())
        .order_by(Transfer.created.desc())
        .limit(limit)
        .offset(offset)
    )

    return _transfers_fmt(*transfers)


async def count_address_token_transfers(
    session: AsyncSession, address: Address, token: Token
):
    return (
        await session.scalar(
            select(func.count(Transfer.id)).filter(
                or_(
                    Transfer.sender_id == address.id, Transfer.receiver_id == address.id
                ),
                Transfer.token_id == token.id,
            )
        )
        or 0
    )


async def list_address_token_transfers(
    session: AsyncSession,
    address: Address,
    token: Token,
    limit: int,
    offset: int,
):
    transfers = await session.scalars(
        select(Transfer)
        .filter(
            or_(Transfer.sender_id == address.id, Transfer.receiver_id == address.id),
            Transfer.token_id == token.id,
        )
        .options(*_transfers_options())
        .order_by(Transfer.created.desc())
        .limit(limit)
        .offset(offset)
    )

    return _transfers_fmt(*transfers)


async def get_params(session: AsyncSession):
    settings: typing.Any = utils.get_settings()
    chain: dict[str, typing.Any] = get_chain(settings.general.chain)
    latest = await session.scalar(select(Block).order_by(Block.height.desc()).limit(1))
    assert latest

    fee_address = await session.scalar(
        select(FeeAddress).order_by(FeeAddress.height.desc()).limit(1)
    )
    assert fee_address

    create_root = await session.scalar(
        select(TokenCost)
        .filter(
            TokenCost.action == constants.ACTION_CREATE,
            TokenCost.type == constants.TOKEN_ROOT,
        )
        .order_by(TokenCost.height.desc())
        .limit(1)
    )
    assert create_root
    create_sub = await session.scalar(
        select(TokenCost)
        .filter(
            TokenCost.action == constants.ACTION_CREATE,
            TokenCost.type == constants.TOKEN_SUB,
        )
        .order_by(TokenCost.height.desc())
        .limit(1)
    )
    assert create_sub
    create_unique = await session.scalar(
        select(TokenCost)
        .filter(
            TokenCost.action == constants.ACTION_CREATE,
            TokenCost.type == constants.TOKEN_UNIQUE,
        )
        .order_by(TokenCost.height.desc())
        .limit(1)
    )
    assert create_unique

    issue_root = await session.scalar(
        select(TokenCost)
        .filter(
            TokenCost.action == constants.ACTION_ISSUE,
            TokenCost.type == constants.TOKEN_ROOT,
        )
        .order_by(TokenCost.height.desc())
        .limit(1)
    )
    assert issue_root
    issue_sub = await session.scalar(
        select(TokenCost)
        .filter(
            TokenCost.action == constants.ACTION_ISSUE,
            TokenCost.type == constants.TOKEN_SUB,
        )
        .order_by(TokenCost.height.desc())
        .limit(1)
    )
    assert issue_sub

    admin: list[str] = []

    for address in chain["admin"]:
        if chain["admin"][address][0] > latest.height:
            continue

        if chain["admin"][address][1] and chain["admin"][address][1] < latest.height:
            continue

        admin.append(address)

    return {
        "chain": settings.general.chain,
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
