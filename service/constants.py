# Token layer genesis block
GENESIS = {
    "hash": "301e5324cc205c4d10e5b4cd9222231e0e0cdc1e8bdcd543985138d2c23b50c6",
    "height": 1670859
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
