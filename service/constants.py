# Token layer genesis block
GENESIS = {
    "hash": "ac3be150a8dcbb2db6df462a9875c67f55e845de40cb49dc2e30f4dfab9b9115",
    "height": 1672530
}

# Token layer admin addresses
ADMIN_ADDRESSES = {
    "mbc1q3tv8yfalfkrxdhez8ksuwqar25wv5skuwuh32n": [1670859, None]
}

# Network decimals
NETWORK_DECIMALS = 4

# Transaction build default fee
DEFAULT_FEE = 0.015

# Transaction build default marker
DEFAULT_MARKER = 0.1

# Transfer categories
CATEGORY_TRANSFER = "transfer"
CATEGORY_CREATE = "create"
CATEGORY_ISSUE = "issue"

# Payload categories
CREATE = 1
ISSUE = 2
TRANSFER = 3
BAN = 4
UNBAN = 5

# Consensus decimals constraints
MIN_DECIMALS = 0
MAX_DECIMALS = 8

# Consensus ticker length
MIN_TICKER_LENGTH = 3
MAX_TICKER_LENGTH = 8

# Consensus value constraints
MIN_VALUE = 1
MAX_VALUE = 10000000000000000000

# Consensus max supply
MAX_SUPPLY = 100000000000

TICKER_RE = "^[A-Z0-9_.-]*$"
