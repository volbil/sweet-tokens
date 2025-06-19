from app.utils import log_message, get_settings, amount
from app.models import TokenCost, Address
from app.chain import get_chain


async def process_cost(decoded, inputs, block):
    settings = get_settings()
    chain = get_chain(settings.general.chain)

    send_address_label = list(inputs)[0]

    send_address = await Address.filter(label=send_address_label).first()

    value = amount(decoded["value"], chain["decimals"])

    await TokenCost.create(
        **{
            "action": decoded["action"],
            "type": decoded["type"],
            "height": block.height,
            "admin": send_address,
            "value": value,
            "block": block,
        }
    )

    admin = send_address_label
    token_type = decoded["type"]

    log_message(f"Fee cost for {token_type} updated to {value} by {admin}")
