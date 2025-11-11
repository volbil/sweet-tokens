from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

from app.database import sessionmanager
from app.utils import get_settings


async def init_scheduler():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    scheduler = AsyncIOScheduler()

    from app.sync import run_sync_chain

    scheduler.add_job(run_sync_chain, "interval", seconds=10)
    scheduler.start()

    try:
        await asyncio.Event().wait()
    except (KeyboardInterrupt, SystemExit):
        pass


if __name__ == "__main__":
    asyncio.run(init_scheduler())
