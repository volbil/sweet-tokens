from sqlalchemy.ext.asyncio import AsyncSession
from app.utils import log_message
from app.models import Address
from sqlalchemy import select


async def banned(session: AsyncSession, address_label):
    if not (
        address := await session.scalar(
            select(Address).filter(Address.label == address_label)
        )
    ):
        log_message(f"Address {address_label} not found")
        return False

    return address.banned
