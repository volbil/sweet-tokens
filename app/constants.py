# System version
VERSION = "0.2.2"

DEFAULT_VERSION = 1
MIN_VERSION = 1
MAX_VERSION = 1

# Transfer categories
CATEGORY_TRANSFER = "transfer"
CATEGORY_CREATE = "create"
CATEGORY_ISSUE = "issue"
CATEGORY_BURN = "burn"

# Cost actions
ACTION_CREATE = "create"
ACTION_ISSUE = "issue"

ACTIONS_RE = "^create$|^issue$"

# Token types
TOKEN_ROOT = "root"
TOKEN_SUB = "sub"
TOKEN_UNIQUE = "unique"
TOKEN_OWNER = "owner"

TOKEN_TYPE_RE = "^root$|^sub$|^unique$"

# Ticker flags
FLAG_SUB = "/"
FLAG_UNIQUE = "#"
FLAG_OWNER = "!"

# Payload categories
CREATE = 1
ISSUE = 2
TRANSFER = 3
BAN = 4
UNBAN = 5
BURN = 6
FEE_ADDRESS = 7
COST = 8

# Consensus decimals constraints
MIN_DECIMALS = 0
MAX_DECIMALS = 8

# Consensus ticker length
MIN_TICKER_LENGTH = 3
MAX_TICKER_LENGTH = 32

# Consensus value constraints
MIN_VALUE = 1
MAX_VALUE = 10_000_000_000_000_000_000_000

# Consensus max supply
MAX_SUPPLY = 100_000_000_000_000
