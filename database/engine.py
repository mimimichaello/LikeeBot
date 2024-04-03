import os
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from database.models import BaseSubscribe


username = os.getenv("DB_USERNAME")
password = os.getenv("DB_PASSWORD")
host = os.getenv("DB_HOST")
dbname = os.getenv("DB_NAME")


#engine = create_async_engine(os.getenv("DB_URL"), echo=True)
engine = create_async_engine(f"postgresql+asyncpg://{username}:{password}@{host}/{dbname}", echo=True)

session_maker = async_sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseSubscribe.metadata.create_all)


async def drop_db():
    async with engine.begin() as conn:
        await conn.run_sync(BaseSubscribe.metadata.drop_all)
