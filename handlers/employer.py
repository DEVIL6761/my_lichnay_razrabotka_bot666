from aiogram import Router, F
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from database import async_session
from models import Job, Request, User
from keyboards import employer_actions_keyboard, job_list_keyboard, edit_job_keyboard
from moderation import contains_forbidden_content
from aiogram import Bot
from config import settings
from keyboards import skip_contact_keyboard

router = Router()


class CreateJob(StatesGroup):
    title = State()
    description = State()
    location = State()
    salary = State()
    work_time = State()
    contact = State()


class EditJob(StatesGroup):
    title = State()
    description = State()
    location = State()
    salary = State()
    work_time = State()
    contact = State()


@router.callback_query(F.data == "create_job")
async def show_example_and_prompt_title(callback: CallbackQuery, state: FSMContext):
    example_text = (
        "📌 Пример оформления вакансии в Беларуси:\n\n"
        "📝 Название: *Менеджер по продажам*\n"
        "📋 Описание: *Требуется менеджер по продажам. Опыт от 1 года, знание 1С, "
        "ответственность, коммуникабельность. Работа в команде, выполнение плана продаж, "
        "поиск клиентов. График 5/2, зарплата от 1500 до 2500 Br.*\n"
        "📍 Локация: *Минск, ул. Независимости, д. 10*\n"
        "💰 Зарплата: *от 1500 до 2500 бел. руб.*\n"
        "🕐 Время работы: *с 9:00 до 18:00, 5/2*\n"
        "📞 Контакт: *+375 (29) 123-45-67* или *@username*\n\n"
        "Введите название вакансии:"
    )
    await callback.message.answer(example_text)
    await state.set_state(CreateJob.title)
    await callback.answer()


@router.message(CreateJob.title)
async def get_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Введите описание вакансии.")
    await state.set_state(CreateJob.description)


@router.message(CreateJob.description)
async def get_description(message: Message, state: FSMContext):
    await state.update_data(description=message.text)
    await message.answer("Введите локацию работы (адрес).")
    await state.set_state(CreateJob.location)


@router.message(CreateJob.location)
async def get_location(message: Message, state: FSMContext):
    await state.update_data(location=message.text)
    await message.answer("Введите зарплату (например: от 1500 до 2500 бел. руб.).")
    await state.set_state(CreateJob.salary)


@router.message(CreateJob.salary)
async def get_salary(message: Message, state: FSMContext):
    await state.update_data(salary=message.text)
    await message.answer("Введите время работы (например: с 9:00 до 18:00, 5/2).")
    await state.set_state(CreateJob.work_time)


@router.message(CreateJob.work_time)
@router.message(CreateJob.work_time)
async def get_work_time(message: Message, state: FSMContext):
    await state.update_data(work_time=message.text)
    # ✅ Сохраняем tg_id из message.from_user
    await state.update_data(user_tg_id=message.from_user.id)
    await message.answer(
        "Введите контакт (ID Telegram или номер телефона).\n\n"
        "Если не хотите указывать — нажмите кнопку ниже.",
        reply_markup=skip_contact_keyboard()
    )
    await state.set_state(CreateJob.contact)


@router.message(CreateJob.contact)
async def create_job_from_message(message: Message, state: FSMContext):
    contact_input = message.text.strip() if message.text else ""
    if not contact_input:
        contact_input = "Не указан"
    await state.update_data(contact=contact_input)
    await create_job(message, state)

