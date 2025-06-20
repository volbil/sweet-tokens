from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.models import Lock, Balance
from app.utils import log_message
from sqlalchemy import select


async def process_locks(session: AsyncSession, height: int):
    locks = await session.scalars(
        select(Lock)
        .filter(Lock.unlock_height == height)
        .options(joinedload(Lock.transfer))
        .options(joinedload(Lock.address))
        .options(joinedload(Lock.token))
    )

    for lock in locks:
        balance = await session.scalar(
            select(Balance).filter(
                Balance.address == lock.address,
                Balance.token == lock.token,
            )
        )

        balance.locked -= lock.transfer.value
        balance.value += lock.transfer.value

        log_message(
            f"Unlocked {lock.transfer.value} {lock.token.ticker} to {lock.address.label}"
        )

    await session.commit()
