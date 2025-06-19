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
    Lock,
)


async def process_transfer(
    session: AsyncSession, decoded, inputs, outputs, block, txid
):
    send_address_label = list(inputs)[0]
    outputs.pop(send_address_label)
    receive_address_label = list(outputs)[0]

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

    if not (
        receive_address := await session.scalar(
            select(Address).filter(Address.label == receive_address_label)
        )
    ):
        receive_address = Address(**{"label": receive_address_label})
        session.add(receive_address)

    # We have this check in place for some edge cases like regorg
    # This way we make sure that we won't create multiple balances
    if not (
        receive_balance := await session.scalar(
            select(Balance).filter(
                Balance.address == receive_address,
                Balance.token == token,
            )
        )
    ):
        receive_balance = Balance(
            **{
                "address": receive_address,
                "token": token,
                "received": 0,
                "locked": 0,
                "value": 0,
                "sent": 0,
            }
        )
        session.add(receive_balance)

    has_lock = decoded["lock"] != None

    transfer = Transfer(
        **{
            "value": float_to_decimal(value),
            "category": constants.CATEGORY_TRANSFER,
            "version": decoded["version"],
            "receiver": receive_address,
            "created": block.created,
            "sender": send_address,
            "has_lock": has_lock,
            "token": token,
            "block": block,
            "txid": txid,
        }
    )

    send_balance.value -= transfer.value
    send_balance.sent += transfer.value

    receive_balance.received += transfer.value

    if has_lock and decoded["lock"] > block.height:
        receive_balance.locked += transfer.value

        session.add(
            Lock(
                **{
                    "unlock_height": decoded["lock"],
                    "address": receive_address,
                    "value": transfer.value,
                    "transfer": transfer,
                    "token": token,
                }
            )
        )

    else:
        receive_balance.value += transfer.value

    session.add_all(
        [
            Index(
                **{
                    "category": constants.CATEGORY_TRANSFER,
                    "created": block.created,
                    "address": send_address,
                    "transfer": transfer,
                    "token": token,
                }
            ),
            Index(
                **{
                    "category": constants.CATEGORY_TRANSFER,
                    "address": receive_address,
                    "created": block.created,
                    "transfer": transfer,
                    "token": token,
                }
            ),
        ]
    )

    log_message(f"Transfered {value} {token.ticker}")

    await session.commit()
