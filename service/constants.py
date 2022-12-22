# Token layer genesis block
GENESIS = {
    "hash": "7a374ce1bc57589bf28331616b28e16438381f04ac6a233384e3485ff4fd7c28",
    "height": 100
}

# Network decimals
NETWORK_DECIMALS = 4

# Transaction build default fee
DEFAULT_FEE = 0.015

# Transaction build default marker
DEFAULT_MARKER = 0.1

# Transfer categories
CATEGORY_CREATE = "create"
CATEGORY_ISSUE = "issue"
CATEGORY_TRANSFER = "transfer"

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

# Token layer admin addresses
ADMIN_ADDRESSES = {
    "rmbc1qlduvy4qs5qumemkuewe5huecgunxlsuw5vgsk6": [0, None]
}
