from ..models import FeeAddress, Address
from ..utils import log_message

async def process_fee_address(inputs, outputs, block):
    send_address_label = list(inputs)[0]
    outputs.pop(send_address_label)
    receive_address_label = list(outputs)[0]

    send_address = await Address.filter(label=send_address_label).first()

    fee = await FeeAddress.create(**{
        "label": receive_address_label,
        "height": block.height,
        "admin": send_address,
        "block": block
    })

    admin = send_address_label

    log_message(f"Fee address updated to {fee.label} by {admin}")
