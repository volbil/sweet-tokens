from sqlalchemy.ext.asyncio import AsyncSession
from app.models import FeeAddress, Address
from app.utils import log_message
from sqlalchemy import select


async def process_fee_address(session: AsyncSession, inputs, outputs, block):
    send_address_label = list(inputs)[0]
    outputs.pop(send_address_label)
    receive_address_label = list(outputs)[0]

    send_address = await session.scalar(
        select(Address).filter(Address.label == send_address_label)
    )

    fee = await FeeAddress(
        **{
            "label": receive_address_label,
            "height": block.height,
            "admin": send_address,
            "block": block,
        }
    )

    session.add(fee)

    admin = send_address_label

    log_message(f"Fee address updated to {fee.label} by {admin}")
