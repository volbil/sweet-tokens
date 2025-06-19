from app.utils import log_message, get_settings
from app.chain import get_chain


def admin(send_address_label, height):
    settings = get_settings()
    chain = get_chain(settings.general.chain)

    if not send_address_label in chain["admin"]:
        log_message(f"Address {send_address_label} not in admin list")
        return False

    if chain["admin"][send_address_label][0] > height:
        log_message(f"Address {send_address_label} not yet admin")
        return False

    if (
        chain["admin"][send_address_label][1]
        and chain["admin"][send_address_label][1] < height
    ):
        log_message(f"Address {send_address_label} not admin anymore")
        return False

    return True
