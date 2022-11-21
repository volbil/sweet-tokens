from apscheduler.schedulers.asyncio import AsyncIOScheduler
from service.scheduler import parse_blockchain
import asyncio

def init_scheduler():
    scheduler = AsyncIOScheduler()

    scheduler.add_job(parse_blockchain, "interval", seconds=10)
    scheduler.start()

    try:
        asyncio.get_event_loop().run_forever()
    except (KeyboardInterrupt, SystemExit):
        pass

if __name__ == "__main__":
    init_scheduler()
