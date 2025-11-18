import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import User, Base

DATABASE_URL = "postgresql+asyncpg://postgres:1234567891@localhost:5432/job_bot_db"

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def show_users():
    async with async_session() as session:
        users = await session.scalars(select(User))
        for u in users:
            print(f"ID: {u.id}, tg_id: {u.tg_id}, name: {u.name}, role: {u.role}")

from sqlalchemy import select
asyncio.run(show_users())