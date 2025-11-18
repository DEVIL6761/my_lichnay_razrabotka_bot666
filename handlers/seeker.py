from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func  # ✅
from database import async_session
from models import Job, User
from keyboards import seeker_actions_keyboard

router = Router()

class SearchJobs(StatesGroup):
    query = State()

async def seeker_menu(message: Message):
    keyboard = seeker_actions_keyboard()
    await message.answer("Ты в меню соискателя.", reply_markup=keyboard)

@router.callback_query(F.data == "view_all_jobs")
async def view_all_jobs(callback: CallbackQuery):
    async with async_session() as session:
        jobs = await session.scalars(
            select(Job).where(Job.status == "active")
        )
        jobs = jobs.all()

        if jobs:
            text = "📋 Доступные вакансии:\n\n"
            for job in jobs:
                text += f"📌 **{job.title}**\n"
                text += f"📝 {job.description}\n"
                text += f"📍 {job.location or 'Не указана'}\n"
                text += f"💰 {job.salary or 'Не указана'}\n"
                text += f"🕐 {job.work_time or 'Не указано'}\n"
                text += f"📞 Контакт: {job.contact or 'Не указан'}\n\n"
        else:
            text = "На данный момент нет доступных вакансий."

    await callback.message.edit_text(text)
    await callback.answer()

@router.callback_query(F.data == "search_jobs")
async def prompt_search_query(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите ключевое слово для поиска вакансий (например, 'менеджер'):")
    await state.set_state(SearchJobs.query)
    await callback.answer()

@router.message(SearchJobs.query)
async def search_jobs(message: Message, state: FSMContext):
    query = message.text.strip()
    if not query:
        await message.answer("❌ Пустой запрос. Попробуйте снова.")
        await state.clear()
        return

    async with async_session() as session:
        # Ищем вакансии, где title содержит query (без учёта регистра)
        jobs = await session.scalars(
            select(Job)
            .where(Job.status == "active")
            .where(func.lower(Job.title).contains(func.lower(query)))
        )
        jobs = jobs.all()

        if jobs:
            text = f"🔍 Результаты по запросу **\"{query}\"**:\n\n"
            for job in jobs:
                text += f"📌 **{job.title}**\n"
                text += f"📝 {job.description}\n"
                text += f"📍 {job.location or 'Не указана'}\n"
                text += f"💰 {job.salary or 'Не указана'}\n"
                text += f"🕐 {job.work_time or 'Не указано'}\n"
                text += f"📞 Контакт: {job.contact or 'Не указан'}\n\n"
        else:
            text = f"❌ Ничего не найдено по запросу **\"{query}\"**."

    await message.answer(text)
    await state.clear()

    # Покажем меню снова
    from handlers.seeker import seeker_menu
    await seeker_menu(message)