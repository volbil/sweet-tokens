from .parse import parse_block, parse_transaction
from ..utils import make_request, log_message
from tortoise.transactions import atomic
from ..models import Block, Token
from ..protocol import Protocol
from tortoise import Tortoise
from ..utils import satoshis
from .. import constants
import config

@atomic()
async def process_block(data):
    block = await Block.create(**{
        "height": data["block"]["height"],
        "hash": data["block"]["hash"]
    })

    decoded = None
    outputs = {}
    inputs = {}

    for index, tx_data in enumerate(data["transactions"]):
        if index == 0:
            continue

        for input in tx_data["inputs"]:
            input_tx_data = await parse_transaction(input["output_txid"])
            input_output = input_tx_data["outputs"][input["output_index"]]

            if input_output["address"]:
                if input_output["address"] not in inputs:
                    inputs[input_output["address"]] = 0

                inputs[input_output["address"]] += satoshis(
                    input_output["value"], constants.NETWORK_DECIMALS
                )

        for output in tx_data["outputs"]:
            if output["script_type"] == "nulldata":
                payload = output["script_asm"].split(" ")[1]
                decoded = Protocol.decode(payload)

            if output["address"]:
                if output["address"] not in outputs:
                    outputs[output["address"]] = 0

                outputs[output["address"]] += satoshis(
                    output["value"], constants.NETWORK_DECIMALS
                )

    if decoded:
        if decoded["category"] == constants.CREATE:
            print(inputs)
            print(outputs)

        raise

@atomic()
async def process_reorg(block):
    await block.delete()

async def sync_chain():
    await Tortoise.init(config=config.tortoise)
    await Tortoise.generate_schemas()

    # Init genesis
    if not (await Block.filter().order_by("-height").limit(1).first()):
        log_message("Adding genesis block to db")

        block_data = await parse_block(0)
        await process_block(block_data)

    latest = await Block.filter().order_by("-height").limit(1).first()
    chain_data = await make_request("getblockchaininfo")

    # Process chain reorgs
    while latest.hash != await make_request("getblockhash", [latest.height]):
        log_message(f"Found reorg at height #{latest.height}")

        reorg_block = latest
        latest = await Block.filter(
            height=(latest.height - 1)
        ).first()

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

            try:
                await process_block(block_data)
            except:
                break

        except KeyboardInterrupt:
            log_message(f"Keyboard interrupt")
            break

    await Tortoise.close_connections()