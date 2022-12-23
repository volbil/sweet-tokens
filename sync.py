from apscheduler.schedulers.asyncio import AsyncIOScheduler
from service.sync import sync_chain
import asyncio

def init_scheduler():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(sync_chain, "interval", seconds=10)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    init_scheduler()
