from ..models import TokenCost, Address
from ..utils import log_message
from ..chain import get_chain
from ..utils import amount
import config

async def process_cost(decoded, inputs, block):
    chain = get_chain(config.chain)

    send_address_label = list(inputs)[0]

    send_address = await Address.filter(label=send_address_label).first()

    value = amount(decoded["value"], chain["decimals"])

    await TokenCost.create(**{
        "action": decoded["action"],
        "type": decoded["type"],
        "height": block.height,
        "admin": send_address,
        "value": value,
        "block": block
    })

    admin = send_address_label
    token_type = decoded["type"]

    log_message(f"Fee cost for {token_type} updated to {value} by {admin}")
