from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Unban, Address
from app.utils import log_message
from sqlalchemy import select


async def process_unban(session: AsyncSession, inputs, outputs, block, txid):
    send_address_label = list(inputs)[0]
    outputs.pop(send_address_label)
    receive_address_label = list(outputs)[0]

    send_address = await session.scalar(
        select(Address).filter(Address.label == send_address_label)
    )

    if not (
        receive_address := await session.scalar(
            select(Address).filter(Address.label == receive_address_label)
        )
    ):
        receive_address = Address(**{"label": receive_address_label})
        session.add(receive_address)

    session.add(
        Unban(
            **{
                "address": receive_address,
                "admin": send_address,
                "block": block,
                "txid": txid,
            }
        )
    )

    receive_address.banned = False

    admin = send_address_label
    banned = send_address_label

    log_message(f"Address {banned} unbanned by {admin}")

    await session.commit()
