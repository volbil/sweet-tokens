from service.utils import log_message
from service.models import Address

async def banned(address_label):
    if not (address := await Address.filter(label=address_label).first()):
        log_message(f"Address {address_label} not found")
        return False

    return address.banned
