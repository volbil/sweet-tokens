from tortoise.transactions import atomic
from ..models import Balance, Lock
from ..utils import log_message
from .. import constants

@atomic()
async def process_reorg(block):
    async for transfer in block.transfers:
        if transfer.category == constants.CATEGORY_CREATE:
            token = await transfer.token
            await token.delete()

            log_message(f"Rollback token {token.ticker} creation")

        if transfer.category == constants.CATEGORY_ISSUE:
            receiver = await transfer.receiver
            token = await transfer.token

            receiver_balance = await Balance.filter(
                address=receiver, token=token
            ).first()

            receiver_balance.received -= transfer.value
            receiver_balance.value -= transfer.value
            await receiver_balance.save()

            token.supply -= transfer.value
            await token.save()

            log_message(f"Rollback token {token.ticker} supply issue")

        if transfer.category == constants.CATEGORY_TRANSFER:
            receiver = await transfer.receiver
            sender = await transfer.receiver
            token = await transfer.token

            receiver_balance = await Balance.filter(
                address=receiver, token=token
            ).first()

            sender_balance = await Balance.filter(
                address=sender, token=token
            ).first()

            sender_balance.value += transfer.value
            sender_balance.sent -= transfer.value
            await sender_balance.save()

            receiver_balance.received -= transfer.value

            if transfer.has_lock:
                receiver_balance.locked -= transfer.value

            else:
                receiver_balance.value -= transfer.value

            await receiver_balance.save()

            log_message(f"Rollback {transfer.value} {token.ticker} transfer")

    async for ban in block.bans:
        address = await ban.address
        address.banned = False
        await address.save()
        await ban.delete()

        log_message(f"Rollback address {address.label} ban")

    async for unban in block.unbans:
        address = await unban.address
        address.banned = True
        await address.save()
        await unban.delete()

        log_message(f"Rollback address {address.label} unban")

    locks = await Lock.filter(unlock_height=block.height)

    for lock in locks:
        transfer = await lock.transfer
        address = await lock.address
        token = await lock.token

        balance = await Balance.filter(
            address=address, token=token
        ).first()

        balance.locked += transfer.value
        balance.value -= transfer.value

        await balance.save()

        log_message(
            f"Rollback lock {transfer.value} {token.ticker} to {address.label}"
        )

    await block.delete()
