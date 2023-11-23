from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


# Создание клавиатуры для ЛК вожатого
def create_profile_keyboard():
    profile_keyboard = [
        [KeyboardButton(text="Список детей")],
        [KeyboardButton(text="Список детей в группе")],
        [KeyboardButton(text="Проверить задания")],
        [KeyboardButton(text="Проверить конкретное задание")],
        [KeyboardButton(text="Узнать общий прогресс отряда")],
        [KeyboardButton(text="Получить информацию о ребенке")],
        [KeyboardButton(text="Проверить задание конкретного ребенка")],
        [KeyboardButton(text="Проверить задание всего отряда")],
    ]
    return ReplyKeyboardMarkup(keyboard=profile_keyboard, resize_keyboard=True)


# Создание инлайн клавиатуры для проверки задания вожатым
def create_inline_keyboard(task_id, name):
    accept_button = InlineKeyboardButton(
        text="✔️ Принять", callback_data=f"accept:{task_id}:{name}"
    )

    reject_button = InlineKeyboardButton(
        text="❌ Отклонить", callback_data=f"reject:{task_id}:{name}"
    )
    send_back_button = InlineKeyboardButton(
        text="🔄 Отправить на доп.проверку",
        callback_data=f"back:{task_id}:{name}",
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[[accept_button], [reject_button], [send_back_button]]
    )


# Создание инлайн клавиатуры для добавления комментария при отколении вожатым
# дз
def create_yes_no_keyboard(task_id):
    yes_button = InlineKeyboardButton(
        text="Да", callback_data=f"yes:{task_id}"
    )
    no_button = InlineKeyboardButton(text="Нет", callback_data=f"no:{task_id}")
    return InlineKeyboardMarkup(inline_keyboard=[[yes_button], [no_button]])
