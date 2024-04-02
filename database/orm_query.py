from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Subscribe


async def orm_add_subscribe(session: AsyncSession, data: dict):
    obj = Subscribe(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]),
    )
    session.add(obj)
    await session.commit()


async def orm_get_subscriptions(session: AsyncSession):
    query = select(Subscribe)
    result = await session.execute(query)
    return result.scalars().all()


async def orm_get_subscribe(session: AsyncSession, subscribe_id: int):
    query = select(Subscribe).where(Subscribe.id == subscribe_id)
    result = await session.execute(query)
    return result.scalar()


async def orm_update_subscribe(session: AsyncSession, subscribe_id: int, data):
    query = update(Subscribe).where(Subscribe.id == subscribe_id).values(
        name=data["name"],
        description=data["description"],
        price=float(data["price"]))
    await session.execute(query)
    await session.commit()


async def orm_delete_subscribe(session: AsyncSession, subscribe_id: int):
    query = delete(Subscribe).where(Subscribe.id == subscribe_id)
    await session.execute(query)
    await session.commit()
