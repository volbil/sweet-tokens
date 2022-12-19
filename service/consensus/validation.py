from ..utils import log_message
from . import checks

async def validate_create(decoded, inputs, height):
    if len(inputs) != 1:
        log_message("CREATE: Failed to check inputs")
        return False

    send_address = list(inputs)[0]

    # Check if transaction has been sent from admin address
    if not checks.admin(send_address, height):
        log_message("CREATE: Failed to check admin")
        return False

    # Check value for new token
    if not checks.value(decoded["value"]):
        log_message("CREATE: Failed to check value")
        return False

    # Check decimal points for new token
    if not checks.decimals(decoded["decimals"]):
        log_message("CREATE: Failed to check decimals")
        return False

    # Check if new token supply within constraints
    if not await checks.supply_create(
        decoded["value"], decoded["decimals"]
    ):
        log_message("CREATE: Failed to check supply")
        return False

    # Check ticker length and if it's available
    if not await checks.ticker(decoded["ticker"]):
        log_message("CREATE: Failed to check ticker")
        return False

    return True

async def validate_issue(decoded, inputs, height):
    if len(inputs) != 1:
        return False

    send_address = list(inputs)[0]

    # Check if transaction has been sent from admin address
    if not checks.admin(send_address, height):
        log_message("ISSUE: Failed to check admin")
        return False

    # Check value for new tokens issued
    if not checks.value(decoded["value"]):
        log_message("ISSUE: Failed to check value")
        return False

    # Check if token reissuable
    if not await checks.reissuable(decoded["ticker"]):
        log_message("ISSUE: Failed to check reissuable")
        return False

    # Check if token exists
    if not await checks.token(decoded["ticker"]):
        log_message("ISSUE: Failed to check token")
        return False

    # Check if token owner
    if not await checks.owner(decoded["ticker"], send_address):
        log_message("ISSUE: Failed to check owner")
        return False

    # Check if issued amount within supply constraints
    if not await checks.supply_issue(
        decoded["ticker"], decoded["value"]
    ):
        log_message("ISSUE: Failed to check supply")
        return False

    return True

async def validate_transfer(decoded, inputs, outputs):
    if len(inputs) != 1:
        log_message("TRANSFER: Failed to check inputs")
        return False

    if len(outputs) != 2:
        log_message("TRANSFER: Failed to check outputs")
        return False

    send_address = list(inputs)[0]

    # Check transfer value
    if not checks.value(decoded["value"]):
        log_message("TRANSFER: Failed to check value")
        return False

    # Check if token exists
    if not await checks.token(decoded["ticker"]):
        log_message("TRANSFER: Failed to check token")
        return False

    # Check if address has enough balance
    if not await checks.balance(
        decoded["ticker"], send_address, decoded["value"]
    ):
        log_message("TRANSFER: Failed to check balance")
        return False

    return True
