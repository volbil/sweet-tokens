from ..models import Ban, Address
from ..utils import log_message

async def process_ban(inputs, outputs, block, txid):
    send_address_label = list(inputs)[0]
    outputs.pop(send_address_label)
    receive_address_label = list(outputs)[0]

    send_address = await Address.filter(label=send_address_label).first()

    if not (receive_address := await Address.filter(
        label=receive_address_label
    ).first()):
        receive_address = await Address.create(**{
            "label": receive_address_label
        })

    await Ban.create(**{
        "address": receive_address,
        "admin": send_address,
        "block": block,
        "txid": txid
    })

    receive_address.banned = True
    await receive_address.save()

    admin = send_address_label
    banned = send_address_label

    log_message(f"Address {banned} banned by {admin}")
