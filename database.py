from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from models import Base, User  # ✅ добавь User
from config import settings

print(f"DEBUG: database imported Base = {Base}")
print(f"DEBUG: database imported User = {User}")

DATABASE_URL = settings.db_url
print(f"DEBUG: database.DATABASE_URL = {DATABASE_URL}")

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)