from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import CommandStart
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import async_session
from models import User
from keyboards import start_keyboard

router = Router()

@router.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer("Привет! Выбери, что ты хочешь сделать:", reply_markup=start_keyboard())

@router.callback_query(F.data.startswith("role_"))
async def set_role(callback: CallbackQuery):
    role = callback.data.split("_")[1]
    tg_id = callback.from_user.id

    async with async_session() as session:
        result = await session.scalars(select(User).where(User.tg_id == tg_id))
        user = result.first()
        if not user:
            new_user = User(tg_id=tg_id, name=callback.from_user.full_name, role=role)
            session.add(new_user)
            await session.commit()
        else:
            user.role = role
            await session.commit()

    if role == "employer":
        await callback.message.edit_text("Ты выбрал: я предлагаю работу.")
        from handlers.employer import employer_menu
        await employer_menu(callback.message)
    elif role == "seeker":
        await callback.message.edit_text("Ты выбрал: я ищу работу.")
        from handlers.seeker import seeker_menu
        await seeker_menu(callback.message)

    await callback.answer()

# ✅ Новая функция для кнопки "🏠 В начало"
@router.callback_query(F.data == "back_to_start")
async def back_to_start(callback: CallbackQuery):
    await callback.message.answer("Привет! Выбери, что ты хочешь сделать:", reply_markup=start_keyboard())
    await callback.answer()

__all__ = ["router"]