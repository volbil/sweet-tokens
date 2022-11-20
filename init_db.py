from tortoise import Tortoise, run_async
from service.models import Settings
import config

async def init_db():
    await Tortoise.init(**config.tortoise)

    await Tortoise.generate_schemas()

    if not (await Settings.first()):
        settings = await Settings.create(**{
            "current_height": 0
        })

if __name__ == "__main__":
    run_async(init_db())
