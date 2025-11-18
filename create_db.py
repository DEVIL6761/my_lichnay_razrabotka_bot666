import asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.exc import ProgrammingError

# ----- Настройки -----
DB_USER = "postgres"
DB_PASSWORD = "1234567891"  # ← ЗАМЕНИ НА СВОЙ ПАРОЛЬ!
DB_HOST = "localhost"
DB_PORT = "5432"
NEW_DB_NAME = "job_bot_db"

DEFAULT_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/postgres"
TARGET_DB_URL = f"postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{NEW_DB_NAME}"


async def create_database():
    # Подключаемся к стандартной БД 'postgres'
    engine = create_async_engine(DEFAULT_DB_URL)

    async with engine.connect() as conn:
        # Включаем автокоммит для создания БД
        await conn.execution_options(isolation_level="AUTOCOMMIT")

        try:
            # PostgreSQL НЕ поддерживает "IF NOT EXISTS" — просто пробуем создать
            await conn.execute(text(f"CREATE DATABASE {NEW_DB_NAME}"))
            print(f"✅ База данных '{NEW_DB_NAME}' успешно создана!")
        except ProgrammingError as e:
            if "already exists" in str(e):
                print(f"ℹ️ База данных '{NEW_DB_NAME}' уже существует.")
            else:
                print(f"❌ Ошибка при создании БД: {e}")
                raise
        finally:
            await engine.dispose()


async def create_tables():
    engine = create_async_engine(TARGET_DB_URL)

    # Модели (можно вынести в отдельный файл)
    from sqlalchemy import Integer, String, DateTime, ForeignKey
    from sqlalchemy.ext.asyncio import AsyncAttrs
    from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
    from datetime import datetime

    class Base(AsyncAttrs, DeclarativeBase):
        pass

    class User(Base):
        __tablename__ = "users"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        tg_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
        name: Mapped[str] = mapped_column(String)
        role: Mapped[str] = mapped_column(String)
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    class Job(Base):
        __tablename__ = "jobs"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        title: Mapped[str] = mapped_column(String)
        description: Mapped[str] = mapped_column(String)
        employer_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
        status: Mapped[str] = mapped_column(String, default="active")
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        employer = relationship("User")

    class Request(Base):
        __tablename__ = "requests"
        id: Mapped[int] = mapped_column(Integer, primary_key=True)
        job_id: Mapped[int] = mapped_column(Integer, ForeignKey("jobs.id"))
        seeker_id: Mapped[int] = mapped_column(Integer, ForeignKey("users.id"))
        status: Mapped[str] = mapped_column(String, default="pending")
        created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
        seeker = relationship("User", foreign_keys=[seeker_id])
        job = relationship("Job")

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Таблицы созданы: users, jobs, requests")

    await engine.dispose()


async def main():
    await create_database()
    await create_tables()


if __name__ == "__main__":
    asyncio.run(main())