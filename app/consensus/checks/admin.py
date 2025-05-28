from service.utils import log_message
from service.chain import get_chain
import config

def admin(send_address_label, height):
    chain = get_chain(config.chain)

    if not send_address_label in chain["admin"]:
        log_message(f"Address {send_address_label} not in admin list")
        return False

    if chain["admin"][send_address_label][0] > height:
        log_message(f"Address {send_address_label} not yet admin")
        return False

    if chain["admin"][
        send_address_label
    ][1] and chain["admin"][
        send_address_label
    ][1] < height:
        log_message(f"Address {send_address_label} not admin anymore")
        return False

    return True
