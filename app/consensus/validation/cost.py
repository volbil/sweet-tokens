from service import constants
from .. import checks

async def validate_cost(decoded, inputs, height):
    if not checks.inputs_len(inputs):
        return False

    send_address = list(inputs)[0]

    # Check if transaction has been sent from admin address
    if not checks.admin(send_address, height):
        return False

    # Check cost value
    if not checks.value(decoded["value"]):
        return False

    # Check cost action (just in case)
    if decoded["action"] not in [
        constants.ACTION_CREATE, constants.ACTION_ISSUE
    ]:
        return False

    # Check cost type (just in case)
    if decoded["type"] not in [
        constants.TOKEN_ROOT, constants.TOKEN_SUB,
        constants.TOKEN_UNIQUE
    ]:
        return False

    return True
