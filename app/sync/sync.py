from app.utils import make_request, log_message, get_settings
from app.process import process_block, process_reorg
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import sessionmanager
from app.process import process_locks
from app.parse import parse_block
from app.chain import get_chain
from sqlalchemy import select
from app.models import Block


async def emergency_reorg(reorg_height):
    latest = await Block.filter().order_by("-height").limit(1).first()

    # Process chain reorgs
    while reorg_height < latest.height:
        log_message(f"Found reorg at height #{latest.height}")

        reorg_block = latest
        latest = await Block.filter(height=(latest.height - 1)).first()

        await process_reorg(reorg_block)


async def sync_chain(session: AsyncSession):
    # Init genesis
    if not await session.scalar(
        select(Block).order_by(Block.height.desc()).limit(1)
    ):
        log_message("Adding genesis block to db")

        settings = get_settings()
        chain = get_chain(settings.general.chain)

        block_data = await parse_block(chain["genesis"]["height"])

        if block_data["block"]["hash"] != chain["genesis"]["hash"]:
            log_message("Genesis hash missmatch")
            raise

        await process_block(session, block_data)

    chain_data = await make_request("getblockchaininfo")
    latest = await session.scalar(
        select(Block).order_by(Block.height.desc()).limit(1)
    )

    # Process chain reorgs
    while latest.hash != await make_request("getblockhash", [latest.height]):
        log_message(f"Found reorg at height #{latest.height}")

        reorg_block = latest
        latest = await session.scalar(
            select(Block).filter(Block.height == latest.height - 1)
        )

        await process_reorg(reorg_block)

    display_log = latest.height + 10 > chain_data["blocks"]

    for height in range(latest.height + 1, chain_data["blocks"] + 1):
        try:
            if display_log:
                log_message(f"Processing block #{height}")
            else:
                if height % 100 == 0:
                    log_message(f"Processing block #{height}")

            block_data = await parse_block(height)

            await process_block(session, block_data)

            await process_locks(session, height)

        except KeyboardInterrupt:
            log_message(f"Keyboard interrupt")
            break


async def run_sync_chain():
    async with sessionmanager.session() as session:
        await sync_chain(session)
