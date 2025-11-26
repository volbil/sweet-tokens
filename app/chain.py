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
    },
    "sugar-testnet": {
        "id": "02",
        "genesis": {
            "hash": "36a85721176bd211301caf19162728cb5864814930b7c8b254786b8511d6c3bc",
            "height": 39391879,
        },
        "decimals": 8,
        "admin": {"sugar1q9c3pq4yff5ukt4g2jp7ae672sz8fgnv2gvwgd6": [39130381, None]},
        "fee": 10000000,  # 0.1 SUGAR in satoshis
        "marker": 10000000,  # 0.1 SUGAR in satoshis,
        "protected": ["SUGAR", "SUGARCHAIN"],
        "cost": {
            "address": "sugar1q9c3pq4yff5ukt4g2jp7ae672sz8fgnv2gvwgd6",
            "create": {"root": 1, "sub": 1, "unique": 1},
            "issue": {"root": 1, "sub": 1},
        },
    },
}


def get_chain(name) -> dict[str, typing.Any]:
    if name not in CHAIN:
        raise ValueError(f"Invalid chain name {name}")

    return CHAIN[name]