async def create_job(message: Message, state: FSMContext):
    # ✅ Берём tg_id из FSM
    data = await state.get_data()
    tg_id = data.get("user_tg_id")

    if not tg_id:
        await message.answer("❌ Ошибка: не удалось получить ID пользователя.")
        await state.clear()
        return

    contact_input = data.get('contact', 'Не указан')

    fields_to_check = [
        data.get('title', ''),
        data.get('description', ''),
        data.get('location', ''),
        data.get('salary', ''),
        data.get('work_time', ''),
        contact_input
    ]

    for field in fields_to_check:
        if contains_forbidden_content(field):
            await message.answer(
                "❌ Вакансия не может быть создана.\n"
                "Обнаружено запрещённое содержание (наркотики, мошенничество, незаконная деятельность и т.д.).\n"
                "Пожалуйста, соблюдайте правила публикации."
            )
            await state.clear()
            return

    async with async_session() as session:
        user_result = await session.scalars(select(User).where(User.tg_id == tg_id))
        user = user_result.first()
        if not user:
            await message.answer("❌ Ошибка: пользователь не найден.")
            await state.clear()
            return

        job = Job(
            title=data['title'],
            description=data['description'],
            location=data['location'],
            salary=data['salary'],
            work_time=data['work_time'],
            contact=contact_input,
            employer_id=user.id
        )
        session.add(job)
        await session.commit()

    # ✅ Отправляем вакансию в канал
    channel_id = "@podrabotka_rabota_minsk"  # Замени на ID или username канала
    bot = Bot(token=settings.bot_token)

    # ✅ Получаем информацию о пользователе из БД (или из Telegram, если нужно)
    telegram_user = await bot.get_chat(tg_id)
    first_name = telegram_user.first_name
    last_name = telegram_user.last_name
    full_name = f"{first_name} {last_name}" if last_name else first_name

    user_link = f'<a href="tg://user?id={tg_id}">{full_name}</a>'

    contact_line = f"📞 Контакт: {job.contact}\n" if job.contact and job.contact != "Не указан" else ""

    job_text = (
        f"💼 {job.title}\n\n"
        f"📝 {job.description}\n"
        f"📍 {job.location or 'Не указано'}\n"
        f"💰 {job.salary or 'Не указана'}\n"
        f"🕐 {job.work_time or 'Не указано'}\n"
        f"{contact_line}"
        f"\n"
        f"От: {user_link}"
    )

    try:
        await bot.send_message(chat_id=channel_id, text=job_text, parse_mode="HTML")
    except Exception as e:
        print(f"❌ Ошибка при отправке в канал: {e}")

    await message.answer("✅ Вакансия создана и опубликована в канале!")
    await state.clear()

    from handlers.employer import employer_menu
    await employer_menu(message)


async def employer_menu(message: Message):
    keyboard = employer_actions_keyboard()
    await message.answer("Ты в меню работодателя.", reply_markup=keyboard)


@router.callback_query(F.data == "view_my_jobs")
async def view_my_jobs(callback: CallbackQuery):
    tg_id = callback.from_user.id

    async with async_session() as session:
        user_result = await session.scalars(select(User).where(User.tg_id == tg_id))
        user = user_result.first()
        if not user:
            await callback.message.answer("❌ Ошибка: пользователь не найден.")
            await callback.answer()
            return

        jobs = await session.scalars(select(Job).where(Job.employer_id == user.id))
        jobs = jobs.all()

        if jobs:
            text = "Твои вакансии:\n\n"
            for job in jobs:
                text += f"📌 Название: {job.title}\n"
                text += f"📋 Описание: {job.description}\n"
                text += f"📍 Локация: {job.location or 'Не указана'}\n"
                text += f"💰 Зарплата: {job.salary or 'Не указана'}\n"
                text += f"🕐 Время работы: {job.work_time or 'Не указано'}\n"
                text += f"📞 Контакт: {job.contact or 'Не указан'}\n"
                text += f"📅 Дата создания: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"

            keyboard = job_list_keyboard(jobs)
        else:
            text = "У тебя нет вакансий."
            keyboard = employer_actions_keyboard()

    await callback.message.edit_text(text) if callback.message.text else await callback.message.answer(text)
    await callback.message.edit_reply_markup(reply_markup=keyboard)
    await callback.answer()


@router.callback_query(F.data.startswith("edit_job_"))
async def start_edit_job(callback: CallbackQuery, state: FSMContext):
    job_id = int(callback.data.split("_")[2])
    tg_id = callback.from_user.id

    async with async_session() as session:
        user_result = await session.scalars(select(User).where(User.tg_id == tg_id))
        user = user_result.first()
        if not user:
            await callback.message.answer("❌ Ошибка: пользователь не найден.")
            await callback.answer()
            return

        job = await session.get(Job, job_id)
        if not job or job.employer_id != user.id:
            await callback.message.answer("❌ Невозможно редактировать: вакансия не найдена или не принадлежит тебе.")
            await callback.answer()
            return

        await callback.message.answer("Выбери, что хочешь изменить:", reply_markup=edit_job_keyboard(job_id))
        await state.update_data(job_id=job.id)
        await callback.answer()


