from app.utils import log_message
from app import constants


def decimals(decimals):
    if decimals < constants.MIN_DECIMALS or decimals > constants.MAX_DECIMALS:
        log_message(f"Decimals {decimals} not met constraints")
        return False

    return True
