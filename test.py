from service.sync import sync_chain
from tortoise import Tortoise
import asyncio
import config

async def main():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    await sync_chain()

if __name__ == "__main__":
    asyncio.run(main())
