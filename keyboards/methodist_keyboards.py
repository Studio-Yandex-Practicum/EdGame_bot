from aiogram.types import InlineKeyboardButton, KeyboardButton

from lexicon.lexicon import BUTTONS


# Кнопки при уведомлении о поступивших артефактах
def art_list_keyboard(language: str):
    '''Кнопки при входящем уведомлении методисту.'''
    buttons = BUTTONS[language]
    show_art_list = KeyboardButton(text=buttons["tasks_for_review"])
    lk = KeyboardButton(text=buttons["lk"])

    keyboard = [[show_art_list], [lk]]
    return keyboard


# Кнопки в личном кабинете
def methodist_profile_keyboard(language: str):
    '''Генерирует клавиатуру в ЛК методиста.'''
    buttons = BUTTONS[language]
    add_task = KeyboardButton(text=buttons["add_task"])
    edit_task = KeyboardButton(text=buttons["edit_task"])
    tasks_for_review = KeyboardButton(text=buttons["tasks_for_review"])
    edit_profile = KeyboardButton(text=buttons["edit_profile"])

    keyboard = [
        [add_task, edit_task],
        [tasks_for_review],
        [edit_profile]
    ]
    return keyboard
