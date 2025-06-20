from app.utils import log_message, get_settings, amount
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import TokenCost, Address
from app.chain import get_chain
from sqlalchemy import select


async def process_cost(session: AsyncSession, decoded, inputs, block):
    settings = get_settings()
    chain = get_chain(settings.general.chain)

    send_address_label = list(inputs)[0]

    send_address = await session.scalar(
        select(Address).filter(Address.label == send_address_label)
    )

    value = amount(decoded["value"], chain["decimals"])

    session.add(
        TokenCost(
            **{
                "action": decoded["action"],
                "type": decoded["type"],
                "height": block.height,
                "admin": send_address,
                "value": value,
                "block": block,
            }
        )
    )

    admin = send_address_label
    token_type = decoded["type"]

    log_message(f"Fee cost for {token_type} updated to {value} by {admin}")

    await session.commit()
