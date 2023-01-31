from service.utils import log_message
from service import constants

def value(value):
    if value < constants.MIN_VALUE or value > constants.MAX_VALUE:
        log_message(f"Value {value} not met constraints")
        return False

    return True
