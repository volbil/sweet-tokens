from apscheduler.schedulers.asyncio import AsyncIOScheduler
from tortoise import Tortoise
import asyncio
import config

async def init_scheduler():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    scheduler = AsyncIOScheduler()

    from service.sync import sync_chain

    scheduler.add_job(sync_chain, "interval", seconds=10)
    scheduler.start()

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    asyncio.run(init_scheduler())
