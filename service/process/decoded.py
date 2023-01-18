from tortoise.transactions import atomic
from .transfer import process_transfer
from .create import process_create
from .issue import process_issue
from .unban import process_unban
from .ban import process_ban
from .. import constants
from .. import consensus

@atomic()
async def process_decoded(
    decoded, inputs, outputs, block, txid
):
    category = decoded["category"]
    valid = True

    if category == constants.CREATE:
        # Validate create payload
        if await consensus.validate_create(
            decoded, inputs, block.height
        ):
            await process_create(
                decoded, inputs, block, txid
            )

    if category == constants.ISSUE:
        # Validate issue payload
        if await consensus.validate_issue(
            decoded, inputs, block.height
        ):
            await process_issue(
                decoded, inputs, block, txid
            )

    if category == constants.TRANSFER:
        # Validate issue payload
        if await consensus.validate_transfer(
            decoded, inputs, outputs, block.height
        ):
            await process_transfer(
                decoded, inputs, outputs, block, txid
            )

    if category == constants.BAN:
        if await consensus.validate_admin(inputs, outputs, block.height, True):
            await process_ban(
                inputs, outputs, block, txid
            )

    if category == constants.UNBAN:
        if await consensus.validate_admin(inputs, outputs, block.height, False):
            await process_unban(
                inputs, outputs, block, txid
            )

    return valid
