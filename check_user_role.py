import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import select
from models import User, Job

DATABASE_URL = "postgresql+asyncpg://postgres:1234567891@localhost:5432/job_bot_db"

engine = create_async_engine(DATABASE_URL)
async_session = async_sessionmaker(engine, expire_on_commit=False)

async def check_user_and_jobs():
    async with async_session() as session:
        # Проверим пользователя
        user_result = await session.scalars(select(User).where(User.tg_id == 1074751733))
        user = user_result.first()
        if user:
            print(f"✅ Пользователь найден: id = {user.id}, tg_id = {user.tg_id}, role = {user.role}")
        else:
            print("❌ Пользователь не найден.")
            return

        # Проверим вакансии этого пользователя
        jobs_result = await session.scalars(select(Job).where(Job.employer_id == user.id))
        jobs = jobs_result.all()
        if jobs:
            print("✅ Вакансии пользователя:")
            for job in jobs:
                print(f"  - ID: {job.id}, Название: {job.title}, employer_id: {job.employer_id}")
        else:
            print("❌ У пользователя нет вакансий.")

if __name__ == "__main__":
    asyncio.run(check_user_and_jobs())