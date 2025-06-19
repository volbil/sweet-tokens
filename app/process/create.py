from app.utils import log_message, float_to_decimal
from sqlalchemy.ext.asyncio import AsyncSession
from app.consensus import regex
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


async def process_create(session: AsyncSession, decoded, inputs, block, txid):
    send_address = list(inputs)[0]

    value = utils.amount(decoded["value"], decoded["decimals"])

    if not (
        address := await session.scalar(
            select(Address).filter(Address.label == send_address)
        )
    ):
        address = Address(**{"label": send_address})
        session.add(address)

    ticker_data = regex.ticker(decoded["ticker"])

    token = Token(
        **{
            "reissuable": decoded["reissuable"],
            "decimals": decoded["decimals"],
            "ticker": decoded["ticker"],
            "type": ticker_data["type"],
            "created": block.created,
            "supply": value,
        }
    )

    session.add(token)

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
            "category": constants.CATEGORY_CREATE,
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

    session.add(
        Index(
            **{
                "category": constants.CATEGORY_CREATE,
                "created": block.created,
                "transfer": transfer,
                "address": address,
                "token": token,
            }
        )
    )

    log_message(f"Created {value} {token.ticker}")

    need_owner = [constants.TOKEN_ROOT, constants.TOKEN_SUB]

    if ticker_data["type"] in need_owner and token.reissuable:
        token_owner = Token(
            **{
                "ticker": token.ticker + constants.FLAG_OWNER,
                "type": constants.TOKEN_OWNER,
                "created": block.created,
                "reissuable": False,
                "decimals": 0,
                "supply": 1,
            }
        )

        session.add(token_owner)

        if not (
            balance_owner := await session.scalar(
                select(Balance).filter(
                    Balance.address == address,
                    Balance.token == token_owner,
                )
            )
        ):
            balance_owner = Balance(
                **{
                    "token": token_owner,
                    "address": address,
                    "received": 0,
                    "locked": 0,
                    "value": 0,
                    "sent": 0,
                }
            )

            session.add(balance_owner)

        transfer_owner = Transfer(
            **{
                "category": constants.CATEGORY_CREATE,
                "version": decoded["version"],
                "created": block.created,
                "token": token_owner,
                "receiver": address,
                "has_lock": False,
                "block": block,
                "txid": txid,
                "value": 1,
            }
        )

        session.add(transfer_owner)

        balance_owner.received += transfer_owner.value
        balance_owner.value += transfer_owner.value

        session.add(
            Index(
                **{
                    "category": constants.CATEGORY_CREATE,
                    "transfer": transfer_owner,
                    "created": block.created,
                    "token": token_owner,
                    "address": address,
                }
            )
        )

        log_message(f"Created owner token {token_owner.ticker}")

    await session.commit()
