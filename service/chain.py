CHAIN = {
    "mbc-mainnet": {
        "id": "01",
        "genesis": {
            "hash": "ac3be150a8dcbb2db6df462a9875c67f55e845de40cb49dc2e30f4dfab9b9115",
            "height": 1672530
        },
        "decimals": 4,
        "admin": {
            "mbc1q3tv8yfalfkrxdhez8ksuwqar25wv5skuwuh32n": [1670859, None]
        },
        "fee": 1000,  # 0.1 MBC in satoshis
        "marker": 1000,  # 0.1 MBC in satoshis
    },
    "mbc-testnet": {
        "id": "02",
        "genesis": {
            "hash": "cdbb477ce0c62161a45dff151142f5e7742a8f6208c1a7b0259b0cd580a68f0f",
            "height": 113
        },
        "decimals": 4,
        "admin": {
            "rmbc1qk0u42kmvld9ewza7w0tm2ul6cfdywrd0pcx4t6": [113, None]
        },
        "fee": 1000,  # 0.1 MBC in satoshis
        "marker": 1000,  # 0.1 MBC in satoshis
    }
}

def get_chain(name):
    if name not in CHAIN:
        raise ValueError(f"Invalid chain name {name}")

    return CHAIN[name]