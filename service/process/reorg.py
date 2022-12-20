from tortoise.transactions import atomic

@atomic()
async def process_reorg(block):
    await block.delete()
