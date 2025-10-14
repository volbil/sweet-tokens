import typing


CHAIN = {
    "mbc-mainnet": {
        "id": "01",
        "genesis": {
            "hash": "d7f7df92b379ce61a57a067f5597839d390798464f0c126f4e25c55087428136",
            "height": 1807100,
        },
        "decimals": 4,
        "admin": {"mbc1q3tv8yfalfkrxdhez8ksuwqar25wv5skuwuh32n": [1806960, None]},
        "fee": 1000,  # 0.1 MBC in satoshis
        "marker": 1000,  # 0.1 MBC in satoshis,
        "protected": ["MBC", "MICROBITCOIN"],
        "cost": {
            "address": "Bm47QN43BYKhSLDuiN8TLYMx2NcnmUWjWz",
            "create": {"root": 1, "sub": 615, "unique": 10},
            "issue": {"root": 51800, "sub": 615},
        },
    }
}


def get_chain(name) -> dict[str, typing.Any]:
    if name not in CHAIN:
        raise ValueError(f"Invalid chain name {name}")

    return CHAIN[name]
