from app.schemas import CustomModel, datetime_pd


class BlockStats(CustomModel):
    transfers: int
    holders: int
    tokens: int


class BlockInfo(CustomModel):
    created: datetime_pd
    height: int
    hash: str
    stats: BlockStats


class TokenInfo(CustomModel):
    supply: int
    reissuable: bool
    decimals: int
    transfers: int
    ticker: str
    type: str
    holders: int


class TokenHolderInfo(CustomModel):
    received: int
    value: int
    sent: int
    decimals: int
    address: str
    ticker: str


class TokenTransferInfo(CustomModel):
    value: int
    receiver: str | None
    created: int
    sender: str | None
    category: str
    version: int
    decimals: int
    height: int
    token: str
    txid: str


class AddressStats(CustomModel):
    transfers: int
    balances: int


class BalanceInfo(CustomModel):
    received: int
    value: int
    sent: int
    decimals: int
    address: str
    transfers: int
    ticker: str


class AddressInfo(CustomModel):
    stats: AddressStats
    balances: list[BalanceInfo]


class CostInfo(CustomModel):
    create: dict[str, int]
    issue: dict[str, int]


class LayerParams(CustomModel):
    chain: str
    fee_address: str
    cost: CostInfo
    admin: list[str]