@router.callback_query(F.data.startswith("edit_"))
async def prompt_edit_field(callback: CallbackQuery, state: FSMContext):
    data = callback.data.split("_")
    field = data[1]
    job_id = int(data[2])

    field_names = {
        "title": "название",
        "description": "описание",
        "location": "локацию",
        "salary": "зарплату",
        "work_time": "время работы",
        "contact": "контакт"
    }

    await state.update_data(field_to_edit=field, job_id=job_id)
    await callback.message.answer(f"Введите новое {field_names[field]}:")

    if field == "title":
        await state.set_state(EditJob.title)
    elif field == "description":
        await state.set_state(EditJob.description)
    elif field == "location":
        await state.set_state(EditJob.location)
    elif field == "salary":
        await state.set_state(EditJob.salary)
    elif field == "work_time":
        await state.set_state(EditJob.work_time)
    elif field == "contact":
        await state.set_state(EditJob.contact)

    await callback.answer()


@router.message(EditJob.title)
async def edit_title(message: Message, state: FSMContext):
    data = await state.get_data()
    job_id = data['job_id']
    async with async_session() as session:
        job = await session.get(Job, job_id)
        job.title = message.text
        await session.commit()
    await message.answer("✅ Название обновлено.")
    await state.clear()


@router.message(EditJob.description)
async def edit_description(message: Message, state: FSMContext):
    data = await state.get_data()
    job_id = data['job_id']
    async with async_session() as session:
        job = await session.get(Job, job_id)
        job.description = message.text
        await session.commit()
    await message.answer("✅ Описание обновлено.")
    await state.clear()


@router.message(EditJob.location)
async def edit_location(message: Message, state: FSMContext):
    data = await state.get_data()
    job_id = data['job_id']
    async with async_session() as session:
        job = await session.get(Job, job_id)
        job.location = message.text
        await session.commit()
    await message.answer("✅ Локация обновлена.")
    await state.clear()


@router.message(EditJob.salary)
async def edit_salary(message: Message, state: FSMContext):
    data = await state.get_data()
    job_id = data['job_id']
    async with async_session() as session:
        job = await session.get(Job, job_id)
        job.salary = message.text
        await session.commit()
    await message.answer("✅ Зарплата обновлена.")
    await state.clear()


@router.message(EditJob.work_time)
async def edit_work_time(message: Message, state: FSMContext):
    data = await state.get_data()
    job_id = data['job_id']
    async with async_session() as session:
        job = await session.get(Job, job_id)
        job.work_time = message.text
        await session.commit()
    await message.answer("✅ Время работы обновлено.")
    await state.clear()


@router.message(EditJob.contact)
async def edit_contact(message: Message, state: FSMContext):
    data = await state.get_data()
    job_id = data['job_id']
    async with async_session() as session:
        job = await session.get(Job, job_id)
        job.contact = message.text
        await session.commit()
    await message.answer("✅ Контакт обновлён.")
    await state.clear()


@router.callback_query(F.data.startswith("delete_job_"))
async def delete_job(callback: CallbackQuery):
    job_id = int(callback.data.split("_")[2])
    tg_id = callback.from_user.id

    async with async_session() as session:
        user_result = await session.scalars(select(User).where(User.tg_id == tg_id))
        user = user_result.first()
        if not user:
            await callback.message.answer("❌ Ошибка: пользователь не найден.")
            await callback.answer()
            return

        job = await session.get(Job, job_id)
        if not job or job.employer_id != user.id:
            await callback.message.answer("❌ Невозможно удалить: вакансия не найдена или не принадлежит тебе.")
            await callback.answer()
            return

        await session.delete(job)
        await session.commit()

    await callback.message.answer("✅ Вакансия удалена.")
    await callback.answer()

    # Показать обновлённый список вакансий
    from handlers.employer import view_my_jobs
    await view_my_jobs(callback)


@router.callback_query(F.data == "back_to_menu")
async def back_to_menu(callback: CallbackQuery):
    await employer_menu(callback.message)
    await callback.answer()

@router.callback_query(F.data == "skip_contact")
async def skip_contact(callback: CallbackQuery, state: FSMContext):
    # ✅ Правильно берём tg_id из callback.from_user
    tg_id = callback.from_user.id
    await state.update_data(contact="Не указан", user_tg_id=tg_id)
    await create_job(callback.message, state)
    await callback.answer()


__all__ = ["router"]