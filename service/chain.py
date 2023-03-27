CHAIN = {
    "mbc-mainnet": {
        "id": "01",
        "genesis": {
            "hash": "d7f7df92b379ce61a57a067f5597839d390798464f0c126f4e25c55087428136",
            "height": 1807100
        },
        "decimals": 4,
        "admin": {
            "mbc1q3tv8yfalfkrxdhez8ksuwqar25wv5skuwuh32n": [1806960, None]
        },
        "fee": 1000,  # 0.1 MBC in satoshis
        "marker": 1000,  # 0.1 MBC in satoshis,
        "protected": ["MBC", "MICROBITCOIN"],
        "cost": {
            "address": "Bm47QN43BYKhSLDuiN8TLYMx2NcnmUWjWz",
            "create": {
                "root": 1,
                "sub": 615,
                "unique": 10
            },
            "issue": {
                "root": 51800,
                "sub": 615
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
            "rmbc1qwuw7s4fsj38qhmqz2l08at429ysnq80cz3e4pd": [123, None]
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