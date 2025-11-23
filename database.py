# database.py
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import Base
from config import settings

# Получаем URL из настроек
DATABASE_URL = settings.db_url

# ✅ Заменяем схему, если нужно
if DATABASE_URL and DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"DEBUG: database.DATABASE_URL = {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)