from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

def start_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Я ищу работу", callback_data="role_seeker")],
        [InlineKeyboardButton(text="Я предлагаю работу", callback_data="role_employer")]
    ])
    return keyboard

def employer_actions_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Создать вакансию", callback_data="create_job")],
        [InlineKeyboardButton(text="Просмотреть мои вакансии", callback_data="view_my_jobs")],
        [InlineKeyboardButton(text="🏠 В начало", callback_data="back_to_start")]  # ✅
    ])
    return keyboard

def seeker_actions_keyboard():
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📋 Показать все вакансии", callback_data="view_all_jobs")],
        [InlineKeyboardButton(text="🔍 Поиск вакансий", callback_data="search_jobs")],
        [InlineKeyboardButton(text="🏠 В начало", callback_data="back_to_start")]  # ✅
    ])
    return keyboard

def job_list_keyboard(jobs):
    keyboard = []
    for job in jobs:
        keyboard.append([
            InlineKeyboardButton(text=f"✏️ Редактировать {job.title}", callback_data=f"edit_job_{job.id}"),
            InlineKeyboardButton(text=f"❌ Удалить {job.title}", callback_data=f"delete_job_{job.id}")
        ])
    keyboard.append([
        InlineKeyboardButton(text="← Назад", callback_data="back_to_menu"),
        InlineKeyboardButton(text="🏠 В начало", callback_data="back_to_start")  # ✅
    ])
    return InlineKeyboardMarkup(inline_keyboard=keyboard)

def edit_job_keyboard(job_id):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📝 Название", callback_data=f"edit_title_{job_id}")],
        [InlineKeyboardButton(text="📋 Описание", callback_data=f"edit_description_{job_id}")],
        [InlineKeyboardButton(text="📍 Локация", callback_data=f"edit_location_{job_id}")],
        [InlineKeyboardButton(text="💰 Зарплата", callback_data=f"edit_salary_{job_id}")],
        [InlineKeyboardButton(text="🕐 Время работы", callback_data=f"edit_work_time_{job_id}")],
        [InlineKeyboardButton(text="📞 Контакт", callback_data=f"edit_contact_{job_id}")],
        [InlineKeyboardButton(text="← Назад", callback_data="view_my_jobs")],
        [InlineKeyboardButton(text="🏠 В начало", callback_data="back_to_start")]  # ✅
    ])
    return keyboard