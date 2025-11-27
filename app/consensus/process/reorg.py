from app.models import Transfer, Balance, Lock, Unban, Ban
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload
from app.utils import log_message
from sqlalchemy import select
from app import constants


async def process_reorg(session: AsyncSession, block):
    transfers = await session.stream_scalars(
        select(Transfer)
        .options(joinedload(Transfer.receiver))
        .options(joinedload(Transfer.sender))
        .options(joinedload(Transfer.token))
        .filter(Transfer.block == block)
    )

    async for transfer in transfers:
        if transfer.category == constants.CATEGORY_CREATE:
            ticker = transfer.token

            # Since we deleting token here all relacted records like balances
            # should be deleted via cascade deletion
            await session.delete(transfer.token)

            log_message(f"Rollback token {ticker} creation")

        if transfer.category == constants.CATEGORY_ISSUE:
            receiver_balance = await session.scalar(
                select(Balance).filter(
                    Balance.address == transfer.receiver,
                    Balance.token == transfer.token,
                )
            )

            receiver_balance.received -= transfer.value
            receiver_balance.value -= transfer.value

            token.supply -= transfer.value

            log_message(f"Rollback token {token.ticker} supply issue")

        if transfer.category == constants.CATEGORY_TRANSFER:
            receiver_balance = await session.scalar(
                select(Balance).filter(
                    Balance.address == transfer.receiver,
                    Balance.token == transfer.token,
                )
            )

            sender_balance = await session.scalar(
                select(Balance).filter(
                    Balance.address == transfer.sender,
                    Balance.token == transfer.token,
                )
            )

            sender_balance.value += transfer.value
            sender_balance.sent -= transfer.value

            receiver_balance.received -= transfer.value

            if transfer.has_lock:
                receiver_balance.locked -= transfer.value

            else:
                receiver_balance.value -= transfer.value

            log_message(f"Rollback {transfer.value} {token.ticker} transfer")

    bans = await session.scalars(
        select(Ban).options(joinedload(Ban.address)).filter(Ban.block == block)
    )

    unbans = await session.scalars(
        select(Unban).options(joinedload(Unban.address)).filter(Unban.block == block)
    )

    for ban in bans:
        ban.address.banned = False
        await session.delete(ban)
        log_message(f"Rollback address {address.label} ban")

    for unban in unbans:
        unban.address.banned = True
        await session.delete(unban)
        log_message(f"Rollback address {address.label} unban")

    locks = await session.scalars(
        select(Lock)
        .options(joinedload(Lock.transfer))
        .options(joinedload(Lock.address))
        .options(joinedload(Lock.token))
        .filter(Lock.unlock_height == block.height)
    )

    for lock in locks:
        balance = await session.scalar(
            select(Balance).filter(
                Balance.address == lock.address,
                Balance.token == lock.token,
            )
        )

        balance.locked += lock.transfer.value
        balance.value -= lock.transfer.value

        log_message(
            f"Rollback lock {lock.transfer.value} {lock.token.ticker} to {lock.address.label}"
        )

    await session.delete(block)
    await session.commit()
