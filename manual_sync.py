from app.database import sessionmanager
from app.sync import run_sync_chain
from app.utils import get_settings
import asyncio


async def manual_sync():
    settings = get_settings()

    sessionmanager.init(settings.database.endpoint)

    await run_sync_chain()

    await sessionmanager.close()


if __name__ == "__main__":
    asyncio.run(manual_sync())
