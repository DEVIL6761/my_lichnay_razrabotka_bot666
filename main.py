from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from config import settings
from handlers import start, employer, seeker
from database import init_db
import asyncio

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Начать сначала")
    ]
    await bot.set_my_commands(commands)

async def main():
    await init_db()

    bot = Bot(token=settings.bot_token)
    dp = Dispatcher()

    # Устанавливаем команду /start
    await set_commands(bot)

    dp.include_router(start.router)
    dp.include_router(employer.router)
    dp.include_router(seeker.router)

    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())