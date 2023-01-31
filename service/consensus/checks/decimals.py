from service.utils import log_message
from service import constants

def decimals(decimals):
    if decimals < constants.MIN_DECIMALS or decimals > constants.MAX_DECIMALS:
        log_message(f"Decimals {decimals} not met constraints")
        return False

    return True
