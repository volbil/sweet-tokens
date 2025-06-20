from app.utils import float_to_decimal, log_message, amount
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app import constants

from app.models import (
    Transfer,
    Balance,
    Address,
    Index,
    Token,
)


async def process_burn(session: AsyncSession, decoded, inputs, block, txid):
    send_address_label = list(inputs)[0]

    token = await session.scalar(
        select(Token).filter(Token.ticker == decoded["ticker"])
    )

    value = amount(decoded["value"], token.decimals)

    send_address = await session.scalar(
        select(Address).filter(Address.label == send_address_label)
    )

    send_balance = await session.scalar(
        select(Balance).filter(
            Balance.address == send_address, Balance.token == token
        )
    )

    transfer = Transfer(
        **{
            "value": float_to_decimal(value),
            "category": constants.CATEGORY_BURN,
            "version": decoded["version"],
            "created": block.created,
            "sender": send_address,
            "has_lock": False,
            "receiver": None,
            "token": token,
            "block": block,
            "txid": txid,
        }
    )

    session.add(transfer)

    send_balance.value -= transfer.value
    send_balance.sent += transfer.value

    token.supply -= transfer.value

    session.add(
        Index(
            **{
                "category": constants.CATEGORY_BURN,
                "created": block.created,
                "address": send_address,
                "transfer": transfer,
                "token": token,
            }
        )
    )

    log_message(f"Burned {value} {token.ticker}")

    await session.commit()
