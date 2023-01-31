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
        "marker": 1000,  # 0.1 MBC in satoshis,
        "protected": ["MBC", "MICROBITCOIN"],
        "cost": {
            "address": None,
            "create": {
                "root": 10.0,
                "sub": 10.0,
                "unique": 10.0
            },
            "issue": {
                "root": 1.0,
                "sub": 1.0,
                "unique": 1.0
            }
        }
    },
    "mbc-testnet": {
        "id": "02",
        "genesis": {
            "hash": "286ad56902839035c4736f0257e027e9b3f3cd9a157357fb0d981542473ad80f",
            "height": 123
        },
        "decimals": 4,
        "admin": {
            "rmbc1qk0u42kmvld9ewza7w0tm2ul6cfdywrd0pcx4t6": [123, None]
        },
        "fee": 1000,  # 0.1 MBC in satoshis
        "marker": 1000,  # 0.1 MBC in satoshis
        "protected": ["MBC", "MICROBITCOIN"],
        "cost": {
            "address": "rmbc1quvumlwgq7z2vkfzxkm0m9xx2t6skk3yyf50k5k",
            "create": {
                "root": 10.0,
                "sub": 10.0,
                "unique": 10.0
            },
            "issue": {
                "root": 1.0,
                "sub": 1.0,
                "unique": 1.0
            }
        }
    }
}

def get_chain(name):
    if name not in CHAIN:
        raise ValueError(f"Invalid chain name {name}")

    return CHAIN[name]