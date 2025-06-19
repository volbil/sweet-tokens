from app.utils import float_to_decimal, log_message, amount
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import constants
from app import utils

from app.models import (
    Transfer,
    Balance,
    Address,
    Index,
    Token,
)


async def process_issue(session: AsyncSession, decoded, inputs, block, txid):
    send_address = list(inputs)[0]

    token = await session.scalar(
        select(Token).filter(Token.ticker == decoded["ticker"])
    )

    value = amount(decoded["value"], token.decimals)

    if not (
        address := await session.scalar(
            select(Address).filter(Address.label == send_address)
        )
    ):
        address = Address(**{"label": send_address})
        session.add(address)

    # We have this check in place for some edge cases like regorg
    # This way we make sure that we won't create multiple balances
    if not (
        balance := await session.scalar(
            select(Balance).filter(
                Balance.address == address,
                Balance.token == token,
            )
        )
    ):
        balance = Balance(
            **{
                "address": address,
                "token": token,
                "received": 0,
                "locked": 0,
                "value": 0,
                "sent": 0,
            }
        )
        session.add(balance)

    transfer = Transfer(
        **{
            "value": float_to_decimal(value),
            "category": constants.CATEGORY_ISSUE,
            "version": decoded["version"],
            "created": block.created,
            "receiver": address,
            "has_lock": False,
            "token": token,
            "block": block,
            "txid": txid,
        }
    )

    session.add(transfer)

    balance.received += transfer.value
    balance.value += transfer.value

    token.supply += transfer.value

    session.add(
        Index(
            **{
                "category": constants.CATEGORY_ISSUE,
                "created": block.created,
                "transfer": transfer,
                "address": address,
                "token": token,
            }
        )
    )

    log_message(f"Issued {value} {token.ticker}")

    await session.commit()
