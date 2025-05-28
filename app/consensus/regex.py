from ..chain import get_chain
from .. import constants
import config
import re

def ticker(ticker: str) -> dict:
    chain = get_chain(config.chain)

    PROTECTED_NAMES = re.compile("^" + "$|^".join(chain["protected"]) + "$")

    ROOT_NAME_CHARACTERS = re.compile(r"^[A-Z0-9._]{3,}$")
    SUB_NAME_CHARACTERS = re.compile(r"^[A-Z0-9._]+$")
    UNIQUE_TAG_CHARACTERS = re.compile(r"^[-A-Za-z0-9@$%&*()[\]{}_.?:]+$")

    DOUBLE_PUNCTUATION = re.compile(r"^.*[._]{2,}.*$")
    LEADING_PUNCTUATION = re.compile(r"^[._].*$")
    TRAILING_PUNCTUATION = re.compile(r"^.*[._]$")

    result = {
        "valid": False, "parent": None, "error": None,
        "type": None, "ticker": ticker,
        "owner": False
    }

    if ticker.endswith(constants.FLAG_OWNER):
        result["owner"] = True
        ticker = ticker[:-1]

    if len(ticker) not in range(
        constants.MIN_TICKER_LENGTH, constants.MAX_TICKER_LENGTH
    ):
        result["error"] = "Invalid ticker length"
        return result

    if ticker.count(constants.FLAG_UNIQUE) > 1:
        result["error"] = "Bad unique ticker"
        return result

    # After that the variables should be like this:
    # unique_token - list with 0-1 elements
    # sub_tokens - list with 0-n elements
    # root_token - list with 1 element

    unique_token = ticker.split(constants.FLAG_UNIQUE)
    sub_tokens = unique_token.pop(0).split(constants.FLAG_SUB)
    root_token = [sub_tokens.pop(0)]

    if unique_token and constants.FLAG_SUB in unique_token[0]:
        result["error"] = "Malformed ticker"
        return result

    if not ROOT_NAME_CHARACTERS.match(root_token[0]):
        result["error"] = "Invalid root name"
        return result

    for sub_token in sub_tokens:
        if not SUB_NAME_CHARACTERS.match(sub_token):
            result["error"] = "Invalid sub name"
            return result

    if unique_token and not UNIQUE_TAG_CHARACTERS.match(unique_token[0]):
        result["error"] = "Invalid unique name"
        return result

    for part in unique_token + sub_tokens + root_token:
        if PROTECTED_NAMES.match(part):
            result["error"] = "Protected name"
            return result

        if DOUBLE_PUNCTUATION.match(part):
            result["error"] = "Double punctuation"
            return result

        if LEADING_PUNCTUATION.match(part):
            result["error"] = "Leading punctuation"
            return result

        if TRAILING_PUNCTUATION.match(part):
            result["error"] = "Trailing punctuation"
            return result

    if unique_token:
        if result["owner"]:
            result["error"] = "Unique token can't have owner"
            return result

        parent_name = constants.FLAG_SUB.join(root_token + sub_tokens)

        result["valid"] = True
        result["parent"] = parent_name
        result["type"] = constants.TOKEN_UNIQUE

        return result

    if sub_tokens:
        parent_name = constants.FLAG_SUB.join(root_token + sub_tokens[:-1])

        result["parent"] = parent_name
        result["type"] = constants.TOKEN_SUB
        result["valid"] = True

        if result["owner"]:
            result["type"] = constants.TOKEN_OWNER

        return result

    if root_token:
        result["valid"] = True
        result["type"] = constants.TOKEN_ROOT

        if result["owner"]:
            result["type"] = constants.TOKEN_OWNER

        return result

    result["error"] = "Unknown error"

    return result
