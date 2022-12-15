from service.models import Settings, Address, Balance, Token, Transfer
from service.protocol import Protocol
from service import constants
from tortoise import Tortoise
from service import utils
import config

blockchain = [
# Create token
{
    "data": "85a16301a161cb40c3880000000000a16eaa5465737420746f6b656ea174a454455354a172c3",
    "from": config.admin_address
},
# Random bytes
{
    "data": "c394d23897ab51a6f0fe3c502cf2c92b5c42156e0d",
    "from": "sometestaddress2",
    "to": "sometestaddress3"
},
# Mint tokens
{
    "data": "83a16302a161cb407f400000000000a174a454455354",
    "from": config.admin_address
},
# Send tokens
{
    "data": "83a16303a161cb40250f5c28f5c28fa174a454455354",
    "from": config.admin_address,
    "to": "sometestaddress1",
    "txid": "0x2212fa1fbcec3de942c0ccb01e6e34ea8bdbcdfd769ae4056b52b643af8b658c"
},
# Random bytes
{
    "data": "cf1618bf4a2956b3596a336a500d22fcbc36b9f60caea9ad93307355c92ad0fad93fee4373e62a920c103e73b8047b67b07715f0",
    "from": "sometestaddress2",
    "to": "sometestaddress3"
},
# Ban address
{
    "data": "81a16304",
    "from": config.admin_address,
    "to": "sometestaddress4"
},
# Send to banned address
{
    "data": "83a16303a161cb404b0e353f7ced91a174a454455354",
    "from": config.admin_address,
    "to": "sometestaddress4",
    "txid": "0x2212fa1fbcec123452c0ccb01e6e34ea8bdbcdfd769ae4056b52b643af8b658c"
},
# Random bytes
{
    "data": "a3fd76acd41dfbbce84a60f6d0ac38eac38a013e4b5d4cef719b",
    "from": "sometestaddress2",
    "to": "sometestaddress3"
},
# Unban address
{
    "data": "81a16305",
    "from": config.admin_address,
    "to": "sometestaddress4"
},
# Send to unbanned address
{
    "data": "83a16303a161cb404b0e353f7ced91a174a454455354",
    "from": config.admin_address,
    "to": "sometestaddress4",
    "txid": "0x2212fa1fbcec123452c0ccb01e6e34ea8bdbcdfd769ae4056b52b643af8b658c"
}
]

async def parse_blockchain():
    await Tortoise.init(**config.tortoise)
    await Tortoise.generate_schemas()

    settings = await Settings.first()

    if settings.current_height < len(blockchain):
        block = blockchain[settings.current_height]
        # Todo: Loop through outputs
        for _ in range(1):
            raw_data = block["data"]
            data = Protocol.decode(raw_data)
            print(data)

            if not data:
                continue

            category = data["category"]

            if category == constants.CREATE:
                # Only admin user can create a token
                if block["from"] != config.admin_address:
                    continue

                # Avoid negative amounts
                if data["amount"] <= 0:
                    continue

                # Avoid name duplicates
                if (await Token.filter(name=data["name"]).first()):
                    continue

                # Avoid ticker duplicates
                if (await Token.filter(ticker=data["ticker"]).first()):
                    continue

                token = await Token.create(**{
                    "name": data["name"],
                    "ticker": data["ticker"],
                    "supply": data["amount"],
                    "reissuable": data["reissuable"]
                })

                address = await Address.filter(raw_address=config.admin_address).first()

                # Create a balance for that token for the admin address
                balance = await Balance.create(**{
                    "amount": data["amount"],
                    "address": address,
                    "token": token
                })

            elif category == constants.ISSUE:
                # Only admin user can issue a token
                if block["from"] != config.admin_address:
                    continue

                # Avoid negative amounts
                if data["amount"] <= 0:
                    continue

                # Check if token exists
                if not (token := await Token.filter(ticker=data["ticker"]).first()):
                    continue

                if not token.reissuable:
                    continue

                address = await Address.filter(
                    raw_address=config.admin_address
                ).prefetch_related("balances").first()

                balance = await address.balances.filter(
                    token=token
                ).first()

                balance.amount += utils.float_to_Decimal(data["amount"])
                token.supply += utils.float_to_Decimal(data["amount"])

                await balance.save()
                await token.save()

            elif category == constants.TRANSFER:
                # Avoid negative amounts
                if data["amount"] <= 0:
                    continue

                # Check if token exists
                if not (token := await Token.filter(ticker=data["ticker"]).first()):
                    continue

                # Check if sender address exists
                if not (sender := await Address.filter(
                    raw_address=block["from"]
                ).prefetch_related("balances").first()):
                    continue

                # Create receiver address if doesn't exist
                if not (receiver := await Address.filter(
                    raw_address=block["to"]
                ).prefetch_related("balances").first()):
                    receiver = await Address.create(**{
                        "raw_address": block["to"],
                        "nonce": 0
                    })

                # Check if sender balance exists
                if not (sender_balance := await sender.balances.filter(
                    token=token
                ).first()):
                    continue

                # Create receiver balance if doesn't exist
                if not (receiver_balance := await receiver.balances.filter(
                    token=token
                ).first()):
                    receiver_balance = await Balance.create(**{
                        "amount": 0,
                        "address": receiver,
                        "token": token
                    })

                # Check the balance
                if sender_balance.amount - utils.float_to_Decimal(data["amount"]) < 0:
                    continue

                # Check if banned
                if sender.banned or receiver.banned:
                    continue

                sender_balance.amount -= utils.float_to_Decimal(data["amount"])
                receiver_balance.amount += utils.float_to_Decimal(data["amount"])

                sender.nonce += 1
                receiver.nonce += 1

                transfer = await Transfer.create(**{
                    "amount": utils.float_to_Decimal(data["amount"]),
                    "txid": block["txid"],
                    "token": token,
                    "sender": sender,
                    "receiver": receiver
                })

                await sender.save()
                await sender_balance.save()

                await receiver.save()
                await receiver_balance.save()

            elif category == constants.BAN:
                # Check if the address exists
                if not (address := await Address.filter(
                    raw_address=block["to"]
                ).first()):
                    address = await Address.create(**{
                        "raw_address": block["to"],
                        "nonce": 0
                    })

                address.banned = True

                await address.save()

            elif category == constants.UNBAN:
                # Check if the address exists
                if not (address := await Address.filter(
                    raw_address=block["to"]
                ).first()):
                    address = await Address.create(**{
                        "raw_address": block["to"],
                        "nonce": 0
                    })

                address.banned = False

                await address.save()

    settings.current_height += 1

    await settings.save()
    await Tortoise.close_connections()
