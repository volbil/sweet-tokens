from .. import checks

async def validate_burn(decoded, inputs):
    if not checks.inputs_len(inputs):
        return False

    send_address = list(inputs)[0]

    # Check burn value
    if not checks.value(decoded["value"]):
        return False

    # Check if token exists
    if not await checks.token(decoded["ticker"]):
        return False

    # Check if address has enough balance
    if not await checks.balance(
        decoded["ticker"], send_address, decoded["value"]
    ):
        return False

    return True
