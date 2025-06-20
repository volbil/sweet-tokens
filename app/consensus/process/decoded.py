from sqlalchemy.ext.asyncio import AsyncSession
from .transfer import process_transfer
from .fee import process_fee_address
from .create import process_create
from .issue import process_issue
from .unban import process_unban
from .burn import process_burn
from .cost import process_cost
from .ban import process_ban
from app import constants
from app import consensus


async def process_decoded(
    session: AsyncSession, decoded, inputs, outputs, block, txid
):
    category = decoded["category"]
    valid = True

    if category == constants.CREATE:
        # Validate create payload
        if await consensus.validate_create(session, decoded, inputs, outputs):
            await process_create(session, decoded, inputs, block, txid)

    if category == constants.ISSUE:
        # Validate issue payload
        if await consensus.validate_issue(session, decoded, inputs, outputs):
            await process_issue(session, decoded, inputs, block, txid)

    if category == constants.TRANSFER:
        # Validate transfer payload
        if await consensus.validate_transfer(
            session, decoded, inputs, outputs, block.height
        ):
            await process_transfer(
                session, decoded, inputs, outputs, block, txid
            )

    if category == constants.BURN:
        # Validate burn payload
        if await consensus.validate_burn(session, decoded, inputs):
            await process_burn(session, decoded, inputs, block, txid)

    if category == constants.BAN:
        # Validate admin
        if await consensus.validate_admin_ban(
            session, inputs, outputs, block.height, True
        ):
            await process_ban(inputs, outputs, block, txid)

    if category == constants.UNBAN:
        # Validate admin
        if await consensus.validate_admin_ban(
            session, inputs, outputs, block.height, False
        ):
            await process_unban(inputs, outputs, block, txid)

    if category == constants.FEE_ADDRESS:
        # Validate admin
        if await consensus.validate_admin(inputs, outputs, block.height):
            await process_fee_address(session, inputs, outputs, block)

    if category == constants.COST:
        # Validate cost update
        if await consensus.validate_cost(decoded, inputs, block.height):
            await process_cost(session, decoded, inputs, block)

    return valid
