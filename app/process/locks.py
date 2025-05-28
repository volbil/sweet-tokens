from ..models import Lock, Balance
from ..utils import log_message

async def process_locks(height):
    locks = await Lock.filter(unlock_height=height)

    for lock in locks:
        transfer = await lock.transfer
        address = await lock.address
        token = await lock.token

        balance = await Balance.filter(
            address=address, token=token
        ).first()

        balance.locked -= transfer.value
        balance.value += transfer.value

        await balance.save()

        log_message(
            f"Unlocked {transfer.value} {token.ticker} to {address.label}"
        )
