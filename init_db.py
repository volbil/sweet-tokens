from tortoise import Tortoise, run_async
from service.models import Address
import config

async def init_db():
    await Tortoise.init(**config.tortoise)

    await Tortoise.generate_schemas()

    if not (await Address.filter(raw_address=config.admin_address).first()):
        address = await Address.create(**{
            "raw_address": config.admin_address,
            "nonce": 0
        })

    await Tortoise.close_connections()


if __name__ == "__main__":
    run_async(init_db())
