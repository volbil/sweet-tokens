from service import constants
from .. import checks

async def validate_create(decoded, inputs, outputs):
    if not checks.inputs_len(inputs):
        return False

    if not checks.outputs_len(outputs):
        return False

    if not (receive_address := checks.receiver(inputs, outputs)):
        return False

    send_address = list(inputs)[0]

    # Check value for new token
    if not checks.value(decoded["value"]):
        return False

    # Check decimal points for new token
    if not checks.decimals(decoded["decimals"]):
        return False

    # Check if new token supply within constraints
    if not await checks.supply_create(
        decoded["value"], decoded["decimals"]
    ):
        return False

    # Check ticker length and if it's available
    if not await checks.ticker(decoded["ticker"]):
        return False

    # Check ticker type constraints
    if not checks.ticker_type(
        decoded["ticker"], decoded["reissuable"],
        decoded["decimals"], decoded["value"]
    ):
        return False

    # Check if sender owns parrent token
    if not await checks.owner_parent(decoded["ticker"], send_address):
        return False

    # Check if fee is enough for given action
    if not await checks.token_fee(
        receive_address, outputs[receive_address],
        decoded["ticker"], constants.ACTION_CREATE
    ):
        return False

    return True
