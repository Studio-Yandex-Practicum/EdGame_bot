from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

from lexicon.lexicon import BUTTONS


# Создание клавиатуры для ЛК вожатого
def create_profile_keyboard(language: str):
    buttons = BUTTONS[language]
    profile_keyboard = [
        [KeyboardButton(text=buttons["list_children"])],
        [KeyboardButton(text=buttons["list_children_in_group"])],
        [KeyboardButton(text=buttons["tasks_for_review"])],
        [KeyboardButton(text=buttons["check_specific_task"])],
        [KeyboardButton(text=buttons["squad_progress"])],
        [KeyboardButton(text=buttons["child_information"])],
        [KeyboardButton(text=buttons["check_task_specific_child"])],
        [KeyboardButton(text=buttons["check_tasks_squad"])],
    ]
    return ReplyKeyboardMarkup(keyboard=profile_keyboard, resize_keyboard=True)


# Создание инлайн клавиатуры для проверки задания вожатым
def create_inline_keyboard(task_id: int, name: str, language: str):
    buttons = BUTTONS[language]
    accept_button = InlineKeyboardButton(
        text=f"✔️ {buttons['approve']}",
        callback_data=f"accept:{task_id}:{name}"
    )

    reject_button = InlineKeyboardButton(
        text=f"❌ {buttons['reject']}",
        callback_data=f"reject:{task_id}:{name}"
    )
    send_back_button = InlineKeyboardButton(
        text=f"🔄 {buttons['send_additional_verification']}",
        callback_data=f"back:{task_id}:{name}",
    )
    return InlineKeyboardMarkup(
        inline_keyboard=[[accept_button], [reject_button], [send_back_button]]
    )


# Создание инлайн клавиатуры для добавления комментария при отколении вожатым
# дз
def create_yes_no_keyboard(task_id: int, language: str):
    buttons = BUTTONS[language]
    yes_button = InlineKeyboardButton(
        text=buttons["yes"], callback_data=f"yes:{task_id}"
    )
    no_button = InlineKeyboardButton(
        text=buttons["no"], callback_data=f"no:{task_id}"
    )
    return InlineKeyboardMarkup(inline_keyboard=[[yes_button], [no_button]])
